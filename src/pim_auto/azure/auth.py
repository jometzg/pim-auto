"""Azure authentication management."""
from azure.identity import DefaultAzureCredential


def get_azure_credential() -> DefaultAzureCredential:
    """Get Azure credential using DefaultAzureCredential chain."""
    return DefaultAzureCredential()
