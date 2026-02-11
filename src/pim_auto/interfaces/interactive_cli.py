"""Interactive CLI for PIM activity audit."""
import logging
import sys
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from pim_auto.azure.log_analytics import LogAnalyticsClient
from pim_auto.azure.openai_client import OpenAIClient
from pim_auto.config import Config
from pim_auto.core.activity_correlator import ActivityCorrelator
from pim_auto.core.pim_detector import PIMActivation, PIMDetector
from pim_auto.core.query_generator import QueryGenerator
from pim_auto.core.risk_assessor import RiskAssessor
from pim_auto.reporting.markdown_generator import MarkdownGenerator

logger = logging.getLogger(__name__)


class InteractiveCLI:
    """Interactive command-line interface for PIM activity audit."""

    def __init__(
        self,
        log_analytics: LogAnalyticsClient,
        openai_client: OpenAIClient,
        config: Config,
    ):
        """
        Initialize interactive CLI.

        Args:
            log_analytics: Log Analytics client
            openai_client: OpenAI client
            config: Application configuration
        """
        self.log_analytics = log_analytics
        self.openai_client = openai_client
        self.config = config
        self.console = Console()
        self.pim_detector = PIMDetector(log_analytics)
        self.activity_correlator = ActivityCorrelator(log_analytics)
        self.risk_assessor = RiskAssessor(openai_client)
        self.query_generator = QueryGenerator(openai_client)
        self.markdown_generator = MarkdownGenerator()

        # Conversation context
        self.activations: list[PIMActivation] = []
        self.current_user: Optional[str] = None

    def run(self) -> int:
        """
        Run interactive CLI loop.

        Returns:
            Exit code (0 for success)
        """
        self._print_welcome()

        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]>[/bold cyan]").strip()

                if not user_input:
                    continue

                # Handle exit commands
                if user_input.lower() in ["exit", "quit", "q"]:
                    self._print_goodbye()
                    return 0

                # Handle scan command
                if user_input.lower() == "scan":
                    self._handle_scan()
                    continue

                # Handle "assess" command or natural language questions
                if user_input.lower().startswith("assess"):
                    self._handle_assess(user_input)
                    continue

                # Handle natural language queries
                if "what did" in user_input.lower() or "activities" in user_input.lower():
                    self._handle_activity_query(user_input)
                    continue

                if "align" in user_input.lower() or "assessment" in user_input.lower():
                    self._handle_alignment_query(user_input)
                    continue

                # Try general natural language query
                self._handle_general_query(user_input)

            except KeyboardInterrupt:
                self._print_goodbye()
                return 0
            except Exception as e:
                logger.error(f"Error handling input: {e}", exc_info=True)
                self.console.print(f"[red]Error: {e}[/red]")

    def _print_welcome(self) -> None:
        """Print welcome message."""
        welcome_text = """[bold cyan]🤖 PIM Activity Audit Agent[/bold cyan]

Type 'scan' to detect PIM activations, ask questions, or 'exit' to quit.

[bold]Example commands:[/bold]
  • [cyan]scan[/cyan] - Scan for recent PIM activations
  • [cyan]What did user@example.com do?[/cyan] - View user activities
  • [cyan]assess user@example.com[/cyan] - Assess alignment
  • [cyan]exit[/cyan] - Exit the application"""

        self.console.print(Panel(welcome_text, border_style="cyan"))

    def _print_goodbye(self) -> None:
        """Print goodbye message."""
        self.console.print("\n[bold cyan]👋 Goodbye![/bold cyan]\n")

    def _handle_scan(self) -> None:
        """Handle scan command."""
        hours = self.config.default_scan_hours
        self.console.print(
            f"[bold]📊 Scanning for PIM activations in last {hours} hours...[/bold]\n"
        )

        try:
            self.activations = self.pim_detector.detect_activations(hours=hours)

            if not self.activations:
                self.console.print("[yellow]No PIM activations found.[/yellow]")
                return

            # Display results in a table
            table = Table(title=f"Found {len(self.activations)} elevated user(s)")
            table.add_column("#", style="cyan", width=4)
            table.add_column("User", style="green")
            table.add_column("Reason", style="white")
            table.add_column("Time", style="yellow")

            for i, activation in enumerate(self.activations, 1):
                time_ago = self._format_time_ago(activation.activation_time)
                table.add_row(
                    str(i),
                    activation.user_email,
                    activation.activation_reason,
                    time_ago,
                )

            self.console.print(table)

        except Exception as e:
            logger.error(f"Scan failed: {e}", exc_info=True)
            self.console.print(f"[red]Scan failed: {e}[/red]")

    def _handle_activity_query(self, query: str) -> None:
        """
        Handle queries about user activities.

        Args:
            query: User query string
        """
        # Extract user email from query
        user_email = self._extract_user_email(query)

        if not user_email:
            self.console.print(
                "[yellow]Please specify a user email. Example: 'What did user@example.com do?'[/yellow]"
            )
            return

        # Find activation for this user
        activation = self._find_activation_by_user(user_email)
        if not activation:
            self.console.print(
                f"[yellow]No PIM activation found for {user_email}. Run 'scan' first.[/yellow]"
            )
            return

        self.current_user = user_email
        self.console.print(
            f"\n[bold]📋 Activities for {user_email} during elevation:[/bold]\n"
        )

        try:
            # Get activities
            end_time = datetime.now()
            activities = self.activity_correlator.get_user_activities(
                user_email=user_email,
                start_time=activation.activation_time,
                end_time=end_time,
            )

            if not activities:
                self.console.print("[yellow]No activities found.[/yellow]")
                return

            # Display activities
            for activity in activities:
                time_str = activity.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                self.console.print(
                    f"[cyan][{time_str}][/cyan] {activity.operation_name} - {activity.resource_name}"
                )

        except Exception as e:
            logger.error(f"Failed to get activities: {e}", exc_info=True)
            self.console.print(f"[red]Failed to get activities: {e}[/red]")

    def _handle_alignment_query(self, query: str) -> None:
        """
        Handle queries about alignment assessment.

        Args:
            query: User query string
        """
        # Extract user email from query
        user_email = self._extract_user_email(query)

        # If no user specified, use current user from context
        if not user_email and self.current_user:
            user_email = self.current_user

        if not user_email:
            self.console.print(
                "[yellow]Please specify a user or query activities first.[/yellow]"
            )
            return

        # Find activation for this user
        activation = self._find_activation_by_user(user_email)
        if not activation:
            self.console.print(
                f"[yellow]No PIM activation found for {user_email}. Run 'scan' first.[/yellow]"
            )
            return

        self.console.print(f"\n[bold]🔍 Assessing alignment for {user_email}...[/bold]\n")

        try:
            # Get activities
            end_time = datetime.now()
            activities = self.activity_correlator.get_user_activities(
                user_email=user_email,
                start_time=activation.activation_time,
                end_time=end_time,
            )

            # Assess alignment
            assessment = self.risk_assessor.assess_alignment(
                pim_reason=activation.activation_reason,
                activities=activities,
            )

            # Format and display assessment
            formatted = self.markdown_generator.format_assessment(assessment)
            self.console.print(formatted)

        except Exception as e:
            logger.error(f"Assessment failed: {e}", exc_info=True)
            self.console.print(f"[red]Assessment failed: {e}[/red]")

    def _handle_assess(self, command: str) -> None:
        """
        Handle assess command.

        Args:
            command: Full command string
        """
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            # Assess all users
            self._assess_all_users()
        else:
            # Assess specific user
            user_email = parts[1].strip()
            self._handle_alignment_query(f"assess {user_email}")

    def _assess_all_users(self) -> None:
        """Assess alignment for all scanned users."""
        if not self.activations:
            self.console.print(
                "[yellow]No activations to assess. Run 'scan' first.[/yellow]"
            )
            return

        for activation in self.activations:
            self.console.print(
                f"\n[bold]🔍 Assessing {activation.user_email}...[/bold]"
            )

            try:
                end_time = datetime.now()
                activities = self.activity_correlator.get_user_activities(
                    user_email=activation.user_email,
                    start_time=activation.activation_time,
                    end_time=end_time,
                )

                assessment = self.risk_assessor.assess_alignment(
                    pim_reason=activation.activation_reason,
                    activities=activities,
                )

                formatted = self.markdown_generator.format_assessment(assessment)
                self.console.print(formatted)

            except Exception as e:
                logger.error(f"Assessment failed for {activation.user_email}: {e}")
                self.console.print(f"[red]Assessment failed: {e}[/red]")

    def _handle_general_query(self, query: str) -> None:
        """
        Handle general natural language query.

        Args:
            query: User query string
        """
        self.console.print(
            "[yellow]I can help you with:[/yellow]\n"
            "  • [cyan]scan[/cyan] - Detect PIM activations\n"
            "  • [cyan]What did user@example.com do?[/cyan] - View activities\n"
            "  • [cyan]assess user@example.com[/cyan] - Assess alignment\n"
        )

    def _extract_user_email(self, text: str) -> Optional[str]:
        """
        Extract user email from text.

        Args:
            text: Input text

        Returns:
            User email if found, None otherwise
        """
        # Simple extraction - look for email pattern
        import re

        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        match = re.search(email_pattern, text)
        return match.group(0) if match else None

    def _find_activation_by_user(self, user_email: str) -> Optional[PIMActivation]:
        """
        Find activation for a specific user.

        Args:
            user_email: User email to search for

        Returns:
            PIMActivation if found, None otherwise
        """
        for activation in self.activations:
            if activation.user_email.lower() == user_email.lower():
                return activation
        return None

    def _format_time_ago(self, timestamp: datetime) -> str:
        """
        Format timestamp as relative time.

        Args:
            timestamp: Timestamp to format

        Returns:
            Formatted string like "2 hours ago"
        """
        now = datetime.now()
        diff = now - timestamp
        hours = int(diff.total_seconds() / 3600)
        if hours == 0:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
