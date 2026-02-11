# Azure Infrastructure Deployment

This directory contains Infrastructure as Code (IaC) templates for deploying PIM Auto to Azure.

## Prerequisites

- Azure CLI installed and authenticated (`az login`)
- Azure subscription with appropriate permissions
- Resource Group created
- Log Analytics workspace with PIM data
- Azure OpenAI service deployed

## Deployment Steps

### 1. Update Parameters

Edit `parameters.dev.json` (or create environment-specific parameter files):

```bash
# Copy example parameters
cp parameters.dev.json parameters.prod.json

# Edit with your values
vi parameters.prod.json
```

Required parameters:
- `logAnalyticsWorkspaceId`: Your Log Analytics workspace ID (GUID)
- `azureOpenAIEndpoint`: Your Azure OpenAI endpoint URL
- `azureOpenAIDeployment`: Your GPT-4o deployment name

### 2. Deploy Infrastructure

```bash
# Set variables
RESOURCE_GROUP="rg-pimauto-prod"
LOCATION="eastus"
ENVIRONMENT="prod"

# Create resource group (if not exists)
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy using Bicep
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file main.bicep \
  --parameters parameters.$ENVIRONMENT.json

# Or validate first
az deployment group validate \
  --resource-group $RESOURCE_GROUP \
  --template-file main.bicep \
  --parameters parameters.$ENVIRONMENT.json
```

### 3. Build and Push Container Image

```bash
# Get ACR name from deployment outputs
ACR_NAME=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query properties.outputs.containerRegistryName.value \
  --output tsv)

ACR_LOGIN_SERVER=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query properties.outputs.containerRegistryLoginServer.value \
  --output tsv)

# Build and push image
az acr build \
  --registry $ACR_NAME \
  --image pimauto:latest \
  --image pimauto:$(date +%Y%m%d-%H%M%S) \
  --file ../../Dockerfile \
  ../../

# Or using Docker locally
docker build -t $ACR_LOGIN_SERVER/pimauto:latest ../../
az acr login --name $ACR_NAME
docker push $ACR_LOGIN_SERVER/pimauto:latest
```

### 4. Configure Azure OpenAI RBAC

The managed identity needs access to Azure OpenAI:

```bash
# Get managed identity principal ID
MANAGED_IDENTITY_PRINCIPAL_ID=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query properties.outputs.managedIdentityPrincipalId.value \
  --output tsv)

# Assign Cognitive Services OpenAI User role
OPENAI_RESOURCE_ID="/subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/YOUR_RG/providers/Microsoft.CognitiveServices/accounts/YOUR_OPENAI_RESOURCE"

az role assignment create \
  --assignee $MANAGED_IDENTITY_PRINCIPAL_ID \
  --role "Cognitive Services OpenAI User" \
  --scope $OPENAI_RESOURCE_ID
```

### 5. Update Container App (after image push)

```bash
# Get container app name
CONTAINER_APP_NAME=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query properties.outputs.containerAppName.value \
  --output tsv)

# Restart container app to pull new image
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP
```

## Resources Created

The Bicep template creates:

1. **Container Registry** - Stores Docker images
2. **Container Apps Environment** - Hosts the application
3. **Container App** - Runs the PIM Auto application
4. **Managed Identity** - Authenticates to Azure services
5. **Application Insights** - Monitors application telemetry
6. **Log Analytics Workspace** - Stores application logs (for App Insights)
7. **Role Assignments** - Grants necessary permissions

## Monitoring

After deployment, access Application Insights:

```bash
# Get Application Insights details
az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query properties.outputs.appInsightsInstrumentationKey.value
```

View in Azure Portal:
1. Navigate to the Application Insights resource
2. View Live Metrics, Logs, and custom metrics
3. Set up alerts for anomalies

## Troubleshooting

### Container fails to start

Check logs:
```bash
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --tail 100 \
  --follow
```

### Health check failures

Test health endpoint:
```bash
# If ingress is enabled publicly
FQDN=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query properties.outputs.containerAppFQDN.value \
  --output tsv)

curl https://$FQDN/health
```

### Authentication issues

Verify role assignments:
```bash
# Check managed identity assignments
az role assignment list \
  --assignee $MANAGED_IDENTITY_PRINCIPAL_ID \
  --output table
```

## Clean Up

To remove all resources:

```bash
# Delete resource group (removes all resources)
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## Cost Optimization

For dev/test environments:
- Set `minReplicas: 0` to scale to zero when idle
- Use Basic tier for Container Registry
- Reduce Log Analytics retention period
- Disable Application Insights if not needed

## Security Notes

- Managed identity is used for all Azure authentication (no secrets)
- Container runs as non-root user
- Container Registry admin user is disabled
- Network ingress is internal by default (not publicly accessible)
- All communication over HTTPS

## Next Steps

1. Set up Azure Monitor alerts for critical metrics
2. Configure log retention policies
3. Implement backup for configuration
4. Set up CI/CD pipeline for automated deployments
5. Configure Azure Key Vault for additional secrets (if needed)
