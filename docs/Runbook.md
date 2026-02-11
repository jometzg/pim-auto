# Runbook - PIM Auto

**Document Status**: Current State (As-Is)  
**Last Updated**: 2026-02-10  
**Repository**: jometzg/pim-auto

## Overview

This runbook provides operational instructions for the pim-auto repository in its **current state**. Since no application code exists yet, this document focuses on repository operations and documents what will be needed once implementation begins.

---

## Current State Operations

### Repository Access

**Clone the repository**:
```bash
git clone https://github.com/jometzg/pim-auto.git
cd pim-auto
```

**Check repository status**:
```bash
git status
git log --oneline -10
```

**Current branches**:
```bash
git branch -a
```

### View Documentation

**Read the specification**:
```bash
cat README.md
# Or open in your preferred editor/viewer
```

**View agent configurations**:
```bash
ls -la .github/agents/
cat .github/agents/documentation.agent.md
```

**View skill procedures**:
```bash
ls -la .github/skills/
cat .github/skills/system-discovery.skill.md
```

### Check for Updates

```bash
git fetch origin
git log --oneline HEAD..origin/main  # View new commits
git pull origin main                  # Update local copy
```

---

## Future State Operations (Once Implementation Exists)

The following sections document the **expected** build, test, and run procedures based on the README.md specification. These commands will only work once the Python application is implemented.

### Prerequisites

Before running the application, ensure you have:

1. **Python 3.11 or higher**:
   ```bash
   python --version  # Should show 3.11 or higher
   # Or
   python3 --version
   ```

2. **Azure CLI** (for local development):
   ```bash
   az --version
   ```

3. **Azure Authentication**:
   ```bash
   # Login to Azure
   az login
   
   # Verify login
   az account show
   ```

4. **Azure Resources**:
   - Azure OpenAI service with GPT-4o deployment
   - Log Analytics workspace with AuditLogs and AzureActivity tables
   - Appropriate RBAC permissions:
     - Log Analytics Reader (minimum)
     - OpenAI User or Contributor

### Installation

**Create Python virtual environment**:
```bash
# Create venv
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
.\venv\Scripts\activate
```

**Install dependencies**:
```bash
# Install package with all dependencies (including dev dependencies)
pip install -e .[dev]

# Or for production-only dependencies
pip install -e .
```

**Verify installation**:
```bash
pip list
# Should show azure-identity, azure-monitor-query, openai, click, rich, etc.
```

### Configuration

**Set environment variables** (expected, not yet defined):

```bash
# Azure OpenAI configuration
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="gpt-4o"  # Your deployment name
export AZURE_OPENAI_API_VERSION="2024-02-15-preview"  # Or latest

# Log Analytics configuration
export LOG_ANALYTICS_WORKSPACE_ID="your-workspace-id"

# Optional: Override default scan window
export PIM_SCAN_HOURS=24  # Default: 24 hours
```

**Verify configuration**:
```bash

Or for Windows PowerShell:
```powershell
# Azure OpenAI configuration
$env:AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
$env:AZURE_OPENAI_DEPLOYMENT = "gpt-4o"  # Your deployment name
$env:AZURE_OPENAI_API_VERSION = "2024-02-15-preview"  # Or latest

# Log Analytics configuration
$env:LOG_ANALYTICS_WORKSPACE_ID = "your-workspace-id"

# Optional: Override default scan window
$env:PIM_SCAN_HOURS = "24"  # Default: 24 hours
```

# Check environment variables are set
env | grep AZURE
env | grep LOG_ANALYTICS
```

### Running the Application

#### Interactive Chat Mode (Default)

```bash
python -m pim_auto.main
```

**With logging options**:
```bash
# Debug logging (shows all Azure queries and authentication details)
python -m pim_auto.main --log-level DEBUG

# Info logging (default - recommended for normal use)
python -m pim_auto.main --log-level INFO

# Custom scan window
python -m pim_auto.main --hours 48
```

Expected behavior:
- Launches interactive CLI
- Displays: "🤖 PIM Activity Audit Agent"
- Waits for user input

**Sample session**:
```
$ python -m pim_auto.main
🤖 PIM Activity Audit Agent
Type 'scan' to detect PIM activations, ask questions, or 'exit' to quit.

> scan
📊 Scanning for PIM activations in last 24 hours...
Found 2 elevated users:
1. john.doe@contoso.com. Reason "need to add a storage account"(activated 2 hours ago)
2. jane.smith@contoso.com Reason "need to add an NSG rule"(activated 5 hours ago)

> What did john.doe@contoso.com do?
📋 Activities for john.doe@contoso.com during elevation:

[2026-02-11 10:30:15] Microsoft.Storage/storageAccounts/write
  Resource: stprod001 | RG: rg-production | Provider: Microsoft.Storage
  Subscription: abc123-def456-ghi789

[2026-02-11 10:35:22] Microsoft.Storage/storageAccounts/blobServices/containers/write
  Resource: stprod001/default/data | RG: rg-production | Provider: Microsoft.Storage
  Subscription: abc123-def456-ghi789

> exit
👋 Goodbye!
```

#### Batch Mode

```bash
python -m pim_auto.main --mode batch
```

**With options**:
```bash
# Custom output file
python -m pim_auto.main --mode batch --output pim-report.md

# Custom scan window (48 hours)
python -m pim_auto.main --mode batch --hours 48 --output report-48h.md

# Debug logging for troubleshooting
python -m pim_auto.main --mode batch --log-level DEBUG
```

Expected behavior:
- Runs non-interactively
- Scans last 24 hours (or specified hours)
- Queries only successful Azure operations (ActivityStatusValue == "Success")
- Generates Markdown report with detailed resource information
- Exits with status code (0 = success, 1 = failure)

**Capture output**:
```bash
python -m pim_auto.main --mode batch --output pim-report-$(date +%Y%m%d).md
```

**Schedule with cron** (Linux/Mac):
```bash
# Add to crontab: Run daily at 6 AM
0 6 * * * cd /path/to/pim-auto && /path/to/.venv/bin/python -m pim_auto.main --mode batch --output /var/log/pim-auto-$(date +\%Y\%m\%d).md 2>&1
```

### Testing

**Run unit tests** (once test suite exists):
```bash
# If using pytest
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_pim_detector.py
```

**Run integration tests**:
```bash
# Integration tests may require Azure resources
pytest tests/integration/ --azure-integration
```

**Run linters and formatters**:
```bash
# Black (code formatting)
black --check src/

# flake8 (linting)
flake8 src/

# mypy (type checking)
mypy src/
```

### Operational Notes

#### Azure Activity Query Behavior

**Activity Filtering**:
- AzureActivity queries filter for `ActivityStatusValue == "Success"` only
- This focuses on completed operations and excludes failed attempts
- Provides clearer picture of actual changes made during PIM elevation

**Activity Details Collected**:
- Operation name (e.g., `Microsoft.Storage/storageAccounts/write`)
- Resource name
- Resource group
- Resource provider (e.g., `Microsoft.Storage`, `Microsoft.Network`)
- Subscription ID
- Timestamp

**Query Timespan**:
- Activities are queried from PIM activation time to current time
- For batch mode, uses the configured scan hours (default: 24)
- The Azure SDK requires a timespan parameter; it defaults to 24 hours if not specified

#### Log Levels

Use `--log-level` flag to control verbosity:

- **DEBUG**: Shows all Azure SDK internals, authentication attempts, raw queries, and query results. Use for troubleshooting.
- **INFO** (default): Shows application flow, PIM detections, and activity counts. Recommended for normal use.
- **WARNING**: Only shows warnings and errors. Use in production when logs are centralized.
- **ERROR**: Only critical errors. Use when you only care about failures.

Example DEBUG output includes:
- Authentication chain attempts (managed identity, Azure CLI, etc.)
- KQL queries sent to Log Analytics
- Number of rows returned from queries
- HTTP request details

### Troubleshooting

#### Issue: "Python version too old"

**Symptom**: Error message about Python version
**Solution**: Install Python 3.11 or higher
```bash
# Check version
python --version

# Install Python 3.11+ via your package manager or python.org
```

#### Issue: "Azure authentication failed"

**Symptom**: `DefaultAzureCredential` cannot authenticate

**Solutions**:

1. **For local development**: Login via Azure CLI
   ```bash
   az login
   az account show  # Verify
   ```

2. **For production (Managed Identity)**: 
   - Ensure the Azure resource (VM, Function App, etc.) has managed identity enabled
   - Grant identity appropriate RBAC roles
   - No code changes needed

3. **Check permissions**:
   ```bash
   # Verify you have access to Log Analytics
   az monitor log-analytics workspace show --resource-group <rg> --workspace-name <name>
   ```

#### Issue: "Azure OpenAI quota exceeded"

**Symptom**: Rate limit or quota errors from Azure OpenAI

**Solutions**:
1. Check Azure OpenAI quota in Azure Portal
2. Request quota increase via Azure support
3. Reduce query frequency in batch mode
4. Implement retry logic with exponential backoff (if not already present)

#### Issue: "No PIM activations found"

**Symptom**: Scan returns zero results even though PIM is in use

**Possible causes**:
1. Time range too narrow (try increasing from 24 hours)
2. Log Analytics workspace not receiving AuditLogs
3. Query syntax error (check application logs)
4. Insufficient permissions to read AuditLogs

**Debugging**:
```bash
# Manually query Log Analytics to verify data
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "AuditLogs | where TimeGenerated > ago(24h) | take 10" \
  --output table
```

#### Issue: "No activities found for user"

**Symptom**: PIM activation detected but "No activities found" when querying user actions

**Possible causes**:
1. User performed no successful operations (all attempts failed)
   - Activities are filtered for `ActivityStatusValue == "Success"` only
2. Log Analytics workspace not receiving AzureActivity logs
3. User's operations not yet synced to Log Analytics (5-10 min delay possible)
4. Caller field in AzureActivity doesn't match user's email format

**Debugging**:
```bash
# Check if AzureActivity data exists for the user
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "AzureActivity | where Caller == 'user@domain.com' | where TimeGenerated > ago(24h) | project TimeGenerated, OperationName, ActivityStatusValue | take 20" \
  --output table

# Check all status values (including failures)
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "AzureActivity | where Caller == 'user@domain.com' | where TimeGenerated > ago(24h) | summarize count() by ActivityStatusValue" \
  --output table
```

**Solutions**:
1. Wait 10-15 minutes after PIM activation for logs to sync
2. Verify AzureActivity logs are being collected in Log Analytics workspace
3. If user had failed operations, they won't appear (by design - we focus on successful changes)

#### Issue: "Application hangs in interactive mode"

**Symptom**: No response to user input

**Solutions**:
1. Check Azure OpenAI service availability
2. Verify network connectivity to Azure endpoints
3. Check application logs for errors
4. Try batch mode to isolate interactive UI issues

### Logging

**Console logging with different levels**:

```bash
# Debug output (verbose - all queries, auth details, results)
python -m pim_auto.main --log-level DEBUG

# Info output (default - normal operations)
python -m pim_auto.main --log-level INFO

# Warning only (minimal output)
python -m pim_auto.main --log-level WARNING

# Errors only
python -m pim_auto.main --log-level ERROR
```

**Redirect to file**:
```bash
# Redirect all output to file
python -m pim_auto.main --log-level DEBUG > app.log 2>&1

# Redirect batch mode output
python -m pim_auto.main --mode batch --output report.md 2>&1 | tee batch.log
```

**View logs**:
```bash
tail -f app.log

# Or if using journalctl (systemd)
journalctl -u pim-auto -f
```

### Performance Monitoring

**Key metrics to monitor** (once application runs):

1. **Azure OpenAI**:
   - Token usage per request
   - Request latency
   - Rate limit hits

2. **Log Analytics**:
   - Query execution time
   - Data scanned (GB)
   - Failed queries

3. **Application**:
   - PIM activations detected per scan
   - Activities per user
   - Report generation time

**Monitoring commands**:
```bash
# View Azure OpenAI metrics
az monitor metrics list \
  --resource <openai-resource-id> \
  --metric "Token Usage" \
  --start-time <timestamp> \
  --end-time <timestamp>
```

---

## Known Limitations

### Current State

1. **No Application Code**: Repository contains only specification and governance infrastructure
2. **No Dependencies Defined**: No requirements.txt or pyproject.toml exists
3. **No Tests**: No test suite to validate functionality
4. **No CI/CD Pipeline**: While ci.yml exists, its functionality is unknown
5. **No Configuration Management**: No documented approach for environment-specific settings

### Specified Limitations (from README)

1. **Azure Dependency**: Cannot run without Azure subscription and services
2. **PIM-Specific**: Only monitors Azure AD PIM, not applicable to other identity systems
3. **24-Hour Default**: Default scan window is 24 hours (may miss older activations)
4. **No Real-Time**: Batch mode runs on schedule, not real-time streaming
5. **English Language**: Specification examples in English, localization not mentioned

---

## Technical Debt

### Current Repository

1. **Missing Project Structure**: No src/, tests/, docs/ directories (now partially resolved with docs/)
2. **No Dependency Management**: No Python package configuration
3. **No License**: No LICENSE file present
4. **No Contributing Guide**: No CONTRIBUTING.md for external contributors
5. **No Issue Templates**: No GitHub issue templates for bug reports or features
6. **No PR Templates**: No pull request template
7. **No .gitignore**: No Python .gitignore file (will need for __pycache__, venv/, etc.)

### Future Technical Debt (to avoid during implementation)

1. **Hardcoded Configuration**: Avoid hardcoding Azure endpoints, use environment variables
2. **Missing Error Handling**: Ensure graceful degradation for Azure service failures
3. **No Retry Logic**: Implement exponential backoff for transient failures
4. **No Input Validation**: Validate user queries in interactive mode
5. **No Rate Limiting**: Implement client-side rate limiting for Azure APIs

---

## Recovery Procedures

### Current State

**Repository corruption**:
```bash
# Re-clone from GitHub
rm -rf pim-auto
git clone https://github.com/jometzg/pim-auto.git
```

### Future State

**Application failure recovery** (once deployed):

1. **Restart application**:
   ```bash
   # If running as systemd service
   sudo systemctl restart pim-auto
   
   # If running in container
   docker restart pim-auto
   
   # If running as Azure Function
   az functionapp restart --name <function-name> --resource-group <rg>
   ```

2. **Clear cache** (if implemented):
   ```bash
   rm -rf ~/.pim-auto/cache/*
   ```

3. **Re-authenticate**:
   ```bash
   az logout
   az login
   ```

4. **Rollback deployment**:
   ```bash
   # Revert to previous commit
   git revert <commit-hash>
   git push
   
   # Redeploy
   # [deployment commands TBD]
   ```

---

## Deployment (Future State)

### Local Development Deployment

```bash
# Already covered in "Running the Application" section
python main.py
```

### Production Deployment Options

**Option 1: Azure Function** (recommended for batch mode):
```bash
# Create Function App
az functionapp create \
  --resource-group <rg> \
  --name <function-name> \
  --consumption-plan-location <location> \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux

# Enable managed identity
az functionapp identity assign \
  --name <function-name> \
  --resource-group <rg>

# Deploy code (once implemented)
func azure functionapp publish <function-name>
```

**Option 2: Azure Container Instance** (for interactive or batch):
```bash
# Build container
docker build -t pim-auto:latest .

# Push to Azure Container Registry
az acr login --name <acr-name>
docker tag pim-auto:latest <acr-name>.azurecr.io/pim-auto:latest
docker push <acr-name>.azurecr.io/pim-auto:latest

# Deploy container instance with managed identity
az container create \
  --resource-group <rg> \
  --name pim-auto \
  --image <acr-name>.azurecr.io/pim-auto:latest \
  --assign-identity \
  --environment-variables AZURE_OPENAI_ENDPOINT=<endpoint> ...
```

**Option 3: Azure VM** (for persistent interactive mode):
```bash
# Create VM
az vm create \
  --resource-group <rg> \
  --name pim-auto-vm \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --assign-identity

# SSH to VM and install application
# [installation steps as in "Installation" section]
```

---

## Monitoring and Alerting (Future State)

### Azure Monitor Integration

**Set up alerts**:
```bash
# Create action group for notifications
az monitor action-group create \
  --name pim-auto-alerts \
  --resource-group <rg> \
  --short-name pimauto \
  --email security-team@contoso.com

# Create alert rule for failures (example)
az monitor metrics alert create \
  --name pim-auto-failure \
  --resource-group <rg> \
  --scopes <function-app-id> \
  --condition "Exceptions > 5" \
  --action pim-auto-alerts
```

### Log Analytics Queries

**Query application logs** (if ingested to Log Analytics):
```kql
// Failed batch runs
AppTraces
| where AppRoleName == "pim-auto"
| where SeverityLevel == "Error"
| where TimeGenerated > ago(24h)
| summarize count() by bin(TimeGenerated, 1h)

// PIM activations detected
AppMetrics
| where Name == "pim_activations_detected"
| where TimeGenerated > ago(7d)
| render timechart
```

---

## Backup and Restore

### Current State

**No data to backup** - repository is version-controlled via Git.

### Future State

**Configuration backup**:
```bash
# Backup environment variables
env | grep AZURE > azure-config-backup.env
env | grep LOG_ANALYTICS >> azure-config-backup.env

# Store securely (NOT in git)
# Use Azure Key Vault or similar
```

**Reports backup** (if storing historical reports):
```bash
# Archive monthly reports
mkdir -p archives/$(date +%Y-%m)
mv reports/$(date +%Y-%m)-*.md archives/$(date +%Y-%m)/
tar -czf archives/$(date +%Y-%m).tar.gz archives/$(date +%Y-%m)/
```

---

## Security Operations

### Credential Rotation

**Azure Managed Identity** (no rotation needed - Azure handles it)

**Azure CLI** (local development):
```bash
# Refresh credentials
az logout
az login
```

### Permission Audit

```bash
# Check current identity
az account show

# List role assignments
az role assignment list --assignee <identity-object-id>

# Verify minimum permissions principle
# Should have: Log Analytics Reader, OpenAI User
# Should NOT have: Contributor, Owner (unless necessary)
```

### Security Scanning

```bash
# Scan dependencies for vulnerabilities (once requirements.txt exists)
pip install safety
safety check

# Scan code for secrets
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```

---

## Support and Escalation

### Current State

- **Repository Owner**: jometzg (GitHub username)
- **Issues**: File via GitHub Issues at https://github.com/jometzg/pim-auto/issues
- **Discussions**: Use GitHub Discussions for questions

### Future State

1. **Level 1**: Check this runbook and troubleshooting section
2. **Level 2**: Review application logs and Azure service health
3. **Level 3**: Consult README.md specification and LLD.md for design details
4. **Level 4**: File GitHub issue with:
   - Python version
   - Azure service versions
   - Error logs
   - Steps to reproduce

---

## Change Management

### Current Process

1. Fork repository
2. Create feature branch
3. Submit pull request
4. Human review required (per agent governance model)
5. Merge to main

### Future Process (for deployed applications)

1. **Development**: Change in dev branch
2. **Testing**: Automated tests must pass
3. **Staging**: Deploy to staging environment
4. **Validation**: Run smoke tests
5. **Production**: Deploy to production
6. **Monitoring**: Watch for errors/alerts
7. **Rollback Plan**: Keep previous version for 24 hours

---

## Appendices

### A. Quick Reference Commands

```bash
# Clone repository
git clone https://github.com/jometzg/pim-auto.git

# Check Python version
python3 --version

# Azure login
az login

# Run interactive mode (future)
python main.py

# Run batch mode (future)
python main.py --mode batch

# View logs (future)
tail -f /var/log/pim-auto/app.log
```

### B. Environment Variables Reference

Expected environment variables:

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | `https://myopenai.openai.azure.com/` | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | Yes | `gpt-4o` | GPT-4o deployment name |
| `AZURE_OPENAI_API_VERSION` | No | `2024-02-15-preview` | API version (default shown) |
| `LOG_ANALYTICS_WORKSPACE_ID` | Yes | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | Workspace GUID |
| `DEFAULT_SCAN_HOURS` | No | `24` | Scan window in hours (default: 24) |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `STRUCTURED_LOGGING` | No | `false` | Enable JSON format logging |
| `ENABLE_APP_INSIGHTS` | No | `true` | Enable Application Insights monitoring |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | No | - | App Insights connection string |
| `AZURE_CLIENT_ID` | No | - | Managed identity client ID (for Azure deployment) |

### C. Azure RBAC Roles Reference

Required roles for the application identity:

| Role | Scope | Purpose |
|------|-------|---------|
| Log Analytics Reader | Log Analytics Workspace | Read AuditLogs and AzureActivity |
| Cognitive Services OpenAI User | Azure OpenAI resource | Generate queries and assess alignment |
| AcrPull | Container Registry | Pull container images (production deployment) |

### D. Useful Azure CLI Commands

```bash
# List Log Analytics workspaces
az monitor log-analytics workspace list --output table

# List OpenAI resources
az cognitiveservices account list --output table

# Test Log Analytics query
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "AuditLogs | take 10"

# Check managed identity
az identity show --ids <identity-resource-id>
```

---

## Production Deployment Operations

### Container Deployment (Azure Container Apps)

**Check deployment status**:
```bash
RESOURCE_GROUP="rg-pimauto-prod"
CONTAINER_APP_NAME="pimauto-prod-app"  # Adjust to your deployment

# Check app status
az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.{status:runningStatus,fqdn:configuration.ingress.fqdn}" \
  --output table

# Check revision status
az containerapp revision list \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --output table
```

**View container logs**:
```bash
# View recent logs
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --tail 50 \
  --follow

# View logs from specific revision
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --revision REVISION_NAME \
  --tail 100
```

**Restart application**:
```bash
# Restart current revision
az containerapp revision restart \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --revision REVISION_NAME
```

**Scale application**:
```bash
# Scale to specific replica count
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 1 \
  --max-replicas 3

# Scale to zero (for dev environments)
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 0 \
  --max-replicas 1
```

### Health Check Operations

**Run health check**:
```bash
# Basic health check (returns JSON)
python -m pim_auto.main --mode health

# Detailed health check (includes component status)
python -m pim_auto.main --mode health --detailed-health

# From container (using az containerapp exec)
az containerapp exec \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --command "python -m pim_auto.main --mode health --detailed-health"
```

**Expected health check output**:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-11T10:30:00",
  "uptime_seconds": 3600,
  "components": {
    "authentication": {
      "status": "healthy",
      "message": "Azure authentication configured"
    },
    "log_analytics": {
      "status": "healthy",
      "message": "Log Analytics configured",
      "workspace_id": "xxxxxxxx..."
    },
    "openai": {
      "status": "healthy",
      "message": "Azure OpenAI configured",
      "endpoint": "https://your-openai..."
    }
  }
}
```

### Monitoring with Application Insights

**Access Application Insights**:
```bash
# Get Application Insights details
APP_INSIGHTS_NAME=$(az monitor app-insights component list \
  --resource-group $RESOURCE_GROUP \
  --query "[?contains(name, 'pimauto')].name" \
  --output tsv)

# Get instrumentation key
az monitor app-insights component show \
  --app $APP_INSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey
```

**Query application logs** (using KQL):
```bash
# Run KQL query via CLI
az monitor app-insights query \
  --app $APP_INSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --analytics-query "traces | where timestamp > ago(1h) | project timestamp, message, severityLevel | order by timestamp desc | take 20"
```

**Common monitoring queries** (run in Azure Portal > Application Insights > Logs):

```kql
// View recent errors
traces
| where severityLevel >= 3  // Error and Critical
| where timestamp > ago(24h)
| project timestamp, message, severityLevel, customDimensions
| order by timestamp desc

// PIM activations detected over time
customMetrics
| where name == "pim_activations_detected"
| where timestamp > ago(7d)
| summarize sum(value) by bin(timestamp, 1h)
| render timechart

// Query performance
customMetrics
| where name == "query_duration_ms"
| where timestamp > ago(24h)
| summarize avg(value), max(value), min(value) by bin(timestamp, 1h)
| render timechart

// OpenAI API call rate
customMetrics
| where name == "openai_api_calls"
| where timestamp > ago(24h)
| summarize count() by bin(timestamp, 1h)
| render timechart

// Application health check results
traces
| where message contains "health check"
| where timestamp > ago(24h)
| project timestamp, message, severityLevel
| order by timestamp desc
```

### Alert Management

**View active alerts**:
```bash
# List all alert rules
az monitor metrics alert list \
  --resource-group $RESOURCE_GROUP \
  --output table

# Show specific alert details
az monitor metrics alert show \
  --name pimauto-high-error-rate \
  --resource-group $RESOURCE_GROUP

# View alert history (fired alerts)
az monitor activity-log list \
  --resource-group $RESOURCE_GROUP \
  --offset 7d \
  --query "[?contains(eventName.localizedValue, 'Alert')]" \
  --output table
```

**Temporarily disable alerts** (during maintenance):
```bash
# Disable error rate alert
az monitor metrics alert update \
  --name pimauto-high-error-rate \
  --resource-group $RESOURCE_GROUP \
  --enabled false

# Re-enable after maintenance
az monitor metrics alert update \
  --name pimauto-high-error-rate \
  --resource-group $RESOURCE_GROUP \
  --enabled true
```

### Structured Logging

**Enable JSON logging** (for log aggregation platforms):
```bash
# Set environment variable for JSON output
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars STRUCTURED_LOGGING=true

# Restart to apply
az containerapp revision restart \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP
```

**JSON log format**:
```json
{
  "asctime": "2026-02-11T10:30:15",
  "name": "pim_auto.core.pim_detector",
  "levelname": "INFO",
  "message": "Found 3 PIM activations in last 24 hours"
}
```

---

## Document Maintenance

This runbook should be updated when:
- Application code is implemented
- Deployment procedures change
- New Azure services are added
- Configuration requirements change
- Common issues are discovered

**Last Updated**: 2026-02-11 (Slice 3: Production Readiness)  
**Next Review**: After Slice 4 validation
