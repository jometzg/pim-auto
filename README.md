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

[2026-02-05 10:30:15] Created resource group 'rg-production'
[2026-02-05 10:35:22] Deployed App Service 'app-web-prod'
[2026-02-05 11:15:08] Modified Network Security Group rules

> do their activity align with the reason they gave for activation?

1. john.doe@contoso.com activities do not align with the reason for activation. The user created a resource group and deployed an App Service, which is not related to adding a storage account. This may warrant further investigation.

> exit
👋 Goodbye!
```

### Batch Mode

```bash
python main.py --mode batch
```

Output includes:
- List of all PIM activations in last 24 hours
- Complete activity timeline for each elevated user
- Markdown-formatted report suitable for logging/alerting

