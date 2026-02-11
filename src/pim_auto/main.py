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

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--mode",
    type=click.Choice(["interactive", "batch"], case_sensitive=False),
    default="interactive",
    help="Run mode: interactive (default) or batch",
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
def main(
    mode: str, log_level: str, output: Optional[Path], hours: Optional[int]
) -> int:
    """Main application entry point."""
    # Configure logging with specified level
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )
    
    # Reduce noise from Azure SDK authentication chain
    # Only show warnings/errors from these unless user explicitly wants DEBUG
    if log_level.upper() != "DEBUG":
        logging.getLogger("azure.identity").setLevel(logging.WARNING)
        logging.getLogger("azure.core.pipeline.policies").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    try:
        # Load and validate configuration
        logger.info("Loading configuration...")
        config = Config.from_environment()
        config.validate()
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

        # Route to appropriate interface
        if mode.lower() == "batch":
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
