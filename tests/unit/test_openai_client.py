"""Tests for Azure OpenAI client module."""

from unittest.mock import Mock

import pytest

from src.pim_auto.azure.openai_client import OpenAIClient


@pytest.fixture
def mock_credential() -> Mock:
    """Mock Azure credential."""
    return Mock()


def test_openai_client_init(
        mock_credential: Mock,
        monkeypatch: pytest.MonkeyPatch
        ) -> None:
    """Test OpenAI client initialization."""
    mock_token_provider = Mock()
    mock_get_token_provider = Mock(return_value=mock_token_provider)
    monkeypatch.setattr(
        "src.pim_auto.azure.openai_client.get_bearer_token_provider",
        mock_get_token_provider,
    )

    mock_azure_openai = Mock()
    monkeypatch.setattr(
        "src.pim_auto.azure.openai_client.AzureOpenAI",
        mock_azure_openai,
    )

    client = OpenAIClient(
        endpoint="https://test.openai.azure.com",
        deployment="gpt-4",
        api_version="2024-02-15-preview",
        credential=mock_credential,
    )

    assert client.deployment == "gpt-4"
    mock_get_token_provider.assert_called_once_with(
        mock_credential, "https://cognitiveservices.azure.com/.default"
    )


def test_generate_completion_success(
    mock_credential: Mock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test successful completion generation."""
    # Mock response
    mock_message = Mock()
    mock_message.content = "Generated response"

    mock_choice = Mock()
    mock_choice.message = mock_message

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    # Mock OpenAI client
    mock_client_instance = Mock()
    mock_client_instance.chat.completions.create.return_value = mock_response

    mock_token_provider = Mock()
    mock_get_token_provider = Mock(return_value=mock_token_provider)
    monkeypatch.setattr(
        "src.pim_auto.azure.openai_client.get_bearer_token_provider",
        mock_get_token_provider,
    )

    mock_azure_openai = Mock(return_value=mock_client_instance)
    monkeypatch.setattr(
        "src.pim_auto.azure.openai_client.AzureOpenAI",
        mock_azure_openai
    )

    client = OpenAIClient(
        endpoint="https://test.openai.azure.com",
        deployment="gpt-4",
        api_version="2024-02-15-preview",
        credential=mock_credential,
    )

    messages = [{"role": "user", "content": "test message"}]
    result = client.generate_completion(
        messages,
        temperature=0.7,
        max_tokens=2000
    )

    assert result == "Generated response"
    mock_client_instance.chat.completions.create.assert_called_once_with(
        model="gpt-4", messages=messages, temperature=0.7, max_tokens=2000
    )


def test_generate_completion_exception(
    mock_credential: Mock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test completion generation with exception."""
    mock_client_instance = Mock()
    mock_client_instance.chat.completions.create.side_effect = (
        Exception("API Error")
    )

    mock_token_provider = Mock()
    mock_get_token_provider = Mock(return_value=mock_token_provider)
    monkeypatch.setattr(
        "src.pim_auto.azure.openai_client.get_bearer_token_provider",
        mock_get_token_provider,
    )

    mock_azure_openai = Mock(return_value=mock_client_instance)
    monkeypatch.setattr(
        "src.pim_auto.azure.openai_client.AzureOpenAI",
        mock_azure_openai
    )

    client = OpenAIClient(
        endpoint="https://test.openai.azure.com",
        deployment="gpt-4",
        api_version="2024-02-15-preview",
        credential=mock_credential,
    )

    messages = [{"role": "user", "content": "test message"}]

    with pytest.raises(Exception, match="API Error"):
        client.generate_completion(messages)
