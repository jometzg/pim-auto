"""Unit tests for markdown report generator."""
from datetime import datetime
from pathlib import Path

import pytest

from pim_auto.core.activity_correlator import ActivityEvent
from pim_auto.core.pim_detector import PIMActivation
from pim_auto.core.risk_assessor import AlignmentLevel, RiskAssessment
from pim_auto.reporting.markdown_generator import MarkdownGenerator


@pytest.fixture
def generator():
    """Create markdown generator instance."""
    return MarkdownGenerator()


@pytest.fixture
def sample_activations():
    """Create sample PIM activations."""
    return [
        PIMActivation(
            user_email="user1@example.com",
            role_name="Contributor",
            activation_reason="Add storage account",
            activation_time=datetime(2026, 2, 11, 10, 0, 0),
            duration_hours=24,
        ),
        PIMActivation(
            user_email="user2@example.com",
            role_name="Owner",
            activation_reason="Fix network issue",
            activation_time=datetime(2026, 2, 11, 12, 0, 0),
            duration_hours=24,
        ),
    ]


@pytest.fixture
def sample_activities():
    """Create sample activity events."""
    return {
        "user1@example.com": [
            ActivityEvent(
                timestamp=datetime(2026, 2, 11, 10, 30, 0),
                operation_name="Create Storage Account",
                resource_name="storage123",
                resource_type="Microsoft.Storage/storageAccounts",
                status="Success",
            )
        ],
        "user2@example.com": [
            ActivityEvent(
                timestamp=datetime(2026, 2, 11, 12, 15, 0),
                operation_name="Update NSG Rule",
                resource_name="nsg-prod",
                resource_type="Microsoft.Network/networkSecurityGroups",
                status="Success",
            )
        ],
    }


@pytest.fixture
def sample_assessments():
    """Create sample risk assessments."""
    return {
        "user1@example.com": RiskAssessment(
            level=AlignmentLevel.ALIGNED,
            explanation="User created storage account as stated in activation reason.",
        ),
        "user2@example.com": RiskAssessment(
            level=AlignmentLevel.NOT_ALIGNED,
            explanation="User modified NSG which is not related to stated reason.",
        ),
    }


def test_generate_report_with_activations(
    generator, sample_activations, sample_activities, sample_assessments
):
    """Test generating report with activations."""
    report = generator.generate_report(
        activations=sample_activations,
        activities_by_user=sample_activities,
        assessments_by_user=sample_assessments,
    )

    # Check header
    assert "# PIM Activity Audit Report" in report
    assert "**Generated**:" in report

    # Check summary
    assert "## Executive Summary" in report
    assert "**Total PIM Activations**: 2" in report
    assert "**Aligned**: 1 ✅" in report
    assert "**Not Aligned**: 1 ❌" in report

    # Check activations table
    assert "## PIM Activations" in report
    assert "user1@example.com" in report
    assert "user2@example.com" in report
    assert "Add storage account" in report
    assert "Fix network issue" in report

    # Check detailed analysis
    assert "## Detailed Analysis" in report
    assert "### user1@example.com" in report
    assert "### user2@example.com" in report


def test_generate_report_empty(generator):
    """Test generating report with no activations."""
    report = generator.generate_report(
        activations=[],
        activities_by_user={},
        assessments_by_user={},
    )

    assert "# PIM Activity Audit Report" in report
    assert "No activations found" in report


def test_generate_report_to_file(
    generator, sample_activations, sample_activities, sample_assessments, tmp_path
):
    """Test writing report to file."""
    output_path = tmp_path / "report.md"

    report = generator.generate_report(
        activations=sample_activations,
        activities_by_user=sample_activities,
        assessments_by_user=sample_assessments,
        output_path=output_path,
    )

    assert output_path.exists()
    content = output_path.read_text()
    assert content == report
    assert "# PIM Activity Audit Report" in content


def test_format_activations_summary(generator, sample_activations):
    """Test formatting activations summary."""
    summary = generator.format_activations_summary(sample_activations)

    assert "Found 2 elevated user(s)" in summary
    assert "user1@example.com" in summary
    assert "user2@example.com" in summary
    assert "Add storage account" in summary
    assert "activated" in summary
    assert "hours ago" in summary


def test_format_activations_summary_empty(generator):
    """Test formatting empty activations summary."""
    summary = generator.format_activations_summary([])
    assert "No PIM activations found" in summary


def test_format_activities(generator, sample_activities):
    """Test formatting activities."""
    activities = sample_activities["user1@example.com"]
    formatted = generator.format_activities(activities)

    assert "[2026-02-11 10:30:00]" in formatted
    assert "Create Storage Account" in formatted
    assert "storage123" in formatted


def test_format_activities_empty(generator):
    """Test formatting empty activities."""
    formatted = generator.format_activities([])
    assert "No activities found" in formatted


def test_format_assessment(generator, sample_assessments):
    """Test formatting assessment."""
    assessment = sample_assessments["user1@example.com"]
    formatted = generator.format_assessment(assessment)

    assert "aligned ✅" in formatted
    assert "User created storage account" in formatted


def test_alignment_level_emojis(generator):
    """Test alignment level emoji mapping."""
    assert generator._get_alignment_emoji(AlignmentLevel.ALIGNED) == "✅"
    assert generator._get_alignment_emoji(AlignmentLevel.PARTIALLY_ALIGNED) == "⚠️"
    assert generator._get_alignment_emoji(AlignmentLevel.NOT_ALIGNED) == "❌"
    assert generator._get_alignment_emoji(AlignmentLevel.UNKNOWN) == "❓"


def test_generate_summary_counts(generator, sample_activations, sample_assessments):
    """Test summary generation with correct counts."""
    summary = generator._generate_summary(sample_activations, sample_assessments)

    assert "**Total PIM Activations**: 2" in summary
    assert "**Aligned**: 1" in summary
    assert "**Not Aligned**: 1" in summary
    assert "**Partially Aligned**: 0" in summary
    assert "**Unknown**: 0" in summary


def test_generate_activations_table_empty(generator):
    """Test generating empty activations table."""
    table = generator._generate_activations_table([])
    assert "No activations found" in table


def test_detailed_analysis_without_assessment(generator, sample_activations, sample_activities):
    """Test detailed analysis when assessment is missing."""
    # Create assessments dict with only one user
    assessments = {
        "user1@example.com": RiskAssessment(
            level=AlignmentLevel.ALIGNED,
            explanation="Test explanation",
        )
    }

    report = generator.generate_report(
        activations=sample_activations,
        activities_by_user=sample_activities,
        assessments_by_user=assessments,
    )

    assert "**Assessment**: Not available" in report
