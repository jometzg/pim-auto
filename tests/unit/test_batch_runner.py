"""Unit tests for batch runner."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pim_auto.config import Config
from pim_auto.core.activity_correlator import ActivityEvent
from pim_auto.core.pim_detector import PIMActivation
from pim_auto.core.risk_assessor import AlignmentLevel, RiskAssessment
from pim_auto.interfaces.batch_runner import BatchRunner


@pytest.fixture
def mock_log_analytics():
    """Create mock Log Analytics client."""
    return Mock()


@pytest.fixture
def mock_openai_client():
    """Create mock OpenAI client."""
    return Mock()


@pytest.fixture
def mock_config():
    """Create mock config."""
    config = Mock(spec=Config)
    config.default_scan_hours = 24
    config.batch_output_path = None
    return config


@pytest.fixture
def batch_runner(mock_log_analytics, mock_openai_client, mock_config):
    """Create batch runner instance."""
    return BatchRunner(mock_log_analytics, mock_openai_client, mock_config)


@pytest.fixture
def sample_activations():
    """Create sample PIM activations."""
    return [
        PIMActivation(
            user_email="user1@example.com",
            role_name="Contributor",
            activation_reason="Add storage account",
            activation_time=datetime(2026, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
            duration_hours=24,
        )
    ]


@pytest.fixture
def sample_activities():
    """Create sample activity events."""
    return [
        ActivityEvent(
            timestamp=datetime(2026, 2, 11, 10, 30, 0, tzinfo=timezone.utc),
            operation_name="Create Storage Account",
            resource_name="storage123",
            resource_type="Microsoft.Storage/storageAccounts",
            status="Success",
            resource_group="rg-prod",
            subscription_id="sub-123",
        )
    ]


@pytest.fixture
def sample_assessment():
    """Create sample risk assessment."""
    return RiskAssessment(
        level=AlignmentLevel.ALIGNED,
        explanation="User created storage account as stated.",
    )


def test_batch_runner_initialization(
    batch_runner, mock_log_analytics, mock_openai_client, mock_config
):
    """Test batch runner initialization."""
    assert batch_runner.log_analytics == mock_log_analytics
    assert batch_runner.openai_client == mock_openai_client
    assert batch_runner.config == mock_config
    assert batch_runner.pim_detector is not None
    assert batch_runner.activity_correlator is not None
    assert batch_runner.risk_assessor is not None
    assert batch_runner.markdown_generator is not None


def test_run_with_activations(
    batch_runner, sample_activations, sample_activities, sample_assessment
):
    """Test running batch mode with activations."""
    # Mock the dependencies
    batch_runner.pim_detector.detect_activations = Mock(return_value=sample_activations)
    batch_runner.activity_correlator.get_user_activities = Mock(return_value=sample_activities)
    batch_runner.risk_assessor.assess_alignment = Mock(return_value=sample_assessment)
    batch_runner.markdown_generator.generate_report = Mock(return_value="# Report")

    # Run batch mode
    result = batch_runner.run()

    # Verify calls
    batch_runner.pim_detector.detect_activations.assert_called_once_with(hours=24)
    batch_runner.activity_correlator.get_user_activities.assert_called_once()
    batch_runner.risk_assessor.assess_alignment.assert_called_once()
    batch_runner.markdown_generator.generate_report.assert_called_once()

    # Verify success
    assert result == 0


def test_run_without_activations(batch_runner):
    """Test running batch mode with no activations."""
    # Mock empty activations
    batch_runner.pim_detector.detect_activations = Mock(return_value=[])

    # Run batch mode
    with patch("builtins.print") as mock_print:
        result = batch_runner.run()

    # Verify success
    assert result == 0
    # Verify empty report was printed
    mock_print.assert_called()


def test_run_with_custom_hours(batch_runner, sample_activations):
    """Test running with custom hours parameter."""
    batch_runner.pim_detector.detect_activations = Mock(return_value=sample_activations)
    batch_runner.activity_correlator.get_user_activities = Mock(return_value=[])
    batch_runner.risk_assessor.assess_alignment = Mock(
        return_value=RiskAssessment(AlignmentLevel.UNKNOWN, "")
    )
    batch_runner.markdown_generator.generate_report = Mock(return_value="# Report")

    # Run with custom hours
    result = batch_runner.run(hours=48)

    # Verify custom hours used
    batch_runner.pim_detector.detect_activations.assert_called_once_with(hours=48)
    assert result == 0


def test_run_with_output_file(batch_runner, sample_activations, tmp_path):
    """Test running with output file."""
    output_path = tmp_path / "report.md"

    batch_runner.pim_detector.detect_activations = Mock(return_value=sample_activations)
    batch_runner.activity_correlator.get_user_activities = Mock(return_value=[])
    batch_runner.risk_assessor.assess_alignment = Mock(
        return_value=RiskAssessment(AlignmentLevel.UNKNOWN, "")
    )
    batch_runner.markdown_generator.generate_report = Mock(return_value="# Report")

    # Run with output file
    result = batch_runner.run(output_path=output_path)

    # Verify report generation was called with output path
    call_args = batch_runner.markdown_generator.generate_report.call_args
    assert call_args.kwargs["output_path"] == output_path
    assert result == 0


def test_run_with_exception(batch_runner):
    """Test error handling when exception occurs."""
    # Mock exception during detection
    batch_runner.pim_detector.detect_activations = Mock(side_effect=Exception("Test error"))

    # Run batch mode
    result = batch_runner.run()

    # Verify error return code
    assert result == 1


def test_run_continues_on_assessment_failure(batch_runner, sample_activities):
    """Test that batch mode continues even if one assessment fails."""
    activations = [
        PIMActivation(
            user_email="user1@example.com",
            role_name="Contributor",
            activation_reason="Test",
            activation_time=datetime(2026, 2, 11, 10, 0, 0),
            duration_hours=24,
        ),
        PIMActivation(
            user_email="user2@example.com",
            role_name="Owner",
            activation_reason="Test2",
            activation_time=datetime(2026, 2, 11, 11, 0, 0),
            duration_hours=24,
        ),
    ]

    batch_runner.pim_detector.detect_activations = Mock(return_value=activations)
    batch_runner.activity_correlator.get_user_activities = Mock(return_value=sample_activities)

    # First assessment fails, second succeeds
    batch_runner.risk_assessor.assess_alignment = Mock(
        side_effect=[
            Exception("Assessment failed"),
            RiskAssessment(AlignmentLevel.ALIGNED, "Test"),
        ]
    )
    batch_runner.markdown_generator.generate_report = Mock(return_value="# Report")

    # Run batch mode
    result = batch_runner.run()

    # Should still succeed and generate report
    assert result == 0
    batch_runner.markdown_generator.generate_report.assert_called_once()


def test_generate_empty_report(batch_runner):
    """Test generating empty report."""
    report = batch_runner._generate_empty_report()

    assert "# PIM Activity Audit Report" in report
    assert "No PIM activations found" in report


def test_output_report_to_stdout(batch_runner):
    """Test outputting report to stdout."""
    report = "# Test Report"

    with patch("builtins.print") as mock_print:
        batch_runner._output_report(report, None)

    # Verify print was called
    mock_print.assert_called()
    # Check that report content was printed
    calls = [str(call) for call in mock_print.call_args_list]
    report_printed = any("Test Report" in str(call) for call in calls)
    assert report_printed


def test_output_report_to_file(batch_runner):
    """Test outputting report to file (file creation is handled by markdown_generator)."""
    report = "# Test Report"
    output_path = Path("/tmp/test_report.md")

    # Just verify the method completes without error
    # Actual file writing is done in markdown_generator.generate_report
    batch_runner._output_report(report, output_path)
