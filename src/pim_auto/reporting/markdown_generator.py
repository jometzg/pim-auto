"""Markdown report generator for PIM Auto application."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from pim_auto.core.activity_correlator import ActivityEvent
from pim_auto.core.pim_detector import PIMActivation
from pim_auto.core.risk_assessor import AlignmentLevel, RiskAssessment

logger = logging.getLogger(__name__)


class MarkdownGenerator:
    """Generates Markdown-formatted reports for PIM activity analysis."""

    def generate_report(
        self,
        activations: list[PIMActivation],
        activities_by_user: dict[str, list[ActivityEvent]],
        assessments_by_user: dict[str, RiskAssessment],
        output_path: Optional[Path] = None,
    ) -> str:
        """
        Generate a comprehensive Markdown report.

        Args:
            activations: List of PIM activations
            activities_by_user: Dictionary mapping user emails to their activities
            assessments_by_user: Dictionary mapping user emails to risk assessments
            output_path: Optional path to write report file

        Returns:
            Generated markdown content as string
        """
        logger.info(f"Generating markdown report for {len(activations)} activations")

        sections = [
            self._generate_header(),
            self._generate_summary(activations, assessments_by_user),
            self._generate_activations_table(activations),
            self._generate_detailed_analysis(
                activations, activities_by_user, assessments_by_user
            ),
        ]

        report = "\n\n".join(sections)

        if output_path:
            logger.info(f"Writing report to {output_path}")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report)

        return report

    def _generate_header(self) -> str:
        """Generate report header."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        return f"# PIM Activity Audit Report\n\n**Generated**: {timestamp}"

    def _generate_summary(
        self,
        activations: list[PIMActivation],
        assessments_by_user: dict[str, RiskAssessment],
    ) -> str:
        """Generate executive summary."""
        total = len(activations)
        aligned = sum(
            1
            for a in assessments_by_user.values()
            if a.level == AlignmentLevel.ALIGNED
        )
        partially_aligned = sum(
            1
            for a in assessments_by_user.values()
            if a.level == AlignmentLevel.PARTIALLY_ALIGNED
        )
        not_aligned = sum(
            1
            for a in assessments_by_user.values()
            if a.level == AlignmentLevel.NOT_ALIGNED
        )
        unknown = sum(
            1
            for a in assessments_by_user.values()
            if a.level == AlignmentLevel.UNKNOWN
        )

        return f"""## Executive Summary

- **Total PIM Activations**: {total}
- **Aligned**: {aligned} ✅
- **Partially Aligned**: {partially_aligned} ⚠️
- **Not Aligned**: {not_aligned} ❌
- **Unknown**: {unknown} ❓"""

    def _generate_activations_table(self, activations: list[PIMActivation]) -> str:
        """Generate table of PIM activations."""
        if not activations:
            return "## PIM Activations\n\nNo activations found."

        lines = [
            "## PIM Activations",
            "",
            "| User | Role | Activation Time | Reason |",
            "|------|------|----------------|--------|",
        ]

        for activation in activations:
            time_str = activation.activation_time.strftime("%Y-%m-%d %H:%M:%S")
            lines.append(
                f"| {activation.user_email} | {activation.role_name} | {time_str} | {activation.activation_reason} |"
            )

        return "\n".join(lines)

    def _generate_detailed_analysis(
        self,
        activations: list[PIMActivation],
        activities_by_user: dict[str, list[ActivityEvent]],
        assessments_by_user: dict[str, RiskAssessment],
    ) -> str:
        """Generate detailed analysis for each user."""
        sections = ["## Detailed Analysis"]

        for activation in activations:
            user_email = activation.user_email
            activities = activities_by_user.get(user_email, [])
            assessment = assessments_by_user.get(user_email)

            sections.append(self._generate_user_section(activation, activities, assessment))

        return "\n\n".join(sections)

    def _generate_user_section(
        self,
        activation: PIMActivation,
        activities: list[ActivityEvent],
        assessment: Optional[RiskAssessment],
    ) -> str:
        """Generate detailed section for a single user."""
        lines = [
            f"### {activation.user_email}",
            "",
            f"**Role**: {activation.role_name}",
            f"**Activation Time**: {activation.activation_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Reason**: {activation.activation_reason}",
            "",
        ]

        # Activities section
        lines.append("**Activities**:")
        lines.append("")
        if activities:
            for activity in activities:
                time_str = activity.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                lines.append(f"- `{time_str}` {activity.operation_name} - {activity.resource_name}")
        else:
            lines.append("No activities found.")

        lines.append("")

        # Assessment section
        if assessment:
            alignment_emoji = self._get_alignment_emoji(assessment.level)
            lines.append(f"**Assessment**: {assessment.level.value} {alignment_emoji}")
            lines.append("")
            lines.append(f"**Explanation**: {assessment.explanation}")
        else:
            lines.append("**Assessment**: Not available")

        return "\n".join(lines)

    def _get_alignment_emoji(self, level: AlignmentLevel) -> str:
        """Get emoji for alignment level."""
        emoji_map = {
            AlignmentLevel.ALIGNED: "✅",
            AlignmentLevel.PARTIALLY_ALIGNED: "⚠️",
            AlignmentLevel.NOT_ALIGNED: "❌",
            AlignmentLevel.UNKNOWN: "❓",
        }
        return emoji_map.get(level, "")

    def format_activations_summary(self, activations: list[PIMActivation]) -> str:
        """
        Format a brief summary of activations for console output.

        Args:
            activations: List of PIM activations

        Returns:
            Formatted summary string
        """
        if not activations:
            return "No PIM activations found."

        lines = [f"Found {len(activations)} elevated user(s):"]
        for i, activation in enumerate(activations, 1):
            # Calculate time ago
            now = datetime.now()
            time_diff = now - activation.activation_time
            hours_ago = int(time_diff.total_seconds() / 3600)

            lines.append(
                f"{i}. {activation.user_email} - Reason: \"{activation.activation_reason}\" "
                f"(activated {hours_ago} hours ago)"
            )

        return "\n".join(lines)

    def format_activities(self, activities: list[ActivityEvent]) -> str:
        """
        Format activities for console output.

        Args:
            activities: List of activity events

        Returns:
            Formatted activities string
        """
        if not activities:
            return "No activities found."

        lines = []
        for activity in activities:
            time_str = activity.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"[{time_str}] {activity.operation_name} - {activity.resource_name}")

        return "\n".join(lines)

    def format_assessment(self, assessment: RiskAssessment) -> str:
        """
        Format risk assessment for console output.

        Args:
            assessment: Risk assessment object

        Returns:
            Formatted assessment string
        """
        emoji = self._get_alignment_emoji(assessment.level)
        return f"{assessment.level.value} {emoji}\n\n{assessment.explanation}"
