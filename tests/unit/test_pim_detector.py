"""Tests for PIM detector module."""

from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest

from src.pim_auto.core.pim_detector import PIMActivation, PIMDetector


@pytest.fixture
def mock_log_analytics() -> Mock:
    """Mock Log Analytics client."""
    client = Mock()
    client.execute_query = MagicMock(
        return_value=[
            {
                "TimeGenerated": datetime(2026, 2, 10, 10, 0, 0),
                "UserEmail": "john.doe@contoso.com",
                "RoleName": "Contributor",
                "Reason": "need to add a storage account",
            },
            {
                "TimeGenerated": datetime(2026, 2, 10, 11, 0, 0),
                "UserEmail": "jane.smith@contoso.com",
                "RoleName": "Owner",
                "Reason": "emergency production fix",
            },
        ]
    )
    return client


def test_detect_activations(mock_log_analytics: Mock) -> None:
    """Test PIM activation detection."""
    detector = PIMDetector(mock_log_analytics)
    activations = detector.detect_activations(hours=24)

    assert len(activations) == 2
    assert activations[0].user_email == "john.doe@contoso.com"
    assert activations[0].role_name == "Contributor"
    assert activations[0].activation_reason == "need to add a storage account"
    assert activations[1].user_email == "jane.smith@contoso.com"
    assert activations[1].role_name == "Owner"


def test_detect_activations_empty(mock_log_analytics: Mock) -> None:
    """Test PIM detection with no results."""
    mock_log_analytics.execute_query.return_value = []

    detector = PIMDetector(mock_log_analytics)
    activations = detector.detect_activations(hours=24)

    assert len(activations) == 0


def test_detect_activations_query_format(mock_log_analytics: Mock) -> None:
    """Test that the query is formatted correctly."""
    mock_log_analytics.execute_query.return_value = []

    detector = PIMDetector(mock_log_analytics)
    detector.detect_activations(hours=48)

    # Verify query contains correct hour value
    call_args = mock_log_analytics.execute_query.call_args
    query = call_args.kwargs["query"]
    assert "ago(48h)" in query
    assert "AuditLogs" in query


def test_pim_activation_dataclass() -> None:
    """Test PIMActivation dataclass."""
    activation = PIMActivation(
        user_email="test@example.com",
        role_name="Contributor",
        activation_reason="test reason",
        activation_time=datetime(2026, 2, 10, 10, 0, 0),
        duration_hours=24,
    )

    assert activation.user_email == "test@example.com"
    assert activation.role_name == "Contributor"
    assert activation.activation_reason == "test reason"
    assert activation.duration_hours == 24
