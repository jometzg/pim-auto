"""Configuration management (stub)."""

from typing import Any, Dict


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    return {
        "azure_openai_endpoint": "",
        "azure_openai_deployment": "",
        "log_analytics_workspace_id": "",
    }
