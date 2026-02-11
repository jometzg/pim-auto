"""Tests for Application Insights monitoring."""

import os
from unittest.mock import MagicMock, patch

from pim_auto.monitoring.app_insights import ApplicationInsightsMonitor


class TestApplicationInsightsMonitor:
    """Test Application Insights monitoring functionality."""

    def test_monitor_disabled_without_connection_string(self):
        """Test monitor is disabled when connection string is missing."""
        # Remove env var if present
        with patch.dict(os.environ, {}, clear=True):
            monitor = ApplicationInsightsMonitor(connection_string=None)

            assert monitor.enabled is False
            assert monitor.connection_string is None

    def test_monitor_enabled_with_connection_string(self):
        """Test monitor is enabled when connection string provided."""
        conn_string = (
            "InstrumentationKey=test-key;"
            "IngestionEndpoint=https://test.monitor.azure.com/"
        )

        with patch("pim_auto.monitoring.app_insights.metrics_exporter"):
            monitor = ApplicationInsightsMonitor(
                connection_string=conn_string,
                enabled=True,
            )

            assert monitor.connection_string == conn_string

    def test_track_pim_activations_when_disabled(self):
        """Test tracking does nothing when monitor is disabled."""
        monitor = ApplicationInsightsMonitor(connection_string=None)

        # Should not raise exception
        monitor.track_pim_activations(5)

    @patch("pim_auto.monitoring.app_insights.metrics_exporter")
    def test_track_pim_activations_when_enabled(self, mock_exporter):
        """Test tracking PIM activations when enabled."""
        conn_string = "InstrumentationKey=test-key"
        monitor = ApplicationInsightsMonitor(connection_string=conn_string)

        # Mock the stats recorder
        with patch.object(
            monitor.stats_recorder, "new_measurement_map"
        ) as mock_mmap_factory:
            mock_mmap = MagicMock()
            mock_mmap_factory.return_value = mock_mmap

            monitor.track_pim_activations(3)

            # Verify measurement was created and recorded
            mock_mmap.measure_int_put.assert_called_once()
            mock_mmap.record.assert_called_once()

    @patch("pim_auto.monitoring.app_insights.metrics_exporter")
    def test_track_user_activities(self, mock_exporter):
        """Test tracking user activities."""
        conn_string = "InstrumentationKey=test-key"
        monitor = ApplicationInsightsMonitor(connection_string=conn_string)

        with patch.object(
            monitor.stats_recorder, "new_measurement_map"
        ) as mock_mmap_factory:
            mock_mmap = MagicMock()
            mock_mmap_factory.return_value = mock_mmap

            monitor.track_user_activities(10)

            mock_mmap.measure_int_put.assert_called_once()
            mock_mmap.record.assert_called_once()

    @patch("pim_auto.monitoring.app_insights.metrics_exporter")
    def test_track_query_duration(self, mock_exporter):
        """Test tracking query duration."""
        conn_string = "InstrumentationKey=test-key"
        monitor = ApplicationInsightsMonitor(connection_string=conn_string)

        with patch.object(
            monitor.stats_recorder, "new_measurement_map"
        ) as mock_mmap_factory:
            mock_mmap = MagicMock()
            mock_mmap_factory.return_value = mock_mmap

            monitor.track_query_duration(1500.5, "pim_detection")

            mock_mmap.measure_float_put.assert_called_once()
            mock_mmap.record.assert_called_once()

    @patch("pim_auto.monitoring.app_insights.metrics_exporter")
    def test_track_openai_call(self, mock_exporter):
        """Test tracking OpenAI API calls."""
        conn_string = "InstrumentationKey=test-key"
        monitor = ApplicationInsightsMonitor(connection_string=conn_string)

        with patch.object(
            monitor.stats_recorder, "new_measurement_map"
        ) as mock_mmap_factory:
            mock_mmap = MagicMock()
            mock_mmap_factory.return_value = mock_mmap

            monitor.track_openai_call()

            mock_mmap.measure_int_put.assert_called_once()
            mock_mmap.record.assert_called_once()

    def test_get_log_handler_when_disabled(self):
        """Test log handler returns None when disabled."""
        monitor = ApplicationInsightsMonitor(connection_string=None)

        handler = monitor.get_log_handler()

        assert handler is None

    @patch("pim_auto.monitoring.app_insights.metrics_exporter")
    @patch("pim_auto.monitoring.app_insights.AzureLogHandler")
    def test_get_log_handler_when_enabled(
            self, mock_handler_class,
            mock_exporter,
            ):
        """Test log handler creation when enabled."""
        conn_string = "InstrumentationKey=test-key"
        monitor = ApplicationInsightsMonitor(connection_string=conn_string)

        mock_handler = MagicMock()
        mock_handler_class.return_value = mock_handler

        handler = monitor.get_log_handler()

        assert handler is not None
        mock_handler_class.assert_called_once_with(
            connection_string=conn_string
        )
        mock_handler.setLevel.assert_called_once()

    @patch("pim_auto.monitoring.app_insights.metrics_exporter")
    def test_track_exception(self, mock_exporter):
        """Test exception tracking."""
        conn_string = "InstrumentationKey=test-key"
        monitor = ApplicationInsightsMonitor(connection_string=conn_string)

        test_exception = ValueError("Test error")
        properties = {"user": "test@example.com"}

        # Should not raise exception
        monitor.track_exception(test_exception, properties)

    def test_monitor_reads_from_environment(self):
        """Test monitor reads connection string from environment."""
        conn_string = "InstrumentationKey=env-key"

        env_var = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        with patch.dict(os.environ, {env_var: conn_string}):
            with patch("pim_auto.monitoring.app_insights.metrics_exporter"):
                monitor = ApplicationInsightsMonitor()

                assert monitor.connection_string == conn_string
