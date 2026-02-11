"""Health check endpoint for monitoring and orchestration."""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from azure.core.credentials import TokenCredential

logger = logging.getLogger(__name__)


class HealthCheck:
    """Health check functionality for the application."""

    def __init__(
        self,
        workspace_id: str,
        credential: TokenCredential,
        openai_endpoint: str,
    ):
        """
        Initialize health check.

        Args:
            workspace_id: Log Analytics workspace ID
            credential: Azure credential for authentication
            openai_endpoint: Azure OpenAI endpoint
        """
        self.workspace_id = workspace_id
        self.credential = credential
        self.openai_endpoint = openai_endpoint
        self.startup_time = datetime.utcnow()

    def check_health(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Perform health check.

        Args:
            detailed: Whether to include detailed component checks

        Returns:
            Health check result dictionary
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.startup_time).total_seconds(),
        }

        if detailed:
            health_status["components"] = self._check_components()
            
            # Overall status is unhealthy if any component is unhealthy
            component_statuses = [
                comp["status"] for comp in health_status["components"].values()
            ]
            if "unhealthy" in component_statuses:
                health_status["status"] = "unhealthy"
            elif "degraded" in component_statuses:
                health_status["status"] = "degraded"

        return health_status

    def _check_components(self) -> Dict[str, Dict[str, Any]]:
        """
        Check health of individual components.

        Returns:
            Dictionary of component health statuses
        """
        components = {}

        # Check Azure credential
        components["authentication"] = self._check_authentication()

        # Check Log Analytics configuration
        components["log_analytics"] = self._check_log_analytics()

        # Check OpenAI configuration
        components["openai"] = self._check_openai()

        return components

    def _check_authentication(self) -> Dict[str, Any]:
        """Check Azure authentication."""
        try:
            # Attempt to get a token (doesn't actually call service)
            # This validates the credential is properly configured
            token = self.credential.get_token(
                "https://api.loganalytics.io/.default"
            )
            if token and token.token:
                return {
                    "status": "healthy",
                    "message": "Azure authentication configured",
                }
            else:
                return {
                    "status": "degraded",
                    "message": "Token obtained but appears invalid",
                }
        except Exception as e:
            logger.warning(f"Authentication check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Authentication failed: {str(e)}",
            }

    def _check_log_analytics(self) -> Dict[str, Any]:
        """Check Log Analytics configuration."""
        if not self.workspace_id:
            return {
                "status": "unhealthy",
                "message": "Workspace ID not configured",
            }

        # Validate workspace ID format (GUID)
        if len(self.workspace_id) != 36 or self.workspace_id.count("-") != 4:
            return {
                "status": "unhealthy",
                "message": "Invalid workspace ID format",
            }

        return {
            "status": "healthy",
            "message": "Log Analytics configured",
            "workspace_id": self.workspace_id[:8] + "...",  # Partial ID for security
        }

    def _check_openai(self) -> Dict[str, Any]:
        """Check Azure OpenAI configuration."""
        if not self.openai_endpoint:
            return {
                "status": "unhealthy",
                "message": "OpenAI endpoint not configured",
            }

        if not self.openai_endpoint.startswith("https://"):
            return {
                "status": "unhealthy",
                "message": "Invalid OpenAI endpoint format",
            }

        return {
            "status": "healthy",
            "message": "Azure OpenAI configured",
            "endpoint": self.openai_endpoint.split(".")[0] + "...",  # Partial for security
        }

    def is_ready(self) -> bool:
        """
        Check if application is ready to serve requests.

        Returns:
            True if ready, False otherwise
        """
        health = self.check_health(detailed=True)
        return health["status"] in ["healthy", "degraded"]

    def is_alive(self) -> bool:
        """
        Check if application is alive (basic liveness check).

        Returns:
            Always returns True if code is executing
        """
        return True
