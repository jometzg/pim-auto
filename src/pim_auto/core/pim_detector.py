"""PIM activation detection module."""
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List

logger = logging.getLogger(__name__)


@dataclass
class PIMActivation:
    """Represents a PIM activation event."""

    user_email: str
    role_name: str
    activation_reason: str
    activation_time: datetime
    duration_hours: int


class PIMDetector:
    """Detects PIM activations from Azure Log Analytics."""

    def __init__(self, log_analytics_client: Any):
        self.log_analytics_client = log_analytics_client

    def detect_activations(self, hours: int = 24) -> List[PIMActivation]:
        """Detect PIM activations in the specified time window."""
        query = f"""
        AuditLogs
        | where TimeGenerated > ago({hours}h)
        | where OperationName == "Add member to role completed (PIM activation)"
        | extend ReasonValue = tostring(parse_json(tostring(AdditionalDetails[3])).value)
        | project
            TimeGenerated,
            UserEmail = tostring(InitiatedBy.user.userPrincipalName),
            RoleName = tostring(TargetResources[0].displayName),
            Reason = iff(isempty(ResultDescription), ReasonValue, ResultDescription)
        | order by TimeGenerated desc
        """

        results = self.log_analytics_client.execute_query(
            query=query, timespan=f"PT{hours}H"
        )

        activations = []
        for row in results:
            activations.append(
                PIMActivation(
                    user_email=row["UserEmail"],
                    role_name=row["RoleName"],
                    activation_reason=row["Reason"],
                    activation_time=row["TimeGenerated"],
                    duration_hours=hours,  # Simplified: assume full window
                )
            )

        logger.info(f"Detected {len(activations)} PIM activations")
        return activations
