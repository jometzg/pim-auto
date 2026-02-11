"""Tests for configuration module."""

import pytest

from src.pim_auto.config import Config


def test_config_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading configuration from environment variables."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
    monkeypatch.setenv("LOG_ANALYTICS_WORKSPACE_ID", "test-workspace-id")

    config = Config.from_environment()

    assert config.azure_openai_endpoint == "https://test.openai.azure.com"
    assert config.azure_openai_deployment == "gpt-4"
    assert config.log_analytics_workspace_id == "test-workspace-id"
    assert config.default_scan_hours == 24
    assert config.log_level == "INFO"


def test_config_with_optional_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test configuration with optional environment variables."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
    monkeypatch.setenv("LOG_ANALYTICS_WORKSPACE_ID", "test-workspace-id")
    monkeypatch.setenv("DEFAULT_SCAN_HOURS", "48")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("BATCH_OUTPUT_PATH", "/tmp/output")

    config = Config.from_environment()

    assert config.default_scan_hours == 48
    assert config.log_level == "DEBUG"
    assert config.batch_output_path == "/tmp/output"


def test_config_missing_required_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that missing required variables raise an error."""
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)
    monkeypatch.delenv("LOG_ANALYTICS_WORKSPACE_ID", raising=False)

    with pytest.raises(ValueError, match="Missing required environment variables"):
        Config.from_environment()


def test_config_validation_endpoint() -> None:
    """Test endpoint validation."""
    config = Config(
        azure_openai_endpoint="http://invalid.com",
        azure_openai_deployment="gpt-4",
        log_analytics_workspace_id="test-id",
    )

    with pytest.raises(ValueError, match="must start with https://"):
        config.validate()


def test_config_validation_scan_hours() -> None:
    """Test scan hours validation."""
    config = Config(
        azure_openai_endpoint="https://test.openai.azure.com",
        azure_openai_deployment="gpt-4",
        log_analytics_workspace_id="test-id",
        default_scan_hours=200,
    )

    with pytest.raises(ValueError, match="must be between 1 and 168"):
        config.validate()


def test_config_validation_log_level() -> None:
    """Test log level validation."""
    config = Config(
        azure_openai_endpoint="https://test.openai.azure.com",
        azure_openai_deployment="gpt-4",
        log_analytics_workspace_id="test-id",
        log_level="INVALID",
    )

    with pytest.raises(ValueError, match="Invalid log level"):
        config.validate()


def test_config_validation_success() -> None:
    """Test successful validation."""
    config = Config(
        azure_openai_endpoint="https://test.openai.azure.com",
        azure_openai_deployment="gpt-4",
        log_analytics_workspace_id="test-id",
    )

    # Should not raise
    config.validate()
