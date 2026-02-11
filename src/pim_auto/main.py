"""Main entry point for PIM Auto application."""
import logging
import sys

import click

from pim_auto.azure.auth import get_azure_credential
from pim_auto.azure.log_analytics import LogAnalyticsClient
from pim_auto.azure.openai_client import OpenAIClient
from pim_auto.config import Config
from pim_auto.core.pim_detector import PIMDetector

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Set the logging level",
)
def main(log_level: str) -> int:
    """Main application entry point."""
    # Configure logging with specified level
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )
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

        _openai_client = OpenAIClient(
            endpoint=config.azure_openai_endpoint,
            deployment=config.azure_openai_deployment,
            api_version=config.azure_openai_api_version,
            credential=credential,
        )

        logger.info("Azure clients initialized successfully")

        # Basic functionality test: detect PIM activations
        logger.info(
            f"Scanning for PIM activations (last {config.default_scan_hours} hours)..."
        )
        pim_detector = PIMDetector(log_analytics)
        activations = pim_detector.detect_activations(hours=config.default_scan_hours)

        logger.info(f"Found {len(activations)} PIM activations")
        for activation in activations:
            logger.info(
                f"  - {activation.user_email}: {activation.role_name} (Reason: {activation.activation_reason})"
            )

        return 0

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())  # pylint: disable=no-value-for-parameter
