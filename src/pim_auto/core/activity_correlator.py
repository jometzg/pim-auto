"""Activity correlation module."""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List

logger = logging.getLogger(__name__)


@dataclass
class ActivityEvent:
    """Represents an Azure activity event."""

    timestamp: datetime
    operation_name: str
    resource_type: str
    resource_name: str
    status: str
    resource_group: str
    subscription_id: str


class ActivityCorrelator:
    """Correlates user activities with PIM activations."""

    def __init__(self, log_analytics_client: Any):
        self.log_analytics_client = log_analytics_client

    def get_user_activities(
        self, user_email: str, start_time: datetime, end_time: datetime
    ) -> List[ActivityEvent]:
        """Get all activities for a user in the specified time range."""
        query = f"""
        AzureActivity
        | where TimeGenerated between (datetime("{start_time.isoformat()}") .. datetime("{end_time.isoformat()}"))
        | where Caller == "{user_email}"
        | where ActivityStatusValue == "Success"
        | project
            TimeGenerated,
            OperationName,
            ResourceProviderValue,
            Resource,
            ResourceGroup,
            SubscriptionId,
            ActivityStatusValue
        | order by TimeGenerated asc
        """

        results = self.log_analytics_client.execute_query(query=query, timespan=None)

        activities = []
        for row in results:
            # Debug: log what we're getting from the query
            logger.debug(f"Activity row: {row}")
            activities.append(
                ActivityEvent(
                    timestamp=row["TimeGenerated"],
                    operation_name=row.get("OperationName", "Unknown"),
                    resource_type=row.get("ResourceProviderValue", "Unknown"),
                    resource_name=row.get("Resource", "Unknown"),
                    status=row.get("ActivityStatusValue", "Unknown"),
                    resource_group=row.get("ResourceGroup", "Unknown"),
                    subscription_id=row.get("SubscriptionId", "Unknown"),
                )
            )

        logger.info(f"Found {len(activities)} activities for {user_email}")
        return activities
