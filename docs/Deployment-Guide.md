# Deployment Guide - PIM Auto

**Document Status**: Production Ready  
**Last Updated**: 2026-02-11  
**Target Audience**: DevOps Engineers, Platform Teams

## Overview

This guide provides step-by-step instructions for deploying PIM Auto to Azure. The application is deployed as a containerized workload using Azure Container Apps with managed identity for secure authentication.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Architecture](#deployment-architecture)
3. [Initial Deployment](#initial-deployment)
4. [Application Updates](#application-updates)
5. [Environment Configuration](#environment-configuration)
6. [Monitoring Setup](#monitoring-setup)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Azure Resources

Before deploying, ensure you have:

1. **Azure Subscription** with permissions to:
   - Create resource groups
   - Deploy resources (Container Apps, Container Registry, etc.)
   - Assign RBAC roles

2. **Log Analytics Workspace** with:
   - AuditLogs table (Azure AD/Entra ID logs)
   - AzureActivity table (Azure resource activity logs)
   - Data retention configured (minimum 7 days recommended)

3. **Azure OpenAI Service** with:
   - GPT-4o model deployed
   - Endpoint URL and deployment name

4. **Tools Installed**:
   - Azure CLI (`az`) version 2.50+
   - Docker (for local image builds)
   - Git

### Required Permissions

Your Azure account needs:
- `Owner` or `Contributor` + `User Access Administrator` on the resource group
- Permission to assign RBAC roles
- Access to Azure OpenAI and Log Analytics resources

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Subscription                        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Resource Group: rg-pimauto-prod          │    │
│  │                                                     │    │
│  │  ┌──────────────────┐  ┌──────────────────┐      │    │
│  │  │ Container        │  │ Container         │      │    │
│  │  │ Registry         │→ │ App               │      │    │
│  │  │ (ACR)            │  │ (PIM Auto)        │      │    │
│  │  └──────────────────┘  └──────────────────┘      │    │
│  │                              ↓                     │    │
│  │                        ┌──────────────────┐       │    │
│  │                        │ Managed          │       │    │
│  │                        │ Identity         │       │    │
│  │                        └──────────────────┘       │    │
│  │                              ↓                     │    │
│  │  ┌──────────────────┐  ┌──────────────────┐      │    │
│  │  │ Application      │  │ Log Analytics    │      │    │
│  │  │ Insights         │  │ (App Logs)       │      │    │
│  │  └──────────────────┘  └──────────────────┘      │    │
│  │                                                    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  External Resources (existing):                             │
│  - Azure OpenAI Service                                     │
│  - Log Analytics Workspace (PIM data)                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Initial Deployment

### Step 1: Prepare Configuration

1. Clone the repository:
   ```bash
   git clone https://github.com/jometzg/pim-auto.git
   cd pim-auto
   ```

2. Navigate to infrastructure directory:
   ```bash
   cd infrastructure/bicep
   ```

3. Copy and customize parameters file:
   ```bash
   cp parameters.dev.json parameters.prod.json
   ```

4. Edit `parameters.prod.json` with your values:
   ```json
   {
     "logAnalyticsWorkspaceId": {
       "value": "YOUR_WORKSPACE_ID_GUID"
     },
     "azureOpenAIEndpoint": {
       "value": "https://your-openai.openai.azure.com/"
     },
     "azureOpenAIDeployment": {
       "value": "gpt-4o"
     },
     "environment": {
       "value": "prod"
     }
   }
   ```

### Step 2: Login to Azure

```bash
# Login
az login

# Select subscription
az account set --subscription "YOUR_SUBSCRIPTION_NAME_OR_ID"

# Verify
az account show
```

### Step 3: Create Resource Group

```bash
# Set variables
RESOURCE_GROUP="rg-pimauto-prod"
LOCATION="eastus"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 4: Deploy Infrastructure

```bash
# Validate template first (optional but recommended)
az deployment group validate \
  --resource-group $RESOURCE_GROUP \
  --template-file main.bicep \
  --parameters parameters.prod.json

# Deploy
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file main.bicep \
  --parameters parameters.prod.json \
  --name pimauto-deployment-$(date +%Y%m%d-%H%M%S)

# Note: Deployment takes 3-5 minutes
```

### Step 5: Capture Deployment Outputs

```bash
# Get deployment outputs
DEPLOYMENT_NAME=$(az deployment group list \
  --resource-group $RESOURCE_GROUP \
  --query "[0].name" \
  --output tsv)

# Container Registry
ACR_NAME=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs.containerRegistryName.value \
  --output tsv)

ACR_LOGIN_SERVER=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs.containerRegistryLoginServer.value \
  --output tsv)

# Managed Identity
MANAGED_IDENTITY_PRINCIPAL_ID=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs.managedIdentityPrincipalId.value \
  --output tsv)

# Container App
CONTAINER_APP_NAME=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs.containerAppName.value \
  --output tsv)

# Application Insights
APP_INSIGHTS_CONNECTION_STRING=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name $DEPLOYMENT_NAME \
  --query properties.outputs.appInsightsConnectionString.value \
  --output tsv)

# Save these for later use
echo "ACR_NAME=$ACR_NAME" > deployment.env
echo "ACR_LOGIN_SERVER=$ACR_LOGIN_SERVER" >> deployment.env
echo "MANAGED_IDENTITY_PRINCIPAL_ID=$MANAGED_IDENTITY_PRINCIPAL_ID" >> deployment.env
echo "CONTAINER_APP_NAME=$CONTAINER_APP_NAME" >> deployment.env
```

### Step 6: Build and Push Container Image

From the repository root:

```bash
# Option A: Use Azure Container Registry build (recommended)
az acr build \
  --registry $ACR_NAME \
  --image pimauto:latest \
  --image pimauto:v1.0.0 \
  --file Dockerfile \
  .

# Option B: Build locally and push
docker build -t $ACR_LOGIN_SERVER/pimauto:latest .
az acr login --name $ACR_NAME
docker push $ACR_LOGIN_SERVER/pimauto:latest
```

### Step 7: Configure Azure OpenAI Access

Grant the managed identity access to Azure OpenAI:

```bash
# Get your Azure OpenAI resource ID
OPENAI_RESOURCE_ID=$(az cognitiveservices account show \
  --name YOUR_OPENAI_RESOURCE_NAME \
  --resource-group YOUR_OPENAI_RESOURCE_GROUP \
  --query id \
  --output tsv)

# Assign Cognitive Services OpenAI User role
az role assignment create \
  --assignee $MANAGED_IDENTITY_PRINCIPAL_ID \
  --role "Cognitive Services OpenAI User" \
  --scope $OPENAI_RESOURCE_ID

# Verify assignment
az role assignment list \
  --assignee $MANAGED_IDENTITY_PRINCIPAL_ID \
  --output table
```

### Step 8: Verify Deployment

```bash
# Check container app status
az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.runningStatus

# Check health
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --tail 20

# Test health endpoint (if ingress is enabled)
FQDN=$(az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

# Note: Ingress is internal by default, so this may not work externally
```

---

## Application Updates

### Update Container Image

1. **Build new image**:
   ```bash
   # Tag with version
   VERSION="v1.1.0"
   
   az acr build \
     --registry $ACR_NAME \
     --image pimauto:$VERSION \
     --image pimauto:latest \
     --file Dockerfile \
     .
   ```

2. **Update container app**:
   ```bash
   az containerapp update \
     --name $CONTAINER_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --image $ACR_LOGIN_SERVER/pimauto:$VERSION
   ```

3. **Verify update**:
   ```bash
   az containerapp revision list \
     --name $CONTAINER_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --output table
   ```

### Rollback to Previous Version

```bash
# List revisions
az containerapp revision list \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --output table

# Activate previous revision
az containerapp revision activate \
  --revision PREVIOUS_REVISION_NAME \
  --resource-group $RESOURCE_GROUP
```

---

## Environment Configuration

### Environment Variables

The application is configured via environment variables in the Bicep template. To update:

1. Edit `main.bicep` or use Azure CLI:
   ```bash
   az containerapp update \
     --name $CONTAINER_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --set-env-vars \
       LOG_LEVEL=WARNING \
       DEFAULT_SCAN_HOURS=48
   ```

### Supported Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | - | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | Yes | - | GPT-4o deployment name |
| `AZURE_OPENAI_API_VERSION` | No | `2024-02-15-preview` | API version |
| `LOG_ANALYTICS_WORKSPACE_ID` | Yes | - | Log Analytics workspace GUID |
| `DEFAULT_SCAN_HOURS` | No | `24` | Default scan window in hours |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `STRUCTURED_LOGGING` | No | `false` | Enable JSON logging |
| `ENABLE_APP_INSIGHTS` | No | `true` | Enable Application Insights |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Auto | - | App Insights connection (set by deployment) |

---

## Monitoring Setup

### Application Insights Dashboard

1. Navigate to Application Insights in Azure Portal
2. View **Live Metrics** for real-time monitoring
3. Create custom queries in **Logs**:
   ```kql
   traces
   | where timestamp > ago(1h)
   | where severityLevel >= 2  // Warning and above
   | project timestamp, message, severityLevel
   | order by timestamp desc
   ```

### Custom Metrics

The application exports custom metrics:
- `pim_activations_detected` - Number of PIM activations found
- `user_activities_found` - Activities per user
- `query_duration_ms` - Query performance
- `openai_api_calls` - OpenAI API usage

Query metrics:
```kql
customMetrics
| where name in ("pim_activations_detected", "query_duration_ms")
| summarize avg(value), max(value), min(value) by name, bin(timestamp, 1h)
| render timechart
```

### Alerts

Set up alerts for critical conditions:

```bash
# Alert on errors
az monitor metrics alert create \
  --name pimauto-error-alert \
  --resource-group $RESOURCE_GROUP \
  --scopes /subscriptions/YOUR_SUB/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Insights/components/APP_INSIGHTS_NAME \
  --condition "count traces > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action "/subscriptions/YOUR_SUB/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/YOUR_ACTION_GROUP"
```

---

## Troubleshooting

### Container Won't Start

1. **Check logs**:
   ```bash
   az containerapp logs show \
     --name $CONTAINER_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --tail 100 \
     --follow
   ```

2. **Check replica status**:
   ```bash
   az containerapp replica list \
     --name $CONTAINER_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --output table
   ```

3. **Common issues**:
   - Missing environment variables (check configuration)
   - Invalid Azure OpenAI endpoint
   - Managed identity lacks permissions

### Authentication Failures

1. **Verify managed identity**:
   ```bash
   az identity show --ids /subscriptions/YOUR_SUB/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ManagedIdentity/userAssignedIdentities/IDENTITY_NAME
   ```

2. **Check role assignments**:
   ```bash
   az role assignment list \
     --assignee $MANAGED_IDENTITY_PRINCIPAL_ID \
     --output table
   ```

3. **Required roles**:
   - Log Analytics Reader (on Log Analytics workspace)
   - Cognitive Services OpenAI User (on Azure OpenAI)
   - AcrPull (on Container Registry)

### Health Check Failures

1. **Run health check manually**:
   ```bash
   # Get into a container replica
   az containerapp exec \
     --name $CONTAINER_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --command /bin/sh
   
   # Inside container
   python -m pim_auto.main --mode health --detailed-health
   ```

2. **Check component health**:
   - Authentication: Managed identity token acquisition
   - Log Analytics: Workspace ID format and connectivity
   - OpenAI: Endpoint URL and deployment name

### High Memory/CPU Usage

1. **Monitor resource usage**:
   ```bash
   az containerapp show \
     --name $CONTAINER_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --query properties.template.containers[0].resources
   ```

2. **Increase resources** (if needed):
   Edit `main.bicep` and update:
   ```bicep
   resources: {
     cpu: json('1.0')    // Increase from 0.5
     memory: '2Gi'       // Increase from 1Gi
   }
   ```

3. **Redeploy**:
   ```bash
   az deployment group create \
     --resource-group $RESOURCE_GROUP \
     --template-file main.bicep \
     --parameters parameters.prod.json
   ```

---

## Best Practices

1. **Version Control**: Always tag container images with semantic versions
2. **Monitoring**: Set up alerts for errors and performance degradation
3. **Security**: Use managed identity exclusively (no service principals)
4. **Scaling**: For batch workloads, scale to zero when idle
5. **Costs**: Monitor Application Insights and Log Analytics ingestion costs
6. **Testing**: Test deployments in dev environment before production

---

## Next Steps

1. ✅ Complete initial deployment
2. ✅ Configure monitoring alerts
3. ✅ Test health checks
4. 🔄 Set up CI/CD pipeline (GitHub Actions)
5. 🔄 Configure backup and disaster recovery
6. 🔄 Implement log retention policies

---

## Support

- **Documentation**: See `/docs/Runbook.md` for operational procedures
- **Issues**: https://github.com/jometzg/pim-auto/issues
- **Architecture**: See `/docs/Target-Architecture.md`
