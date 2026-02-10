"""Shared pytest fixtures for all tests."""

from pathlib import Path
from typing import Any, Dict

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_audit_log(fixtures_dir: Path) -> Dict[str, Any]:
    """Load sample audit log data."""
    # For now, return inline data since fixture files don't exist yet
    return {
        "user": "john.doe@contoso.com",
        "timestamp": "2026-02-05T10:00:00Z",
        "reason": "need to add a storage account",
        "role": "Contributor",
        "duration": "8h",
    }


@pytest.fixture
def sample_activity_log(fixtures_dir: Path) -> Dict[str, Any]:
    """Load sample activity log data."""
    # For now, return inline data since fixture files don't exist yet
    return {
        "caller": "john.doe@contoso.com",
        "timestamp": "2026-02-05T10:30:15Z",
        "operation": "Microsoft.Resources/resourceGroups/write",
        "resourceId": "/subscriptions/sub-123/resourceGroups/rg-production",
        "status": "Succeeded",
    }


@pytest.fixture
def sample_openai_response(fixtures_dir: Path) -> Dict[str, Any]:
    """Load sample OpenAI response data."""
    # For now, return inline data since fixture files don't exist yet
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4o",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "AuditLogs | where TimeGenerated > ago(24h) | where OperationName == 'Add member to role'",
                },
                "finish_reason": "stop",
            }
        ],
    }
