"""Configuration management for PIM Auto."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application configuration."""

    # Required fields (no defaults)
    azure_openai_endpoint: str
    azure_openai_deployment: str
    log_analytics_workspace_id: str

    # Optional fields (with defaults)
    azure_openai_api_version: str = "2024-02-15-preview"
    log_analytics_region: Optional[str] = None
    default_scan_hours: int = 24
    log_level: str = "INFO"
    batch_output_path: Optional[str] = None

    # Monitoring settings
    enable_app_insights: bool = True
    app_insights_connection_string: Optional[str] = None
    structured_logging: bool = False  # JSON format logging

    @classmethod
    def from_environment(cls) -> "Config":
        """Load configuration from environment variables."""
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT",
            "LOG_ANALYTICS_WORKSPACE_ID",
        ]

        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        return cls(
            azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            azure_openai_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", ""),
            log_analytics_workspace_id=os.getenv("LOG_ANALYTICS_WORKSPACE_ID", ""),
            azure_openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            log_analytics_region=os.getenv("LOG_ANALYTICS_REGION"),
            default_scan_hours=int(os.getenv("DEFAULT_SCAN_HOURS", "24")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            batch_output_path=os.getenv("BATCH_OUTPUT_PATH"),
            enable_app_insights=os.getenv("ENABLE_APP_INSIGHTS", "true").lower() == "true",
            app_insights_connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"),
            structured_logging=os.getenv("STRUCTURED_LOGGING", "false").lower() == "true",
        )

    def validate(self) -> None:
        """Validate configuration values."""
        if not self.azure_openai_endpoint.startswith("https://"):
            raise ValueError("Azure OpenAI endpoint must start with https://")

        if self.default_scan_hours < 1 or self.default_scan_hours > 168:
            raise ValueError("Default scan hours must be between 1 and 168 (1 week)")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {self.log_level}")
