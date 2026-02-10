"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "azure_openai_endpoint": "https://test.openai.azure.com/",
        "azure_openai_deployment": "gpt-4o",
        "log_analytics_workspace_id": "test-workspace-id",
    }
