"""Application Insights integration for monitoring and telemetry."""
import logging
import os
from typing import Any, Dict, Optional

from opencensus.ext.azure import metrics_exporter
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module

logger = logging.getLogger(__name__)


class ApplicationInsightsMonitor:
    """Application Insights monitoring and metrics collection."""

    def __init__(self, connection_string: Optional[str] = None, enabled: bool = True):
        """
        Initialize Application Insights monitor.

        Args:
            connection_string: Application Insights connection string.
                              If None, reads from APPLICATIONINSIGHTS_CONNECTION_STRING env var.
            enabled: Whether monitoring is enabled. Defaults to True.
        """
        self.enabled = enabled
        self.connection_string = connection_string or os.getenv(
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        )

        if not self.connection_string:
            logger.warning(
                "Application Insights connection string not provided. "
                "Monitoring will be disabled."
            )
            self.enabled = False

        self.stats = stats_module.stats
        self.view_manager = self.stats.view_manager
        self.stats_recorder = self.stats.stats_recorder

        # Define custom measures
        self.pim_activations_measure = measure_module.MeasureInt(
            "pim_activations_detected",
            "Number of PIM activations detected",
            "activations",
        )

        self.activities_measure = measure_module.MeasureInt(
            "user_activities_found", "Number of activities found per user", "activities"
        )

        self.query_duration_measure = measure_module.MeasureFloat(
            "query_duration_ms", "Query execution duration", "milliseconds"
        )

        self.openai_calls_measure = measure_module.MeasureInt(
            "openai_api_calls", "Number of OpenAI API calls", "calls"
        )

        if self.enabled:
            self._setup_metrics_exporter()
            self._register_views()

    def _setup_metrics_exporter(self) -> None:
        """Set up Azure Monitor metrics exporter."""
        try:
            exporter = metrics_exporter.new_metrics_exporter(
                connection_string=self.connection_string
            )
            self.view_manager.register_exporter(exporter)
            logger.info("Application Insights metrics exporter configured")
        except Exception as e:
            logger.error(f"Failed to configure metrics exporter: {e}")
            self.enabled = False

    def _register_views(self) -> None:
        """Register metric views for aggregation."""
        # PIM activations count view
        pim_view = view_module.View(
            "pim_activations_view",
            "Number of PIM activations detected",
            [],
            self.pim_activations_measure,
            aggregation_module.SumAggregation(),
        )

        # Activities count view
        activities_view = view_module.View(
            "activities_view",
            "Number of activities found per user",
            [],
            self.activities_measure,
            aggregation_module.SumAggregation(),
        )

        # Query duration view
        query_duration_view = view_module.View(
            "query_duration_view",
            "Query execution duration",
            [],
            self.query_duration_measure,
            aggregation_module.LastValueAggregation(),
        )

        # OpenAI API calls view
        openai_view = view_module.View(
            "openai_calls_view",
            "Number of OpenAI API calls",
            [],
            self.openai_calls_measure,
            aggregation_module.CountAggregation(),
        )

        self.view_manager.register_view(pim_view)
        self.view_manager.register_view(activities_view)
        self.view_manager.register_view(query_duration_view)
        self.view_manager.register_view(openai_view)

        logger.info("Application Insights metric views registered")

    def track_pim_activations(self, count: int) -> None:
        """
        Track number of PIM activations detected.

        Args:
            count: Number of activations detected
        """
        if not self.enabled:
            return

        try:
            mmap = self.stats_recorder.new_measurement_map()
            tmap = tag_map_module.TagMap()
            mmap.measure_int_put(self.pim_activations_measure, count)
            mmap.record(tmap)
            logger.debug(f"Tracked {count} PIM activations")
        except Exception as e:
            logger.warning(f"Failed to track PIM activations: {e}")

    def track_user_activities(self, count: int) -> None:
        """
        Track number of activities found for a user.

        Args:
            count: Number of activities found
        """
        if not self.enabled:
            return

        try:
            mmap = self.stats_recorder.new_measurement_map()
            tmap = tag_map_module.TagMap()
            mmap.measure_int_put(self.activities_measure, count)
            mmap.record(tmap)
            logger.debug(f"Tracked {count} user activities")
        except Exception as e:
            logger.warning(f"Failed to track user activities: {e}")

    def track_query_duration(self, duration_ms: float, query_type: str) -> None:
        """
        Track query execution duration.

        Args:
            duration_ms: Query duration in milliseconds
            query_type: Type of query (e.g., 'pim_detection', 'activity_correlation')
        """
        if not self.enabled:
            return

        try:
            mmap = self.stats_recorder.new_measurement_map()
            tmap = tag_map_module.TagMap()
            mmap.measure_float_put(self.query_duration_measure, duration_ms)
            mmap.record(tmap)
            logger.debug(f"Tracked {query_type} query duration: {duration_ms}ms")
        except Exception as e:
            logger.warning(f"Failed to track query duration: {e}")

    def track_openai_call(self) -> None:
        """Track an OpenAI API call."""
        if not self.enabled:
            return

        try:
            mmap = self.stats_recorder.new_measurement_map()
            tmap = tag_map_module.TagMap()
            mmap.measure_int_put(self.openai_calls_measure, 1)
            mmap.record(tmap)
            logger.debug("Tracked OpenAI API call")
        except Exception as e:
            logger.warning(f"Failed to track OpenAI call: {e}")

    def get_log_handler(self) -> Optional[logging.Handler]:
        """
        Get Azure Log Handler for logging integration.

        Returns:
            AzureLogHandler if enabled, None otherwise
        """
        if not self.enabled or not self.connection_string:
            return None

        try:
            handler = AzureLogHandler(connection_string=self.connection_string)
            handler.setLevel(logging.INFO)
            logger.info("Application Insights log handler created")
            return handler
        except Exception as e:
            logger.error(f"Failed to create log handler: {e}")
            return None

    def track_exception(self, exception: Exception, properties: Optional[Dict[str, Any]] = None) -> None:
        """
        Track an exception with optional properties.

        Args:
            exception: The exception to track
            properties: Optional additional properties
        """
        if not self.enabled:
            return

        try:
            # Log the exception - will be picked up by log handler
            logger.error(
                f"Exception tracked: {type(exception).__name__}: {str(exception)}",
                exc_info=exception,
                extra=properties or {},
            )
        except Exception as e:
            logger.warning(f"Failed to track exception: {e}")
