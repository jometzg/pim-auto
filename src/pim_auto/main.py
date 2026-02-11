"""Main entry point for PIM Auto application."""
import logging
import sys
from pathlib import Path
from typing import Optional

import click

from pim_auto.azure.auth import get_azure_credential
from pim_auto.azure.log_analytics import LogAnalyticsClient
from pim_auto.azure.openai_client import OpenAIClient
from pim_auto.config import Config
from pim_auto.interfaces.batch_runner import BatchRunner
from pim_auto.interfaces.interactive_cli import InteractiveCLI
from pim_auto.monitoring.app_insights import ApplicationInsightsMonitor
from pim_auto.monitoring.health import HealthCheck
from pim_auto.monitoring.logging import StructuredLogger

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--mode",
    type=click.Choice(["interactive", "batch", "health"], case_sensitive=False),
    default="interactive",
    help="Run mode: interactive (default), batch, or health check",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Set the logging level",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file path for batch mode report",
)
@click.option(
    "--hours",
    type=int,
    default=None,
    help="Number of hours to scan (overrides config default)",
)
@click.option(
    "--detailed-health",
    is_flag=True,
    default=False,
    help="Show detailed health check (only for health mode)",
)
def main(
    mode: str, 
    log_level: str, 
    output: Optional[Path], 
    hours: Optional[int],
    detailed_health: bool,
) -> int:
    """Main application entry point."""
    try:
        # Load and validate configuration
        config = Config.from_environment()
        config.validate()
        
        # Configure structured logging
        monitor = None
        if config.enable_app_insights and config.app_insights_connection_string:
            monitor = ApplicationInsightsMonitor(
                connection_string=config.app_insights_connection_string,
                enabled=True,
            )
            app_insights_handler = monitor.get_log_handler()
        else:
            app_insights_handler = None
        
        StructuredLogger.setup(
            log_level=log_level,
            json_format=config.structured_logging,
            include_app_insights=config.enable_app_insights,
            app_insights_handler=app_insights_handler,
        )
        
        logger.info("Loading configuration...")
        logger.info("Configuration loaded successfully")

        # Initialize Azure clients
        logger.info("Initializing Azure clients...")
        credential = get_azure_credential()

        log_analytics = LogAnalyticsClient(
            workspace_id=config.log_analytics_workspace_id, credential=credential
        )

        openai_client = OpenAIClient(
            endpoint=config.azure_openai_endpoint,
            deployment=config.azure_openai_deployment,
            api_version=config.azure_openai_api_version,
            credential=credential,
        )

        logger.info("Azure clients initialized successfully")
        
        # Initialize health check
        health_check = HealthCheck(
            workspace_id=config.log_analytics_workspace_id,
            credential=credential,
            openai_endpoint=config.azure_openai_endpoint,
        )

        # Route to appropriate interface
        if mode.lower() == "health":
            logger.info("Running health check")
            health_result = health_check.check_health(detailed=detailed_health)
            import json
            print(json.dumps(health_result, indent=2))
            return 0 if health_result["status"] in ["healthy", "degraded"] else 1
        elif mode.lower() == "batch":
            logger.info("Running in batch mode")
            runner = BatchRunner(log_analytics, openai_client, config)
            return runner.run(hours=hours, output_path=output)
        else:
            logger.info("Running in interactive mode")
            cli = InteractiveCLI(log_analytics, openai_client, config)
            return cli.run()

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())  # pylint: disable=no-value-for-parameter
