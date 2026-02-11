"""Tests for query generator module."""

from unittest.mock import Mock

import pytest

from src.pim_auto.core.query_generator import QueryGenerator


@pytest.fixture
def mock_openai() -> Mock:
    """Mock OpenAI client."""
    return Mock()


def test_generate_query_success(mock_openai: Mock) -> None:
    """Test successful query generation."""
    mock_openai.generate_completion.return_value = """
    AuditLogs
    | where TimeGenerated > ago(24h)
    | where OperationName == "Add member to role completed (PIM activation)"
    """

    generator = QueryGenerator(mock_openai)
    query = generator.generate_query("Find PIM activations in the last 24 hours")

    assert "AuditLogs" in query
    assert "where" in query
    mock_openai.generate_completion.assert_called_once()


def test_generate_query_with_azure_activity(mock_openai: Mock) -> None:
    """Test query generation with AzureActivity table."""
    mock_openai.generate_completion.return_value = """
    AzureActivity
    | where TimeGenerated > ago(1h)
    | where Caller == "user@example.com"
    """

    generator = QueryGenerator(mock_openai)
    query = generator.generate_query("Find activities for user@example.com")

    assert "AzureActivity" in query


def test_generate_query_retry_on_invalid(mock_openai: Mock) -> None:
    """Test query generation retries on invalid response."""
    mock_openai.generate_completion.side_effect = [
        "This is not a valid KQL query",  # First attempt fails
        "AuditLogs | where TimeGenerated > ago(24h)",  # Second attempt succeeds
    ]

    generator = QueryGenerator(mock_openai)
    query = generator.generate_query("test", max_retries=2)

    assert "AuditLogs" in query
    assert mock_openai.generate_completion.call_count == 2


def test_generate_query_failure_after_retries(mock_openai: Mock) -> None:
    """Test query generation fails after max retries."""
    mock_openai.generate_completion.return_value = "Invalid response"

    generator = QueryGenerator(mock_openai)

    with pytest.raises(ValueError, match="Failed to generate valid query"):
        generator.generate_query("test", max_retries=2)


def test_generate_query_exception_handling(mock_openai: Mock) -> None:
    """Test query generation handles exceptions."""
    mock_openai.generate_completion.side_effect = Exception("API Error")

    generator = QueryGenerator(mock_openai)

    with pytest.raises(Exception, match="API Error"):
        generator.generate_query("test", max_retries=0)


def test_generate_query_temperature(mock_openai: Mock) -> None:
    """Test that query generation uses lower temperature."""
    mock_openai.generate_completion.return_value = (
        "AuditLogs | where TimeGenerated > ago(24h)"
    )

    generator = QueryGenerator(mock_openai)
    generator.generate_query("test")

    call_args = mock_openai.generate_completion.call_args
    assert call_args.kwargs["temperature"] == 0.3
