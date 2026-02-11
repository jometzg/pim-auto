"""Tests for Azure authentication module."""
from unittest.mock import MagicMock, patch

from azure.identity import DefaultAzureCredential

from src.pim_auto.azure.auth import get_azure_credential


@patch("src.pim_auto.azure.auth.DefaultAzureCredential")
def test_get_azure_credential(mock_credential_class: MagicMock) -> None:
    """Test getting Azure credential."""
    mock_instance = MagicMock(spec=DefaultAzureCredential)
    mock_credential_class.return_value = mock_instance

    credential = get_azure_credential()

    assert credential == mock_instance
    mock_credential_class.assert_called_once()
