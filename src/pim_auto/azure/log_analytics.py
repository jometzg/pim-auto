"""Azure Log Analytics client wrapper."""
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union

from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus

logger = logging.getLogger(__name__)


class LogAnalyticsClient:
    """Wrapper for Azure Log Analytics queries."""

    def __init__(self, workspace_id: str, credential: DefaultAzureCredential):
        self.workspace_id = workspace_id
        self.client = LogsQueryClient(credential)

    def execute_query(
        self, query: str, timespan: Optional[Union[str, timedelta]] = None
    ) -> List[Dict[str, Any]]:
        """Execute KQL query and return results."""
        try:
            # Convert string timespan to timedelta if needed
            actual_timespan: timedelta
            if timespan is not None:
                if isinstance(timespan, str):
                    # Parse ISO 8601 duration format (e.g., "P1D" = 1 day, "PT24H" = 24 hours)
                    if timespan.startswith("PT") and timespan.endswith("H"):
                        hours = int(timespan[2:-1])
                        actual_timespan = timedelta(hours=hours)
                    elif timespan.startswith("P") and timespan.endswith("D"):
                        days = int(timespan[1:-1])
                        actual_timespan = timedelta(days=days)
                    else:
                        actual_timespan = timedelta(days=1)  # Default
                else:
                    actual_timespan = timespan
            else:
                # Default to 24 hours if no timespan provided
                actual_timespan = timedelta(hours=24)

            # Log query at DEBUG level
            logger.debug(f"Executing Log Analytics query:\n{query}")
            logger.debug(f"Timespan: {actual_timespan}")

            response = self.client.query_workspace(
                workspace_id=self.workspace_id, query=query, timespan=actual_timespan
            )

            if response.status == LogsQueryStatus.SUCCESS:
                results = []
                for table in response.tables:
                    column_names = [str(col) for col in table.columns]
                    for row in table.rows:
                        row_dict = dict(zip(column_names, row, strict=False))
                        results.append(row_dict)
                logger.debug(f"Query returned {len(results)} rows")
                return results
            else:
                logger.error(f"Query failed with status: {response.status}")
                return []

        except Exception as e:
            logger.error(f"Log Analytics query error: {e}")
            raise
