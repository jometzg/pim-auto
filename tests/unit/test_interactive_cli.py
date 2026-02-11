"""Unit tests for interactive CLI."""
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from pim_auto.config import Config
from pim_auto.core.activity_correlator import ActivityEvent
from pim_auto.core.pim_detector import PIMActivation
from pim_auto.core.risk_assessor import AlignmentLevel, RiskAssessment
from pim_auto.interfaces.interactive_cli import InteractiveCLI


@pytest.fixture
def mock_log_analytics():
    """Create mock Log Analytics client."""
    return Mock()


@pytest.fixture
def mock_openai_client():
    """Create mock OpenAI client."""
    return Mock()


@pytest.fixture
def mock_config():
    """Create mock config."""
    config = Mock(spec=Config)
    config.default_scan_hours = 24
    return config


@pytest.fixture
def cli(mock_log_analytics, mock_openai_client, mock_config):
    """Create interactive CLI instance."""
    return InteractiveCLI(mock_log_analytics, mock_openai_client, mock_config)


@pytest.fixture
def sample_activations():
    """Create sample PIM activations."""
    return [
        PIMActivation(
            user_email="user1@example.com",
            role_name="Contributor",
            activation_reason="Add storage account",
            activation_time=datetime(2026, 2, 11, 10, 0, 0),
            duration_hours=24,
        )
    ]


@pytest.fixture
def sample_activities():
    """Create sample activity events."""
    return [
        ActivityEvent(
            timestamp=datetime(2026, 2, 11, 10, 30, 0),
            operation_name="Create Storage Account",
            resource_name="storage123",
            resource_type="Microsoft.Storage/storageAccounts",
            status="Success",
        )
    ]


@pytest.fixture
def sample_assessment():
    """Create sample risk assessment."""
    return RiskAssessment(
        level=AlignmentLevel.ALIGNED,
        explanation="User created storage account as stated.",
    )


def test_cli_initialization(cli, mock_log_analytics, mock_openai_client, mock_config):
    """Test CLI initialization."""
    assert cli.log_analytics == mock_log_analytics
    assert cli.openai_client == mock_openai_client
    assert cli.config == mock_config
    assert cli.console is not None
    assert cli.activations == []
    assert cli.current_user is None


def test_extract_user_email_valid(cli):
    """Test extracting valid user email from text."""
    text = "What did john.doe@example.com do?"
    email = cli._extract_user_email(text)
    assert email == "john.doe@example.com"


def test_extract_user_email_invalid(cli):
    """Test extracting email from text without email."""
    text = "What did the user do?"
    email = cli._extract_user_email(text)
    assert email is None


def test_find_activation_by_user_found(cli, sample_activations):
    """Test finding activation by user email."""
    cli.activations = sample_activations
    activation = cli._find_activation_by_user("user1@example.com")
    assert activation is not None
    assert activation.user_email == "user1@example.com"


def test_find_activation_by_user_not_found(cli, sample_activations):
    """Test finding activation when user not found."""
    cli.activations = sample_activations
    activation = cli._find_activation_by_user("notfound@example.com")
    assert activation is None


def test_find_activation_by_user_case_insensitive(cli, sample_activations):
    """Test finding activation is case insensitive."""
    cli.activations = sample_activations
    activation = cli._find_activation_by_user("USER1@EXAMPLE.COM")
    assert activation is not None
    assert activation.user_email == "user1@example.com"


def test_format_time_ago_hours(cli):
    """Test formatting time ago in hours."""
    now = datetime.now()
    timestamp = datetime(now.year, now.month, now.day, now.hour - 2, 0, 0)
    result = cli._format_time_ago(timestamp)
    assert "hour" in result
    assert "ago" in result


def test_format_time_ago_minutes(cli):
    """Test formatting time ago in minutes for recent times."""
    # Create a timestamp very close to now
    from datetime import timedelta
    now = datetime.now()
    timestamp = now - timedelta(minutes=30)
    result = cli._format_time_ago(timestamp)
    assert "minute" in result or "hour" in result
    assert "ago" in result


def test_handle_scan_with_activations(cli, sample_activations):
    """Test handling scan command with activations found."""
    cli.pim_detector.detect_activations = Mock(return_value=sample_activations)

    cli._handle_scan()

    assert cli.activations == sample_activations
    cli.pim_detector.detect_activations.assert_called_once_with(hours=24)


def test_handle_scan_no_activations(cli):
    """Test handling scan command with no activations."""
    cli.pim_detector.detect_activations = Mock(return_value=[])

    cli._handle_scan()

    assert cli.activations == []


def test_handle_scan_exception(cli):
    """Test handling scan command with exception."""
    cli.pim_detector.detect_activations = Mock(side_effect=Exception("Test error"))

    # Should not raise, just log error
    cli._handle_scan()


def test_handle_activity_query_without_email(cli):
    """Test handling activity query without user email."""
    cli._handle_activity_query("What did the user do?")
    # Should handle gracefully and show message


def test_handle_activity_query_user_not_found(cli):
    """Test handling activity query for user not in activations."""
    cli.activations = []
    cli._handle_activity_query("What did user@example.com do?")
    # Should handle gracefully


def test_handle_activity_query_success(cli, sample_activations, sample_activities):
    """Test successful activity query."""
    cli.activations = sample_activations
    cli.activity_correlator.get_user_activities = Mock(return_value=sample_activities)

    cli._handle_activity_query("What did user1@example.com do?")

    cli.activity_correlator.get_user_activities.assert_called_once()


def test_handle_alignment_query_without_user(cli):
    """Test handling alignment query without user."""
    cli.current_user = None
    cli._handle_alignment_query("assess alignment")
    # Should handle gracefully


def test_handle_alignment_query_with_context(cli, sample_activations, sample_activities, sample_assessment):
    """Test alignment query using context from previous query."""
    cli.activations = sample_activations
    cli.current_user = "user1@example.com"
    cli.activity_correlator.get_user_activities = Mock(return_value=sample_activities)
    cli.risk_assessor.assess_alignment = Mock(return_value=sample_assessment)

    cli._handle_alignment_query("do their activities align?")

    cli.activity_correlator.get_user_activities.assert_called_once()
    cli.risk_assessor.assess_alignment.assert_called_once()


def test_handle_alignment_query_explicit_user(cli, sample_activations, sample_activities, sample_assessment):
    """Test alignment query with explicit user email."""
    cli.activations = sample_activations
    cli.activity_correlator.get_user_activities = Mock(return_value=sample_activities)
    cli.risk_assessor.assess_alignment = Mock(return_value=sample_assessment)

    cli._handle_alignment_query("assess user1@example.com")

    cli.risk_assessor.assess_alignment.assert_called_once()


def test_handle_assess_all_users(cli, sample_activations, sample_activities, sample_assessment):
    """Test assessing all users."""
    cli.activations = sample_activations
    cli.activity_correlator.get_user_activities = Mock(return_value=sample_activities)
    cli.risk_assessor.assess_alignment = Mock(return_value=sample_assessment)

    cli._assess_all_users()

    # Should assess each activation
    assert cli.activity_correlator.get_user_activities.call_count == len(sample_activations)
    assert cli.risk_assessor.assess_alignment.call_count == len(sample_activations)


def test_handle_assess_no_activations(cli):
    """Test assess command with no activations."""
    cli.activations = []
    cli._assess_all_users()
    # Should handle gracefully


def test_handle_assess_continues_on_error(cli):
    """Test that assess continues even if one user fails."""
    activations = [
        PIMActivation(
            user_email="user1@example.com",
            role_name="Contributor",
            activation_reason="Test",
            activation_time=datetime(2026, 2, 11, 10, 0, 0),
            duration_hours=24,
        ),
        PIMActivation(
            user_email="user2@example.com",
            role_name="Owner",
            activation_reason="Test2",
            activation_time=datetime(2026, 2, 11, 11, 0, 0),
            duration_hours=24,
        ),
    ]

    cli.activations = activations
    cli.activity_correlator.get_user_activities = Mock(
        side_effect=[Exception("Error"), []]
    )

    # Should not raise, continue processing
    cli._assess_all_users()


def test_run_exit_command(cli):
    """Test running CLI with exit command."""
    with patch.object(cli.console, "print"):
        with patch("rich.prompt.Prompt.ask", side_effect=["exit"]):
            result = cli.run()

    assert result == 0


def test_run_keyboard_interrupt(cli):
    """Test handling keyboard interrupt."""
    with patch.object(cli.console, "print"):
        with patch("rich.prompt.Prompt.ask", side_effect=KeyboardInterrupt()):
            result = cli.run()

    assert result == 0


def test_handle_assess_command_with_user(cli, sample_activations, sample_activities, sample_assessment):
    """Test assess command with specific user."""
    cli.activations = sample_activations
    cli.activity_correlator.get_user_activities = Mock(return_value=sample_activities)
    cli.risk_assessor.assess_alignment = Mock(return_value=sample_assessment)

    cli._handle_assess("assess user1@example.com")

    cli.risk_assessor.assess_alignment.assert_called_once()


def test_handle_assess_command_all(cli, sample_activations, sample_activities, sample_assessment):
    """Test assess command without user (assess all)."""
    cli.activations = sample_activations
    cli.activity_correlator.get_user_activities = Mock(return_value=sample_activities)
    cli.risk_assessor.assess_alignment = Mock(return_value=sample_assessment)

    cli._handle_assess("assess")

    assert cli.risk_assessor.assess_alignment.call_count == len(sample_activations)
