"""Batch mode runner for automated PIM activity scanning."""
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pim_auto.azure.log_analytics import LogAnalyticsClient
from pim_auto.azure.openai_client import OpenAIClient
from pim_auto.config import Config
from pim_auto.core.activity_correlator import ActivityCorrelator, ActivityEvent
from pim_auto.core.pim_detector import PIMDetector
from pim_auto.core.risk_assessor import RiskAssessment, RiskAssessor
from pim_auto.reporting.markdown_generator import MarkdownGenerator

logger = logging.getLogger(__name__)


class BatchRunner:
    """Runs PIM activity audit in non-interactive batch mode."""

    def __init__(
        self,
        log_analytics: LogAnalyticsClient,
        openai_client: OpenAIClient,
        config: Config,
    ):
        """
        Initialize batch runner.

        Args:
            log_analytics: Log Analytics client
            openai_client: OpenAI client for risk assessment
            config: Application configuration
        """
        self.log_analytics = log_analytics
        self.openai_client = openai_client
        self.config = config
        self.pim_detector = PIMDetector(log_analytics)
        self.activity_correlator = ActivityCorrelator(log_analytics)
        self.risk_assessor = RiskAssessor(openai_client)
        self.markdown_generator = MarkdownGenerator()

    def run(self, hours: Optional[int] = None, output_path: Optional[Path] = None) -> int:
        """
        Run batch mode scan and generate report.

        Args:
            hours: Number of hours to scan (default from config)
            output_path: Path to output report file (default from config)

        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            scan_hours = hours or self.config.default_scan_hours
            logger.info(f"Starting batch mode scan (last {scan_hours} hours)")

            # Detect PIM activations
            logger.info("Scanning for PIM activations...")
            activations = self.pim_detector.detect_activations(hours=scan_hours)
            logger.info(f"Found {len(activations)} PIM activations")

            if not activations:
                logger.info("No activations found. Generating empty report.")
                report = self._generate_empty_report()
                self._output_report(report, output_path)
                return 0

            # Collect activities and assessments for each user
            activities_by_user: dict[str, list[ActivityEvent]] = {}
            assessments_by_user: dict[str, RiskAssessment] = {}

            for activation in activations:
                logger.info(f"Processing {activation.user_email}...")

                # Get activities
                end_time = datetime.now(timezone.utc)
                activities = self.activity_correlator.get_user_activities(
                    user_email=activation.user_email,
                    start_time=activation.activation_time,
                    end_time=end_time,
                )
                activities_by_user[activation.user_email] = activities
                logger.info(f"  Found {len(activities)} activities")

                # Assess alignment
                try:
                    assessment = self.risk_assessor.assess_alignment(
                        pim_reason=activation.activation_reason,
                        activities=activities,
                    )
                    assessments_by_user[activation.user_email] = assessment
                    logger.info(f"  Assessment: {assessment.level.value}")
                except Exception as e:
                    logger.warning(f"  Failed to assess alignment: {e}")
                    # Continue with other users even if one assessment fails

            # Generate report
            logger.info("Generating markdown report...")
            report = self.markdown_generator.generate_report(
                activations=activations,
                activities_by_user=activities_by_user,
                assessments_by_user=assessments_by_user,
                output_path=output_path,
            )

            # Output report
            self._output_report(report, output_path)

            logger.info("Batch mode completed successfully")
            return 0

        except Exception as e:
            logger.error(f"Batch mode failed: {e}", exc_info=True)
            return 1

    def _generate_empty_report(self) -> str:
        """Generate a report when no activations are found."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        return f"""# PIM Activity Audit Report

**Generated**: {timestamp}

## Executive Summary

No PIM activations found in the specified time period.

## PIM Activations

No activations found.
"""

    def _output_report(self, report: str, output_path: Optional[Path]) -> None:
        """
        Output report to file or stdout.

        Args:
            report: Report content
            output_path: Optional path to output file
        """
        if output_path:
            logger.info(f"Report written to: {output_path}")
        else:
            # Print to stdout
            print("\n" + "=" * 80)
            print(report)
            print("=" * 80 + "\n")
