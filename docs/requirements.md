# Azure PIM Activity Audit Agent - Requirements

## Overview
The Azure PIM Activity Audit Agent is an intelligent monitoring tool that scans Azure Log Analytics for Privileged Identity Management (PIM) activations and correlates user activity during elevation periods. The agent uses Azure AI Foundry (OpenAI) to dynamically generate and self-correct Kusto queries, providing an adaptive and resilient approach to log analysis.

## Core Requirements

### 1. PIM Activation Detection
- **Requirement**: Scan Azure Log Analytics AuditLogs table for PIM activation events
- **Details**:
  - Query the last 24 hours by default
  - Filter for operations where `OperationName` contains "PIM activation"
  - Identify completed activations (success or failure) vs. requests
  - Extract user principal names from TargetResources JSON
  - Distinguish between self-authorized and admin-authorized activations
  - Track activation windows using CorrelationId to match request/completion/expiration events

### 2. Intelligent Query Generation
- **Requirement**: Use Azure AI Foundry (OpenAI) to generate Kusto queries dynamically
- **Details**:
  - Generate appropriate Kusto queries based on natural language task descriptions
  - Embed schema information in prompts (AuditLogs and AzureActivity table structures)
  - Return only executable query code without markdown formatting
  - Support query generation for both PIM activations and user activity tracking

### 3. Self-Correcting Query Execution
- **Requirement**: Automatically detect and fix failed Kusto queries
- **Details**:
  - Retry failed queries up to 3 attempts
  - Use AI to analyze error messages and generate corrected queries
  - Handle semantic errors (e.g., invalid column names, syntax errors)
  - Provide clear feedback about query generation and fix attempts
  - Gracefully handle cases where queries cannot be fixed after max attempts

### 4. User Activity Correlation
- **Requirement**: Track Azure resource changes made by PIM-elevated users
- **Details**:
  - Query AzureActivity table for actions by elevated users
  - Use the `Caller` column to filter by user principal name
  - Query within the specific activation time window (activation start to expiration)
  - Default to 8-hour window if no expiration event is found
  - The timespan of events to look at needs to be defined by the timespan of the PIM activation window
  - Capture: TimeGenerated, ResourceGroup, ResourceProvider, ResourceId, ActivityStatusValue, OperationNameValue
 
### 5. Assess Alignment with PIM Request
- **Requirement**: Look at the activities and make an assessment whether these align with the PIM request reason
- **Details**:
- The PIM request has a structured reason which includes an Action field used to help assess alignment
- The PIM request has a subscription id too and this will also be used to assess alignment
- The alignment result should be:
- full alignment
- partial alignment (for cases where the assessment is that the user did activities in addition to the core reason)
- no alignment

### 6. Alert for no or partial alignment
- **Requirement**: Generate an alert to an action group when alignment is judged to have failed.
- **Details**:
- Create an action group in Log Analytics that will be the vehicle for alerts
- Generate programmatically an alert when the assessment is not fully aligned.

### 5. Interactive Chat Interface
- **Requirement**: Provide a CLI chat interface for interactive querying
- **Details**:
  - Support `scan` command to list PIM-elevated users (shows activations only, not activities)
  - Display activation details: user, activation time, duration, reason, and approver
  - Allow follow-up questions about specific users (e.g., "What did user@domain.com do?")
  - Only query AzureActivity table when user asks about specific user activities
  - Support arbitrary natural language questions about logs
  - Display results in readable format (tables for general queries, formatted lists for activities)
  - Maintain session context to reference previous scan results
  - Track conversation history (last 3 exchanges) for context-aware responses
  - Support pronouns (\"they\", \"them\", \"their\", \"the user\") to refer to current user in conversation
  - Allow querying any user's activities without requiring PIM scan first
  - Support `exit` command to quit

### 6. Batch Mode Operation
- **Requirement**: Support non-interactive batch mode for automated scanning
- **Details**:
  - Run with `--mode batch` argument
  - Execute 24-hour PIM scan and display results
  - Exit automatically after displaying results
  - Suitable for scheduled execution or CI/CD pipelines
  - can also do the whole flow of looking for PIM requests, and for each of these users checking activity and alignment and then alert of the assessment is out of alignment
  - must be able to make sure that the activities and assessment are per PIM request user and not all up across n-users
  - the batch mode needs to be able to accept a prompt via configuration that defines the above
 
## Non-functional Requirements

### 1. Authentication & Security
- **Requirement**: Use DefaultAzureCredential for all Azure service authentication
- **Details**:
  - Authenticate to Azure OpenAI using managed identity or Azure CLI credentials
  - Authenticate to Log Analytics workspace using same credential
  - Support multiple credential types (managed identity, Azure CLI, environment variables)
  - Require appropriate RBAC roles:
    - "Cognitive Services OpenAI User" on Azure OpenAI resource
    - "Log Analytics Reader" or equivalent on Log Analytics workspace

### 2. Configuration Management
- **Requirement**: Support environment-based configuration
- **Details**:
  - Load configuration from `.env` file using python-dotenv
  - Required environment variables:
    - `AZURE_OPENAI_ENDPOINT`: Azure OpenAI service endpoint URL
    - `LOG_ANALYTICS_WORKSPACE_ID`: Log Analytics workspace GUID
  - Optional environment variables:
    - `AZURE_OPENAI_DEPLOYMENT`: OpenAI deployment name (defaults to "gpt-4")
  - Validate required variables at startup and exit with clear error messages

### 3. Report Generation
- **Requirement**: Generate markdown-formatted reports of PIM activity
- **Details**:
  - Display PIM-elevated users with activation details
  - Show requestor, activation time, self-authorization status, and reason
  - List all Azure resource changes during elevation period
  - Format activity with timestamps, operations, resources, and status
  - Include report generation timestamp
  - Support both console output and exportable format

### 4. Testing & Quality
- **Requirement**: Provide unit tests for core functionality
- **Details**:
  - Mock Azure SDK calls for isolated testing
  - Test PIM activation query logic
  - Test user activity query logic
  - Test markdown report generation
  - Verify handling of empty result sets
  - Test datetime parsing for multiple formats

## Technical Requirements

### Programming Language
- Python 3.11 or higher
- Use python virtual environments for dependency management
- use Azure AI Foundry (OpenAI) for intelligent query generation and self-correction
- use AI Foundry Agent framework for agent orchestration and conversation management

### Key Dependencies
- `azure-identity`: DefaultAzureCredential authentication
- `azure-monitor-query`: Log Analytics querying
- `python-dotenv`: Environment variable management
- `pytest`: Unit testing framework

### Architecture Principles
1. **Agent-based**: The system should operate autonomously, generating and refining queries without hardcoded logic
2. **Resilient**: Handle errors gracefully with retry logic and clear error messages
3. **Contextual**: Maintain session state to support follow-up questions
4. **Extensible**: Design to easily add new query types or data sources
5. **Secure**: Never expose credentials; use Azure managed identities where possible

## User Workflows

### Workflow 1: Interactive Investigation
1. User launches agent in chat mode (default)
2. User types `scan` to detect PIM activations
3. Agent displays list of elevated users with time windows
4. User asks "What did user@domain.com do?"
5. Agent queries and displays activity during elevation window
6. User asks follow-up questions as needed
7. User types `exit` to quit

### Workflow 2: Automated Monitoring
1. Schedule agent to run in batch mode (e.g., cron, Azure DevOps pipeline)
2. Agent scans last 24 hours for PIM activations
3. Agent displays list of elevated users and activities
4. Output can be captured and sent to monitoring/alerting systems

### Workflow 3: Ad-hoc Analysis
1. User launches agent in chat mode
2. User asks arbitrary questions about logs (e.g., "Show all failed operations in the last hour")
3. Agent generates appropriate Kusto query
4. Agent executes query and displays results
5. User refines questions based on results


## Future Enhancements (Out of Scope)
- Web-based UI
- Integration with Azure Security Center
- Historical trending and analytics
- Custom alerting rules
- Multi-workspace support
- Export to CSV/JSON formats
- Scheduled report generation
- Integration with Azure SRE Agent
