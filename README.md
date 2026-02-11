# Azure PIM Activity Audit Agent

An intelligent monitoring tool that scans Azure Log Analytics for Privileged Identity Management (PIM) activations and correlates user activity during elevation periods using Azure AI Foundry. 

The agent then evaluates whether the activities performed on Azure during the PIM activation period for each user fully, partially or do not align with the reason the user gave for the PIM activation. 

If the PIM activation reason is not aligned with the activities performed during the elevation period, the agent will generate a report that can be used for further investigation. This report can then be sent via an Azure Monitor Action Group.

## Features

- 🔍 **PIM Activation Detection**: Automatically scans Azure Log Analytics for privilege elevations
- 🤖 **AI-Powered Query Generation**: Uses Azure OpenAI to dynamically generate Kusto queries
- 🔄 **Self-Correcting Queries**: Automatically fixes failed queries with AI assistance
- 💬 **Interactive Chat Interface**: Natural language querying with context awareness
- 📊 **Activity Correlation**: Tracks all Azure resource changes during elevation periods
- 📈 **Risk Assessment**: Evaluates activity alignment with stated PIM activation reasons
- 📝 **Markdown Reports**: Generates detailed reports of PIM activity
- 🔐 **Secure Authentication**: Uses Azure DefaultAzureCredential (managed identity, Azure CLI)
- ⚡ **Batch Mode**: Non-interactive mode for automated monitoring

## Non-Functional Requirements
1. The application must be developed in Python 3.11 or higher.
2. The application must use Azure OpenAI service for natural language processing and query generation.
3. The application must authenticate securely using Azure DefaultAzureCredential, supporting both managed identities and Azure CLI authentication methods.
4. The application must be able to handle and log errors gracefully, providing meaningful feedback to the user.
5. The application must be designed to run both interactively (chat mode) and non-interactively (batch mode) for flexibility in different operational contexts.
6. The application must generate reports in Markdown format for easy readability and integration with other tools.
7. The application must be modular and maintainable, allowing for easy updates and enhancements in the future.
8. The application must be able to handle multiple concurrent users in interactive mode without performance degradation.
9. The application must be tested thoroughly to ensure reliability and correctness of the PIM activity detection and correlation logic.
10. The application must be documented clearly, including setup instructions, usage examples, and troubleshooting tips for users of varying technical expertise.

## Prerequisites

- Python 3.11 or higher
- Azure OpenAI service with GPT-4o deployment
- Log Analytics workspace with AuditLogs and AzureActivity tables
- Azure CLI (for local development)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jometzg/pim-auto.git
   cd pim-auto
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install the package with dependencies**:
   ```bash
   pip install -e .[dev]
   ```

4. **Configure environment variables**:
   
   Create a `.env` file or set environment variables:
   ```bash
   # Linux/Mac
   export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
   export AZURE_OPENAI_DEPLOYMENT="gpt-4o"
   export AZURE_OPENAI_API_VERSION="2024-02-15-preview"
   export LOG_ANALYTICS_WORKSPACE_ID="your-workspace-id"
   ```
   
   Or for Windows PowerShell:
   ```powershell
   $env:AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
   $env:AZURE_OPENAI_DEPLOYMENT = "gpt-4o"
   $env:AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
   $env:LOG_ANALYTICS_WORKSPACE_ID = "your-workspace-id"
   ```

5. **Authenticate with Azure**:
   ```bash
   az login
   az account show
   ```

## CLI Options

The application supports several command-line options:

```bash
python -m pim_auto.main [OPTIONS]
```

**Options:**
- `--mode [interactive|batch]` - Run mode (default: interactive)
- `--log-level [DEBUG|INFO|WARNING|ERROR]` - Logging level (default: INFO)
- `--output PATH` - Output file path for batch mode report
- `--hours INTEGER` - Number of hours to scan (overrides config default)

**Examples:**
```bash
# Interactive mode with debug logging
python -m pim_auto.main --log-level DEBUG

# Batch mode with custom scan window and output file
python -m pim_auto.main --mode batch --hours 48 --output report.md

# Quick scan with info logging
python -m pim_auto.main --hours 12
```

## Usage Examples

### Interactive Chat Mode

```
🤖 PIM Activity Audit Agent
Type 'scan' to detect PIM activations, ask questions, or 'exit' to quit.

> scan
📊 Scanning for PIM activations in last 24 hours...

Found 2 elevated users:
1. john.doe@contoso.com. Reason "need to add a storage account"(activated 2 hours ago)
2. jane.smith@contoso.com Reason "need to add an NSG rule"(activated 5 hours ago)

> What did john.doe@contoso.com do?
📋 Activities for john.doe@contoso.com during elevation:

[2026-02-05 10:30:15] Microsoft.Resources/deployments/write
  Resource: rg-production | RG: rg-production | Provider: Microsoft.Resources
  Subscription: abc123-def456-ghi789

[2026-02-05 10:35:22] Microsoft.Web/sites/write
  Resource: app-web-prod | RG: rg-production | Provider: Microsoft.Web
  Subscription: abc123-def456-ghi789

[2026-02-05 11:15:08] Microsoft.Network/networkSecurityGroups/write
  Resource: nsg-prod | RG: rg-production | Provider: Microsoft.Network
  Subscription: abc123-def456-ghi789

> do their activity align with the reason they gave for activation?

1. john.doe@contoso.com activities do not align with the reason for activation. The user created a resource group and deployed an App Service, which is not related to adding a storage account. This may warrant further investigation.

> exit
👋 Goodbye!
```

### Batch Mode

```bash
python -m pim_auto.main --mode batch --output pim-report.md
```

Output includes:
- List of all PIM activations in last 24 hours
- Complete activity timeline for each elevated user (successful operations only)
- Resource details including subscription, resource group, and provider
- Markdown-formatted report suitable for logging/alerting

**Note**: Activity queries filter for successful operations only (`ActivityStatusValue == "Success"`) to focus on completed actions.

