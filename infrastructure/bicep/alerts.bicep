// Alert rules for PIM Auto monitoring
// Deploy after main infrastructure is created

@description('Application Insights resource name')
param appInsightsName string

@description('Action Group resource ID for notifications')
param actionGroupId string

@description('Location for alert rules')
param location string = resourceGroup().location

// Reference existing Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

// Alert: High error rate
resource errorRateAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'pimauto-high-error-rate'
  location: 'global'
  properties: {
    description: 'Alert when error rate exceeds threshold'
    severity: 2
    enabled: true
    scopes: [
      appInsights.id
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'HighErrorRate'
          metricName: 'traces/count'
          operator: 'GreaterThan'
          threshold: 10
          timeAggregation: 'Count'
          criterionType: 'StaticThresholdCriterion'
          dimensions: [
            {
              name: 'severityLevel'
              operator: 'Include'
              values: [
                '3'  // Error level
                '4'  // Critical level
              ]
            }
          ]
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroupId
      }
    ]
  }
}

// Alert: Application availability
resource availabilityAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'pimauto-low-availability'
  location: 'global'
  properties: {
    description: 'Alert when application availability is below threshold'
    severity: 1
    enabled: true
    scopes: [
      appInsights.id
    ]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'LowAvailability'
          metricName: 'availabilityResults/availabilityPercentage'
          operator: 'LessThan'
          threshold: 90
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroupId
      }
    ]
  }
}

// Alert: Slow query performance
resource slowQueryAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'pimauto-slow-queries'
  location: 'global'
  properties: {
    description: 'Alert when query duration is consistently high'
    severity: 3
    enabled: true
    scopes: [
      appInsights.id
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'SlowQueries'
          metricName: 'customMetrics/query_duration_ms'
          operator: 'GreaterThan'
          threshold: 5000  // 5 seconds
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroupId
      }
    ]
  }
}

// Alert: No PIM activations detected (possible data pipeline issue)
resource noPimDataAlert 'Microsoft.Insights/scheduledQueryRules@2021-08-01' = {
  name: 'pimauto-no-pim-data'
  location: location
  properties: {
    description: 'Alert when no PIM activations detected for extended period (may indicate data pipeline issue)'
    severity: 3
    enabled: true
    evaluationFrequency: 'PT1H'
    windowSize: 'P1D'
    scopes: [
      appInsights.id
    ]
    criteria: {
      allOf: [
        {
          query: 'customMetrics | where name == "pim_activations_detected" | summarize count()'
          timeAggregation: 'Count'
          operator: 'LessThan'
          threshold: 1
          failingPeriods: {
            numberOfEvaluationPeriods: 2
            minFailingPeriodsToAlert: 2
          }
        }
      ]
    }
    actions: {
      actionGroups: [
        actionGroupId
      ]
    }
  }
}

// Alert: Excessive OpenAI API calls (cost control)
resource excessiveApiCallsAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'pimauto-excessive-api-calls'
  location: 'global'
  properties: {
    description: 'Alert when OpenAI API call rate is unusually high'
    severity: 3
    enabled: true
    scopes: [
      appInsights.id
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'HighApiCallRate'
          metricName: 'customMetrics/openai_api_calls'
          operator: 'GreaterThan'
          threshold: 100
          timeAggregation: 'Count'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroupId
      }
    ]
  }
}

// Outputs
output errorRateAlertId string = errorRateAlert.id
output availabilityAlertId string = availabilityAlert.id
output slowQueryAlertId string = slowQueryAlert.id
output noPimDataAlertId string = noPimDataAlert.id
output excessiveApiCallsAlertId string = excessiveApiCallsAlert.id
