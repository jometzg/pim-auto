"""Tests for risk assessor module."""

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from src.pim_auto.core.activity_correlator import ActivityEvent
from src.pim_auto.core.risk_assessor import AlignmentLevel, RiskAssessment, RiskAssessor


@pytest.fixture
def mock_openai() -> Mock:
    """Mock OpenAI client."""
    return Mock()


def test_assess_aligned(mock_openai: Mock) -> None:
    """Test aligned assessment."""
    mock_openai.generate_completion.return_value = (
        "ALIGNED: The user created a storage account as stated."
    )

    assessor = RiskAssessor(mock_openai)
    activities = [
        ActivityEvent(
            timestamp=datetime(2026, 2, 10, 10, 30, tzinfo=timezone.utc),
            operation_name="Create Storage Account",
            resource_type="Microsoft.Storage/storageAccounts",
            resource_name="mystorageaccount",
            status="Succeeded",
            resource_group="rg-prod",
            subscription_id="sub-123",
        )
    ]

    assessment = assessor.assess_alignment(
        pim_reason="need to add a storage account", activities=activities
    )

    assert assessment.level == AlignmentLevel.ALIGNED
    assert "ALIGNED" in assessment.explanation


def test_assess_not_aligned(mock_openai: Mock) -> None:
    """Test not aligned assessment."""
    mock_openai.generate_completion.return_value = (
        "NOT_ALIGNED: Activities don't match the stated reason."
    )

    assessor = RiskAssessor(mock_openai)
    activities = [
        ActivityEvent(
            timestamp=datetime(2026, 2, 10, 10, 30, tzinfo=timezone.utc),
            operation_name="Delete Virtual Machine",
            resource_type="Microsoft.Compute/virtualMachines",
            resource_name="prod-vm-01",
            status="Succeeded",
            resource_group="rg-prod",
            subscription_id="sub-123",
        )
    ]

    assessment = assessor.assess_alignment(
        pim_reason="need to add a storage account", activities=activities
    )

    assert assessment.level == AlignmentLevel.NOT_ALIGNED


def test_assess_partially_aligned(mock_openai: Mock) -> None:
    """Test partially aligned assessment."""
    mock_openai.generate_completion.return_value = (
        "PARTIALLY_ALIGNED: Some activities match the reason."
    )

    assessor = RiskAssessor(mock_openai)
    activities = [
        ActivityEvent(
            timestamp=datetime(2026, 2, 10, 10, 30, tzinfo=timezone.utc),
            operation_name="Create Storage Account",
            resource_type="Microsoft.Storage/storageAccounts",
            resource_name="mystorageaccount",
            status="Succeeded",
            resource_group="rg-prod",
            subscription_id="sub-123",
        )
    ]

    assessment = assessor.assess_alignment(
        pim_reason="need to update networking", activities=activities
    )

    assert assessment.level == AlignmentLevel.PARTIALLY_ALIGNED


def test_assess_unknown(mock_openai: Mock) -> None:
    """Test unknown assessment."""
    mock_openai.generate_completion.return_value = "Unable to determine alignment."

    assessor = RiskAssessor(mock_openai)
    activities = []

    assessment = assessor.assess_alignment(
        pim_reason="vague reason",
        activities=activities,
    )

    assert assessment.level == AlignmentLevel.UNKNOWN


def test_assess_no_activities(mock_openai: Mock) -> None:
    """Test assessment with no activities."""
    mock_openai.generate_completion.return_value = (
        "UNKNOWN: No activities recorded during elevation."
    )

    assessor = RiskAssessor(mock_openai)
    assessment = assessor.assess_alignment(pim_reason="need to troubleshoot issue", activities=[])

    # Should handle empty activity list gracefully
    assert isinstance(assessment, RiskAssessment)


def test_assess_alignment_variations(mock_openai: Mock) -> None:
    """Test different alignment response formats."""
    test_cases = [
        ("NOT ALIGNED (with spaces)", AlignmentLevel.NOT_ALIGNED),
        ("The answer is ALIGNED.", AlignmentLevel.ALIGNED),
        ("PARTIALLY ALIGNED with some concerns", AlignmentLevel.PARTIALLY_ALIGNED),
        ("partially_aligned", AlignmentLevel.PARTIALLY_ALIGNED),
    ]

    assessor = RiskAssessor(mock_openai)

    for response_text, expected_level in test_cases:
        mock_openai.generate_completion.return_value = response_text
        assessment = assessor.assess_alignment("test reason", [])
        assert assessment.level == expected_level


def test_risk_assessment_dataclass() -> None:
    """Test RiskAssessment dataclass."""
    assessment = RiskAssessment(level=AlignmentLevel.ALIGNED, explanation="Test explanation")

    assert assessment.level == AlignmentLevel.ALIGNED
    assert assessment.explanation == "Test explanation"
