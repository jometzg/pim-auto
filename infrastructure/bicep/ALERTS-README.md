# Azure Monitor Alerts Setup

This directory contains Bicep templates for setting up Azure Monitor alerts for PIM Auto.

## Prerequisites

- Main infrastructure deployed (`main.bicep`)
- Application Insights created
- Action Group configured for notifications

## Alert Rules

The `alerts.bicep` template creates the following alerts:

### 1. High Error Rate Alert
- **Severity**: 2 (Warning)
- **Condition**: More than 10 errors in 15 minutes
- **Purpose**: Detect application failures

### 2. Low Availability Alert
- **Severity**: 1 (Critical)
- **Condition**: Availability below 90% over 5 minutes
- **Purpose**: Detect service outages

### 3. Slow Query Alert
- **Severity**: 3 (Informational)
- **Condition**: Average query duration > 5 seconds
- **Purpose**: Detect performance degradation

### 4. No PIM Data Alert
- **Severity**: 3 (Informational)
- **Condition**: No PIM activations detected for 1 day
- **Purpose**: Detect data pipeline issues

### 5. Excessive API Calls Alert
- **Severity**: 3 (Informational)
- **Condition**: More than 100 OpenAI API calls in 15 minutes
- **Purpose**: Cost control and anomaly detection

## Deployment

### Step 1: Create Action Group

First, create an Action Group for notifications:

```bash
RESOURCE_GROUP="rg-pimauto-prod"

# Create action group
az monitor action-group create \
  --name pimauto-alerts \
  --resource-group $RESOURCE_GROUP \
  --short-name pimauto \
  --email-receiver name=security-team email=security@example.com
```

### Step 2: Get Application Insights Name

```bash
APP_INSIGHTS_NAME=$(az monitor app-insights component list \
  --resource-group $RESOURCE_GROUP \
  --query "[?contains(name, 'pimauto')].name" \
  --output tsv)

echo "Application Insights: $APP_INSIGHTS_NAME"
```

### Step 3: Get Action Group ID

```bash
ACTION_GROUP_ID=$(az monitor action-group show \
  --name pimauto-alerts \
  --resource-group $RESOURCE_GROUP \
  --query id \
  --output tsv)

echo "Action Group ID: $ACTION_GROUP_ID"
```

### Step 4: Deploy Alert Rules

```bash
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file alerts.bicep \
  --parameters \
    appInsightsName=$APP_INSIGHTS_NAME \
    actionGroupId=$ACTION_GROUP_ID
```

## Customization

### Adjust Thresholds

Edit `alerts.bicep` to modify thresholds:

```bicep
// Example: Change error threshold from 10 to 5
threshold: 5

// Example: Change query duration from 5000ms to 10000ms
threshold: 10000
```

### Add Additional Receivers

Add more notification channels to the action group:

```bash
# Add SMS receiver
az monitor action-group update \
  --name pimauto-alerts \
  --resource-group $RESOURCE_GROUP \
  --add-sms-receiver \
    name=oncall-sms \
    country-code=1 \
    phone-number=5551234567

# Add webhook
az monitor action-group update \
  --name pimauto-alerts \
  --resource-group $RESOURCE_GROUP \
  --add-webhook-receiver \
    name=teams-webhook \
    service-uri=https://outlook.office.com/webhook/...
```

## Testing Alerts

### Trigger Error Alert

Generate errors to test the alert:

```bash
# Run application with invalid configuration
az containerapp exec \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --command "python -c 'import logging; logger = logging.getLogger(); [logger.error(\"Test error %d\", i) for i in range(15)]'"
```

### Trigger Slow Query Alert

Simulate slow queries in Application Insights:

```bash
# This would need to be done from within the application
# or by modifying test data in App Insights
```

### Test Action Group

```bash
# Send test notification
az monitor action-group test-notifications create \
  --action-group-name pimauto-alerts \
  --resource-group $RESOURCE_GROUP \
  --notification-type Email \
  --email-subject "Test Alert from PIM Auto"
```

## Monitoring Alerts

### View Alert History

```bash
# List fired alerts
az monitor metrics alert list \
  --resource-group $RESOURCE_GROUP \
  --output table

# View specific alert details
az monitor metrics alert show \
  --name pimauto-high-error-rate \
  --resource-group $RESOURCE_GROUP
```

### Query Alert Logs

In Azure Portal > Application Insights > Logs:

```kql
// View all alert firings
AzureMetrics
| where MetricName contains "alert"
| where TimeGenerated > ago(7d)
| project TimeGenerated, MetricName, Average, Maximum
| order by TimeGenerated desc

// View application errors that trigger alerts
traces
| where severityLevel >= 3
| where timestamp > ago(1h)
| summarize count() by severityLevel, message
| order by count_ desc
```

## Disable/Enable Alerts

### Disable an alert temporarily

```bash
az monitor metrics alert update \
  --name pimauto-high-error-rate \
  --resource-group $RESOURCE_GROUP \
  --enabled false
```

### Re-enable

```bash
az monitor metrics alert update \
  --name pimauto-high-error-rate \
  --resource-group $RESOURCE_GROUP \
  --enabled true
```

## Clean Up

Remove all alert rules:

```bash
az monitor metrics alert delete \
  --name pimauto-high-error-rate \
  --resource-group $RESOURCE_GROUP

az monitor metrics alert delete \
  --name pimauto-low-availability \
  --resource-group $RESOURCE_GROUP

# ... repeat for other alerts

# Remove action group
az monitor action-group delete \
  --name pimauto-alerts \
  --resource-group $RESOURCE_GROUP
```

## Best Practices

1. **Start Conservative**: Begin with higher thresholds and adjust based on observed behavior
2. **Alert Fatigue**: Avoid too many low-severity alerts
3. **Actionable Alerts**: Every alert should have a clear remediation action
4. **Test Regularly**: Verify alerts fire correctly
5. **Review Monthly**: Adjust thresholds based on operational experience
6. **Document Runbooks**: Link each alert to troubleshooting procedures

## Cost Considerations

- Alert rules have minimal cost (~$0.10 per alert per month)
- Action Group notifications:
  - Email: Free (up to 1,000/month)
  - SMS: ~$0.01 per SMS
  - Webhooks: Free
- Log Analytics queries: Included in Log Analytics ingestion costs

## Troubleshooting

### Alerts Not Firing

1. Check Application Insights has data:
   ```kql
   traces
   | where timestamp > ago(1h)
   | summarize count()
   ```

2. Verify alert is enabled:
   ```bash
   az monitor metrics alert show --name pimauto-high-error-rate --resource-group $RESOURCE_GROUP --query enabled
   ```

3. Check evaluation frequency and window size are appropriate

### Not Receiving Notifications

1. Verify action group has correct email/phone:
   ```bash
   az monitor action-group show --name pimauto-alerts --resource-group $RESOURCE_GROUP
   ```

2. Check spam/junk folders for alert emails

3. Test action group directly (see Testing section above)

## Next Steps

1. ✅ Deploy alert rules
2. ✅ Test notifications
3. 🔄 Create runbooks for each alert
4. 🔄 Set up dashboard with alert status
5. 🔄 Document escalation procedures
