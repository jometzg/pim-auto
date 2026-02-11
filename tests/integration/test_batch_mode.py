"""Integration tests for batch mode."""

import os
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
def mock_env(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
    monkeypatch.setenv("LOG_ANALYTICS_WORKSPACE_ID", "test-workspace-id")


@pytest.fixture
def sample_data():
    """Create sample test data."""
    activations = [
        PIMActivation(
            user_email="user1@example.com",
            role_name="Contributor",
            activation_reason="Add storage account",
            activation_time=datetime(2026, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
            duration_hours=24,
        ),
        PIMActivation(
            user_email="user2@example.com",
            role_name="Owner",
            activation_reason="Fix network issue",
            activation_time=datetime(2026, 2, 11, 12, 0, 0, tzinfo=timezone.utc),
            duration_hours=24,
        ),
    ]

    activities_by_user = {
        "user1@example.com": [
            ActivityEvent(
                timestamp=datetime(2026, 2, 11, 10, 30, 0, tzinfo=timezone.utc),
                operation_name="Create Storage Account",
                resource_name="storage123",
                resource_type="Microsoft.Storage/storageAccounts",
                status="Success",
                resource_group="rg-prod",
                subscription_id="sub-123",
            )
        ],
        "user2@example.com": [
            ActivityEvent(
                timestamp=datetime(2026, 2, 11, 12, 15, 0, tzinfo=timezone.utc),
                operation_name="Update NSG Rule",
                resource_name="nsg-prod",
                resource_type="Microsoft.Network/networkSecurityGroups",
                status="Success",
                resource_group="rg-prod",
                subscription_id="sub-123",
            )
        ],
    }

    assessments_by_user = {
        "user1@example.com": RiskAssessment(
            level=AlignmentLevel.ALIGNED,
            explanation="User created storage account as stated.",
        ),
        "user2@example.com": RiskAssessment(
            level=AlignmentLevel.NOT_ALIGNED,
            explanation="User modified NSG but stated network issue fix.",
        ),
    }

    return activations, activities_by_user, assessments_by_user


def test_batch_mode_end_to_end(mock_env, sample_data, tmp_path):
    """Test batch mode end-to-end workflow."""
    activations, activities_by_user, assessments_by_user = sample_data
    output_file = tmp_path / "report.md"

    # Mock Azure clients
    mock_log_analytics = Mock()
    mock_openai_client = Mock()

    # Create config
    config = Config.from_environment()

    # Create batch runner
    runner = BatchRunner(mock_log_analytics, mock_openai_client, config)

    # Mock the detections
    runner.pim_detector.detect_activations = Mock(return_value=activations)

    # Mock activity correlator
    def mock_get_activities(user_email, start_time, end_time):
        return activities_by_user.get(user_email, [])

    runner.activity_correlator.get_user_activities = Mock(side_effect=mock_get_activities)

    # Mock risk assessor
    assessment_calls = []

    def mock_assess(pim_reason, activities):
        user_email = None
        for email, acts in activities_by_user.items():
            if acts == activities:
                user_email = email
                break
        assessment_calls.append((pim_reason, activities))
        return assessments_by_user.get(
            user_email, RiskAssessment(AlignmentLevel.UNKNOWN, "Unknown")
        )

    runner.risk_assessor.assess_alignment = Mock(side_effect=mock_assess)

    # Run batch mode
    result = runner.run(hours=24, output_path=output_file)

    # Verify success
    assert result == 0

    # Verify file was created
    assert output_file.exists()

    # Verify report content
    content = output_file.read_text(encoding="utf-8")
    assert "# PIM Activity Audit Report" in content
    assert "## Executive Summary" in content
    assert "user1@example.com" in content
    assert "user2@example.com" in content
    assert "Add storage account" in content
    assert "Fix network issue" in content
    assert "ALIGNED" in content or "aligned" in content
    assert "NOT_ALIGNED" in content or "not_aligned" in content


def test_batch_mode_no_activations(mock_env, tmp_path):
    """Test batch mode when no activations are found."""
    output_file = tmp_path / "report.md"

    # Mock Azure clients
    mock_log_analytics = Mock()
    mock_openai_client = Mock()

    # Create config
    config = Config.from_environment()

    # Create batch runner
    runner = BatchRunner(mock_log_analytics, mock_openai_client, config)

    # Mock empty detections
    runner.pim_detector.detect_activations = Mock(return_value=[])

    # Run batch mode
    with patch("builtins.print"):
        result = runner.run(hours=24)

    # Verify success
    assert result == 0


def test_batch_mode_with_failure(mock_env):
    """Test batch mode handles errors gracefully."""
    # Mock Azure clients
    mock_log_analytics = Mock()
    mock_openai_client = Mock()

    # Create config
    config = Config.from_environment()

    # Create batch runner
    runner = BatchRunner(mock_log_analytics, mock_openai_client, config)

    # Mock detection failure
    runner.pim_detector.detect_activations = Mock(side_effect=Exception("API Error"))

    # Run batch mode
    result = runner.run(hours=24)

    # Verify failure
    assert result == 1


def test_batch_mode_stdout_output(mock_env, sample_data):
    """Test batch mode outputs to stdout when no file specified."""
    activations, activities_by_user, assessments_by_user = sample_data

    # Mock Azure clients
    mock_log_analytics = Mock()
    mock_openai_client = Mock()

    # Create config
    config = Config.from_environment()

    # Create batch runner
    runner = BatchRunner(mock_log_analytics, mock_openai_client, config)

    # Mock the detections
    runner.pim_detector.detect_activations = Mock(return_value=activations)
    runner.activity_correlator.get_user_activities = Mock(
        side_effect=lambda user_email, start_time, end_time: activities_by_user.get(user_email, [])
    )
    runner.risk_assessor.assess_alignment = Mock(
        side_effect=lambda pim_reason, activities: RiskAssessment(AlignmentLevel.ALIGNED, "Test")
    )

    # Run batch mode and capture stdout
    with patch("builtins.print") as mock_print:
        result = runner.run(hours=24)

    # Verify success
    assert result == 0

    # Verify print was called
    assert mock_print.called
