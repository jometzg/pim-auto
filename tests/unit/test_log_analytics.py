"""Tests for Log Analytics client module."""

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from azure.monitor.query import LogsQueryStatus

from src.pim_auto.azure.log_analytics import LogAnalyticsClient


@pytest.fixture
def mock_credential() -> Mock:
    """Mock Azure credential."""
    return Mock()


@pytest.fixture
def mock_logs_client() -> Mock:
    """Mock LogsQueryClient."""
    return Mock()


def test_log_analytics_client_init(
    mock_credential: Mock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test Log Analytics client initialization."""
    mock_client_class = Mock()
    monkeypatch.setattr(
        "src.pim_auto.azure.log_analytics.LogsQueryClient",
        mock_client_class
    )

    client = LogAnalyticsClient(
        workspace_id="test-workspace-id", credential=mock_credential
    )

    assert client.workspace_id == "test-workspace-id"
    mock_client_class.assert_called_once_with(mock_credential)


def test_execute_query_success(
    mock_credential: Mock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test successful query execution."""
    # Mock response
    mock_response = Mock()
    mock_response.status = LogsQueryStatus.SUCCESS

    mock_table = Mock()
    # Columns are now strings directly, not objects with .name
    mock_table.columns = ["TimeGenerated", "UserEmail"]
    mock_table.rows = [
        [
            datetime(2026, 2, 10, 10, 0, 0, tzinfo=timezone.utc),
            "test@example.com"
        ],
        [
            datetime(2026, 2, 10, 11, 0, 0, tzinfo=timezone.utc),
            "user@example.com"
        ],
    ]

    mock_response.tables = [mock_table]

    # Mock client
    mock_client_instance = Mock()
    mock_client_instance.query_workspace.return_value = mock_response

    mock_client_class = Mock(return_value=mock_client_instance)
    monkeypatch.setattr(
        "src.pim_auto.azure.log_analytics.LogsQueryClient",
        mock_client_class
    )

    client = LogAnalyticsClient(
        workspace_id="test-workspace-id", credential=mock_credential
    )
    results = client.execute_query("test query", timespan="P1D")

    assert len(results) == 2
    assert results[0]["TimeGenerated"] == datetime(
        2026, 2, 10, 10, 0, 0, tzinfo=timezone.utc
    )
    assert results[0]["UserEmail"] == "test@example.com"
    assert results[1]["UserEmail"] == "user@example.com"


def test_execute_query_failure(
    mock_credential: Mock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test query execution failure."""
    mock_response = Mock()
    mock_response.status = "FAILED"

    mock_client_instance = Mock()
    mock_client_instance.query_workspace.return_value = mock_response

    mock_client_class = Mock(return_value=mock_client_instance)
    monkeypatch.setattr(
        "src.pim_auto.azure.log_analytics.LogsQueryClient",
        mock_client_class
    )

    client = LogAnalyticsClient(
        workspace_id="test-workspace-id", credential=mock_credential
    )
    results = client.execute_query("test query")

    assert results == []


def test_execute_query_exception(
    mock_credential: Mock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test query execution with exception."""
    mock_client_instance = Mock()
    mock_client_instance.query_workspace.side_effect = Exception(
        "API Error"
    )

    mock_client_class = Mock(return_value=mock_client_instance)
    monkeypatch.setattr(
        "src.pim_auto.azure.log_analytics.LogsQueryClient",
        mock_client_class
    )

    client = LogAnalyticsClient(
        workspace_id="test-workspace-id", credential=mock_credential
    )

    with pytest.raises(Exception, match="API Error"):
        client.execute_query("test query")
