"""Tests for activity correlator module."""
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from src.pim_auto.core.activity_correlator import ActivityCorrelator, ActivityEvent


@pytest.fixture
def mock_log_analytics() -> Mock:
    """Mock Log Analytics client."""
    client = Mock()
    client.execute_query.return_value = [
        {
            "TimeGenerated": datetime(2026, 2, 10, 10, 30, 0, tzinfo=timezone.utc),
            "OperationName": "Create Storage Account",
            "ResourceProviderValue": "Microsoft.Storage/storageAccounts",
            "Resource": "mystorageaccount",
            "ActivityStatusValue": "Success",
            "ResourceGroup": "rg-production",
            "SubscriptionId": "abc123-def456-ghi789",
        },
        {
            "TimeGenerated": datetime(2026, 2, 10, 11, 0, 0, tzinfo=timezone.utc),
            "OperationName": "Update Resource Group",
            "ResourceProviderValue": "Microsoft.Resources/resourceGroups",
            "Resource": "my-rg",
            "ActivityStatusValue": "Success",
            "ResourceGroup": "my-rg",
            "SubscriptionId": "abc123-def456-ghi789",
        },
    ]
    return client


def test_get_user_activities(mock_log_analytics: Mock) -> None:
    """Test getting user activities."""
    correlator = ActivityCorrelator(mock_log_analytics)

    start_time = datetime(2026, 2, 10, 10, 0, 0)
    end_time = datetime(2026, 2, 10, 12, 0, 0)

    activities = correlator.get_user_activities(
        user_email="test@example.com", start_time=start_time, end_time=end_time
    )

    assert len(activities) == 2
    assert activities[0].operation_name == "Create Storage Account"
    assert activities[0].resource_type == "Microsoft.Storage/storageAccounts"
    assert activities[1].operation_name == "Update Resource Group"


def test_get_user_activities_empty(mock_log_analytics: Mock) -> None:
    """Test getting user activities with no results."""
    mock_log_analytics.execute_query.return_value = []

    correlator = ActivityCorrelator(mock_log_analytics)

    start_time = datetime(2026, 2, 10, 10, 0, 0)
    end_time = datetime(2026, 2, 10, 12, 0, 0)

    activities = correlator.get_user_activities(
        user_email="test@example.com", start_time=start_time, end_time=end_time
    )

    assert len(activities) == 0


def test_get_user_activities_query_format(mock_log_analytics: Mock) -> None:
    """Test that the query is formatted correctly."""
    mock_log_analytics.execute_query.return_value = []

    correlator = ActivityCorrelator(mock_log_analytics)

    start_time = datetime(2026, 2, 10, 10, 0, 0)
    end_time = datetime(2026, 2, 10, 12, 0, 0)

    correlator.get_user_activities(
        user_email="test@example.com", start_time=start_time, end_time=end_time
    )

    # Verify query contains correct parameters
    call_args = mock_log_analytics.execute_query.call_args
    query = call_args.kwargs["query"]
    assert "AzureActivity" in query
    assert "test@example.com" in query


def test_activity_event_dataclass() -> None:
    """Test ActivityEvent dataclass."""
    event = ActivityEvent(
        timestamp=datetime(2026, 2, 10, 10, 0, 0, tzinfo=timezone.utc),
        operation_name="Test Operation",
        resource_type="Microsoft.Test/resources",
        resource_name="test-resource",
        status="Succeeded",
        resource_group="test-rg",
        subscription_id="test-sub-id",
    )

    assert event.operation_name == "Test Operation"
    assert event.resource_type == "Microsoft.Test/resources"
    assert event.status == "Succeeded"
    assert event.resource_group == "test-rg"
    assert event.subscription_id == "test-sub-id"


def test_get_user_activities_missing_fields(mock_log_analytics: Mock) -> None:
    """Test handling of missing optional fields."""
    mock_log_analytics.execute_query.return_value = [
        {
            "TimeGenerated": datetime(2026, 2, 10, 10, 30, 0, tzinfo=timezone.utc),
            "OperationName": "Test Operation",
            # Missing ResourceProviderValue, Resource, ActivityStatusValue, ResourceGroup, SubscriptionId
        }
    ]

    correlator = ActivityCorrelator(mock_log_analytics)

    start_time = datetime(2026, 2, 10, 10, 0, 0, tzinfo=timezone.utc)
    end_time = datetime(2026, 2, 10, 12, 0, 0, tzinfo=timezone.utc)

    activities = correlator.get_user_activities(
        user_email="test@example.com", start_time=start_time, end_time=end_time
    )

    assert len(activities) == 1
    assert activities[0].resource_type == "Unknown"
    assert activities[0].resource_name == "Unknown"
    assert activities[0].status == "Unknown"
    assert activities[0].resource_group == "Unknown"
    assert activities[0].subscription_id == "Unknown"
