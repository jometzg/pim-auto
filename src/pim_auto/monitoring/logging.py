"""Structured JSON logging configuration."""

import logging
import sys
from typing import Optional

from pythonjsonlogger import jsonlogger


class StructuredLogger:
    """Configure structured JSON logging for the application."""

    @staticmethod
    def setup(
        log_level: str = "INFO",
        json_format: bool = True,
        include_app_insights: bool = False,
        app_insights_handler: Optional[logging.Handler] = None,
    ) -> None:
        """
        Set up structured logging for the application.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            json_format: Whether to use JSON format (True) or standard format (False)
            include_app_insights: Whether to include Application Insights handler
            app_insights_handler: Application Insights log handler to add
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))

        # Remove existing handlers
        root_logger.handlers.clear()

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))

        if json_format:
            # JSON formatter for structured logging
            formatter = jsonlogger.JsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        else:
            # Standard formatter for local development
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # Add Application Insights handler if provided
        if include_app_insights and app_insights_handler:
            root_logger.addHandler(app_insights_handler)
            logging.info("Application Insights log handler added")

        # Reduce noise from Azure SDK unless debug mode
        if log_level.upper() != "DEBUG":
            logging.getLogger("azure.identity").setLevel(logging.WARNING)
            logging.getLogger("azure.core.pipeline.policies").setLevel(logging.WARNING)
            logging.getLogger("urllib3").setLevel(logging.WARNING)
            logging.getLogger("opencensus").setLevel(logging.WARNING)

        logging.info(f"Structured logging configured: level={log_level}, json_format={json_format}")
