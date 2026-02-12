# GitHub Skill: KQL Query Generation and Execution for Azure Log Analytics

## Overview
This skill enables AI-powered generation of Kusto Query Language (KQL) queries for Azure Log Analytics using Azure OpenAI, with automated execution and self-correction capabilities.

## Prerequisites
- Python 3.11+
- Azure OpenAI resource with GPT-4 deployment
- Azure Log Analytics workspace
- Azure CLI or Managed Identity for authentication
- Required Python packages:
  ```bash
  pip install azure-identity azure-monitor-query openai python-dotenv
  ```

## Required RBAC Roles
- **"Cognitive Services OpenAI User"** on Azure OpenAI resource
- **"Log Analytics Reader"** on Log Analytics workspace

---

## 1. Authentication Setup

Use `DefaultAzureCredential` for secure, environment-agnostic authentication:

```python
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from openai import AzureOpenAI

# Initialize credential (supports Azure CLI, Managed Identity, etc.)
credential = DefaultAzureCredential()

# Create Log Analytics client
logs_client = LogsQueryClient(credential=credential)

# Create Azure OpenAI client
token = credential.get_token("https://cognitiveservices.azure.com/.default")
openai_client = AzureOpenAI(
    azure_endpoint="https://your-openai-resource.openai.azure.com/",
    api_version="2024-02-15-preview",
    azure_ad_token=token.token
)
```

**Environment Variables (.env file):**
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
LOG_ANALYTICS_WORKSPACE_ID=<workspace-guid>
```

---

## 2. Table Schemas for Query Generation

### AuditLogs Table Schema
```python
AUDIT_LOGS_SCHEMA = """
AuditLogs table columns:
- TimeGenerated (datetime): Timestamp of the event
- OperationName (string): Name of the operation (e.g., "Add member to role completed (PIM activation)")
- InitiatedBy (dynamic): Nested JSON object with structure: 
  { "user": { "userPrincipalName": "email@domain.com", "displayName": "User Name" } }
  To extract the email: tostring(InitiatedBy.user.userPrincipalName)
  To extract the display name: tostring(InitiatedBy.user.displayName)
- TargetResources (dynamic): JSON array with target resource details
  To extract first resource's display name: tostring(TargetResources[0].displayName)
- CorrelationId (string): Groups related events
- ResultDescription (string): Reason for action
- Result (string): Success, failure, or other status
- AdditionalDetails (dynamic): JSON array with metadata
  Self-authorization flag: tobool(AdditionalDetails[0].value)
"""
```

### AzureActivity Table Schema
```python
AZURE_ACTIVITY_SCHEMA = """
AzureActivity table columns:
- TimeGenerated (datetime): Timestamp of the activity
- Caller (string): Email/UPN of the user who performed the action
- ResourceGroup (string): Resource group name
- ResourceProvider (string): Azure resource provider
- ResourceId (string): Full Azure resource ID
- OperationNameValue (string): Operation performed
- ActivityStatusValue (string): Success, failure, or other status
- Properties (dynamic): Additional metadata as JSON
- SubscriptionId (string): Azure subscription ID
"""
```

---

## 3. Query Generation Using Azure OpenAI

### Core Query Generator Class

```python
import logging
from typing import Optional
from openai import AzureOpenAI

logger = logging.getLogger(__name__)

class QueryGenerator:
    """Generates Kusto queries using Azure OpenAI."""
    
    def __init__(self, openai_client: AzureOpenAI, deployment_name: str):
        self.client = openai_client
        self.deployment_name = deployment_name
    
    def generate_kusto_query(
        self,
        task_description: str,
        context: Optional[str] = None
    ) -> str:
        """
        Generate a Kusto query from natural language description.
        
        Args:
            task_description: Natural language description of what to query
            context: Optional additional context (e.g., previous errors)
            
        Returns:
            Executable Kusto query string
        """
        logger.info(f"Generating Kusto query for: {task_description}")
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(task_description, context)
        
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temperature for deterministic code generation
            max_tokens=1000
        )
        
        query = response.choices[0].message.content.strip()
        query = self._clean_query(query)  # Remove markdown formatting
        
        logger.debug(f"Generated query:\n{query}")
        return query
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with schema information."""
        return f"""You are an expert at writing Kusto (KQL) queries for Azure Log Analytics.

Your task is to generate executable Kusto queries based on user requirements.

Available table schemas:

{AUDIT_LOGS_SCHEMA}

{AZURE_ACTIVITY_SCHEMA}

Important guidelines:
1. Return ONLY executable Kusto query code
2. Do NOT wrap the query in markdown code blocks or formatting
3. Do NOT include explanations or comments
4. Use proper KQL syntax and operators
5. Handle JSON fields correctly using extend and parse operators
6. ALWAYS use 'ago()' function for time ranges (e.g., ago(1d), ago(10d), ago(24h))
7. If the user specifies a time range, include it in the query using ago()
8. If no timespan is specified in the task, default to ago(1d) for 1 day lookback
9. Use 'contains' for case-insensitive substring matching
10. Use 'project' to select specific columns
11. Use 'where' for filtering
12. Format datetime values properly

The query should be ready to execute as-is without any modifications."""
    
    def _build_user_prompt(
        self,
        task_description: str,
        context: Optional[str] = None
    ) -> str:
        """Build user prompt with task description and context."""
        prompt = f"Generate a Kusto query for the following task:\n\n{task_description}"
        
        if context:
            prompt += f"\n\nAdditional context:\n{context}"
        
        return prompt
    
    def _clean_query(self, query: str) -> str:
        """Remove markdown formatting from query."""
        if query.startswith("```"):
            lines = query.split("\n")
            if lines[0].strip().startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            query = "\n".join(lines)
        return query.strip()
```

---

## 4. Query Execution with Self-Correction

### Executor with Automatic Retry

```python
import logging
from typing import Any, Dict, List, Optional
from datetime import timedelta
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.core.exceptions import HttpResponseError

logger = logging.getLogger(__name__)

class QueryExecutor:
    """Executes Kusto queries with self-correction retry logic."""
    
    MAX_RETRIES = 3
    
    def __init__(
        self,
        logs_client: LogsQueryClient,
        query_generator,
        workspace_id: str
    ):
        self.logs_client = logs_client
        self.query_generator = query_generator
        self.workspace_id = workspace_id
    
    def execute_query(
        self,
        query: str,
        timespan: Optional[timedelta] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a Kusto query with self-correction retry logic.
        
        IMPORTANT: Time filtering should be in the query using ago(), 
        not in the timespan parameter. Always pass timespan=None.
        
        Args:
            query: Kusto query to execute
            timespan: Not used - time filtering is done in query with ago()
            
        Returns:
            List of row dictionaries from query results
        """
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.info(f"Executing query (attempt {attempt}/{self.MAX_RETRIES})")
                logger.debug(f"Query:\n{query}")
                
                # Execute query without timespan - time filtering is in the query
                response = self.logs_client.query_workspace(
                    workspace_id=self.workspace_id,
                    query=query,
                    timespan=None
                )
                
                # Check response status
                if response.status == LogsQueryStatus.PARTIAL:
                    logger.warning("Query returned partial results")
                elif response.status == LogsQueryStatus.SUCCESS:
                    logger.info("✓ Query executed successfully")
                
                # Convert results to list of dictionaries
                results = self._process_results(response)
                logger.info(f"Query returned {len(results)} rows")
                return results
                
            except HttpResponseError as e:
                error_msg = str(e)
                logger.warning(f"Query failed (attempt {attempt}): {error_msg}")
                
                if attempt < self.MAX_RETRIES:
                    # Try to fix the query using AI
                    try:
                        logger.info("Attempting to fix query with AI...")
                        query = self.query_generator.fix_query(
                            original_query=query,
                            error_message=error_msg,
                            attempt_number=attempt
                        )
                        logger.info(f"Generated corrected query for attempt {attempt + 1}")
                    except Exception as fix_error:
                        logger.error(f"Failed to generate fix: {fix_error}")
                else:
                    # All retries exhausted
                    logger.error(
                        f"❌ Query execution failed after {self.MAX_RETRIES} attempts. "
                        f"Error: {error_msg}"
                    )
                    return []
        
        return []
    
    def execute_generated_query(
        self,
        task_description: str,
        timespan: Optional[timedelta] = None,
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate and execute a query from natural language description.
        
        Args:
            task_description: Natural language description of query requirements
            timespan: Not used - time filtering in query
            context: Optional context for query generation
            
        Returns:
            List of row dictionaries
        """
        query = self.query_generator.generate_kusto_query(
            task_description=task_description,
            context=context
        )
        return self.execute_query(query, timespan=None)
    
    def _process_results(self, response) -> List[Dict[str, Any]]:
        """Convert query response to list of dictionaries."""
        results = []
        for table in response.tables:
            for row in table.rows:
                row_dict = {}
                for i, column in enumerate(table.columns):
                    row_dict[column] = row[i]
                results.append(row_dict)
        return results
```

### Query Correction Method

```python
def fix_query(
    self,
    original_query: str,
    error_message: str,
    attempt_number: int
) -> str:
    """
    Generate a corrected version of a failed query.
    
    Args:
        original_query: The query that failed
        error_message: Error message from Kusto
        attempt_number: Which retry attempt this is (1-3)
        
    Returns:
        Corrected Kusto query
    """
    logger.info(f"Fixing query (attempt {attempt_number}/3)")
    
    fix_prompt = f"""
The following Kusto query produced an error:

```kusto
{original_query}
```

Error message:
{error_message}

Please analyze the error and provide a corrected version of the query.
Return ONLY the corrected Kusto query code without any explanation or markdown formatting.
"""
    
    response = self.client.chat.completions.create(
        model=self.deployment_name,
        messages=[
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": fix_prompt}
        ],
        temperature=0.1,
        max_tokens=1000
    )
    
    corrected_query = response.choices[0].message.content.strip()
    corrected_query = self._clean_query(corrected_query)
    
    logger.debug(f"Corrected query:\n{corrected_query}")
    return corrected_query
```

---

## 5. Best Practices for Effective Queries

### AuditLogs Best Practices

#### 1. **Extracting User Information from InitiatedBy (JSON field)**
```python
task_description = """
Query AuditLogs for PIM activations in the last 7 days.
- Filter: TimeGenerated >= ago(7d)
- Extract: tostring(InitiatedBy.user.userPrincipalName) as InitiatedByUser
- Extract: tostring(InitiatedBy.user.displayName) as InitiatedByName
- Order by TimeGenerated descending
"""
```

**Generated KQL:**
```kql
AuditLogs
| where TimeGenerated >= ago(7d)
| extend InitiatedByUser = tostring(InitiatedBy.user.userPrincipalName)
| extend InitiatedByName = tostring(InitiatedBy.user.displayName)
| order by TimeGenerated desc
```

#### 2. **Extracting Target Resources (Array field)**
```python
task_description = """
Query AuditLogs for role assignments showing target resources.
- Filter: TimeGenerated >= ago(14d)
- Filter: OperationName contains "role"
- Extract: tostring(TargetResources[0].displayName) as TargetRole
- Extract: tostring(TargetResources[0].id) as TargetResourceId
"""
```

**Generated KQL:**
```kql
AuditLogs
| where TimeGenerated >= ago(14d)
| where OperationName contains "role"
| extend TargetRole = tostring(TargetResources[0].displayName)
| extend TargetResourceId = tostring(TargetResources[0].id)
| project TimeGenerated, OperationName, TargetRole, TargetResourceId
```

#### 3. **Using CorrelationId to Group Related Events**
```python
task_description = """
Find all events related to PIM activation with CorrelationId.
- Filter: TimeGenerated >= ago(7d)
- Filter: OperationName contains "PIM"
- Group by CorrelationId
- Order by TimeGenerated
"""
```

**Generated KQL:**
```kql
AuditLogs
| where TimeGenerated >= ago(7d)
| where OperationName contains "PIM"
| summarize 
    EventCount = count(),
    Operations = make_set(OperationName),
    FirstEvent = min(TimeGenerated),
    LastEvent = max(TimeGenerated)
    by CorrelationId
| order by FirstEvent desc
```

#### 4. **Extracting Self-Authorization Flag from AdditionalDetails**
```python
task_description = """
Query PIM activations with self-authorization status.
- Filter: TimeGenerated >= ago(10d)
- Filter: OperationName contains "PIM activation"
- Extract: tobool(AdditionalDetails[0].value) as IsSelfAuthorized
- Show only self-authorized activations
"""
```

**Generated KQL:**
```kql
AuditLogs
| where TimeGenerated >= ago(10d)
| where OperationName contains "PIM activation"
| extend IsSelfAuthorized = tobool(AdditionalDetails[0].value)
| where IsSelfAuthorized == true
| project TimeGenerated, OperationName, InitiatedBy, IsSelfAuthorized
```

### AzureActivity Best Practices

#### 1. **Tracking User Activities by Caller**
```python
task_description = """
Find all Azure activities by specific user in last 24 hours.
- Filter: TimeGenerated >= ago(24h)
- Filter: Caller == "user@domain.com"
- Show: ResourceGroup, ResourceProvider, OperationNameValue, ActivityStatusValue
- Order by TimeGenerated descending
"""
```

**Generated KQL:**
```kql
AzureActivity
| where TimeGenerated >= ago(24h)
| where Caller == "user@domain.com"
| project 
    TimeGenerated, 
    Caller, 
    ResourceGroup, 
    ResourceProvider, 
    OperationNameValue, 
    ActivityStatusValue
| order by TimeGenerated desc
```

#### 2. **Correlating Activities During Time Windows**
```python
task_description = """
Find all Azure activities between two timestamps.
- Filter: TimeGenerated between specific start and end times
- Filter: ActivityStatusValue == "Success"
- Group by ResourceGroup and OperationNameValue
"""
```

**Generated KQL:**
```kql
let startTime = datetime(2024-02-10T14:00:00Z);
let endTime = datetime(2024-02-10T22:00:00Z);
AzureActivity
| where TimeGenerated between (startTime .. endTime)
| where ActivityStatusValue == "Success"
| summarize 
    ActivityCount = count()
    by ResourceGroup, OperationNameValue, Caller
| order by ActivityCount desc
```

#### 3. **Filtering by Resource Provider**
```python
task_description = """
Find all compute-related activities in last 7 days.
- Filter: TimeGenerated >= ago(7d)
- Filter: ResourceProvider == "Microsoft.Compute"
- Show: Caller, ResourceGroup, OperationNameValue, ResourceId
"""
```

**Generated KQL:**
```kql
AzureActivity
| where TimeGenerated >= ago(7d)
| where ResourceProvider == "Microsoft.Compute"
| project 
    TimeGenerated,
    Caller,
    ResourceGroup,
    OperationNameValue,
    ResourceId,
    ActivityStatusValue
| order by TimeGenerated desc
```

---

## 6. Complete Usage Example

```python
import logging
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize authentication
credential = DefaultAzureCredential()

# Create clients
logs_client = LogsQueryClient(credential=credential)
token = credential.get_token("https://cognitiveservices.azure.com/.default")
openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-02-15-preview",
    azure_ad_token=token.token
)

# Create query generator and executor
query_generator = QueryGenerator(
    openai_client=openai_client,
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
)

query_executor = QueryExecutor(
    logs_client=logs_client,
    query_generator=query_generator,
    workspace_id=os.getenv("LOG_ANALYTICS_WORKSPACE_ID")
)

# Example 1: Generate and execute query
task = """
Find all PIM activations in the last 14 days.
- Filter: TimeGenerated >= ago(14d)
- Filter: OperationName contains "PIM activation"
- Extract: tostring(InitiatedBy.user.userPrincipalName) as InitiatedByUser
- Extract: tostring(TargetResources[0].displayName) as TargetRole
- Show: TimeGenerated, OperationName, InitiatedByUser, TargetRole, Result
- Order by TimeGenerated descending
"""

results = query_executor.execute_generated_query(task_description=task)

# Process results
for row in results:
    print(f"Time: {row['TimeGenerated']}")
    print(f"User: {row.get('InitiatedByUser', 'N/A')}")
    print(f"Role: {row.get('TargetRole', 'N/A')}")
    print(f"Status: {row['Result']}")
    print("-" * 50)

# Example 2: Track user activities
activity_task = """
Find all Azure activities by user@domain.com in last 24 hours.
- Filter: TimeGenerated >= ago(24h)
- Filter: Caller == "user@domain.com"
- Show: ResourceGroup, OperationNameValue, ActivityStatusValue
- Count activities per resource group
"""

activities = query_executor.execute_generated_query(task_description=activity_task)
print(f"Found {len(activities)} activities")
```

---

## 7. Critical Guidelines

### ⚠️ Time Filtering
**ALWAYS use `ago()` in the query itself, NEVER use the API `timespan` parameter:**
```python
# ✅ CORRECT
task = "Find events from last 7 days using TimeGenerated >= ago(7d)"
results = executor.execute_generated_query(task, timespan=None)

# ❌ INCORRECT
results = executor.execute_generated_query(task, timespan=timedelta(days=7))
```

### 🔍 JSON Field Extraction
**Always use `tostring()` or `tobool()` for dynamic fields:**
```kql
-- ✅ CORRECT
| extend UserEmail = tostring(InitiatedBy.user.userPrincipalName)
| extend IsAuthorized = tobool(AdditionalDetails[0].value)

-- ❌ INCORRECT
| extend UserEmail = InitiatedBy.user.userPrincipalName  -- Returns JSON object
```

### 🔄 Retry Logic
- Maximum 3 retry attempts with AI-powered self-correction
- On failure, log error and return empty list (don't crash)
- Each retry uses the corrected query from previous attempt

### 📊 Result Processing
- Always convert query results to list of dictionaries
- Handle partial results gracefully
- Log row counts for debugging

---

## 8. Error Handling Patterns

```python
try:
    results = query_executor.execute_generated_query(task_description)
    if not results:
        logger.warning("No results found or query failed after retries")
    else:
        logger.info(f"Successfully retrieved {len(results)} rows")
        # Process results...
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle gracefully
```

---

## 9. Performance Tips

1. **Use specific time ranges** - Don't query more than needed
2. **Project early** - Select only required columns
3. **Filter early** - Apply where clauses before transformations
4. **Use summarize** - Aggregate data when possible
5. **Limit results** - Use `take` or `limit` for large datasets

**Example optimized query:**
```kql
AuditLogs
| where TimeGenerated >= ago(7d)  -- Filter early
| where OperationName contains "PIM"  -- Filter before extraction
| extend UserEmail = tostring(InitiatedBy.user.userPrincipalName)
| project TimeGenerated, OperationName, UserEmail, Result  -- Project early
| take 100  -- Limit results
```

---

## 10. Testing Patterns

```python
import pytest
from unittest.mock import Mock, patch

def test_query_generation():
    """Test query generation with mocked OpenAI."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices[0].message.content = "AuditLogs | where TimeGenerated >= ago(1d)"
    mock_client.chat.completions.create.return_value = mock_response
    
    generator = QueryGenerator(mock_client, "gpt-4")
    query = generator.generate_kusto_query("Find events from last day")
    
    assert "AuditLogs" in query
    assert "ago(1d)" in query
```

---

## Summary

This skill enables:
1. ✅ AI-powered KQL query generation from natural language
2. ✅ Automated query execution with retry and self-correction
3. ✅ Best practices for AuditLogs and AzureActivity tables
4. ✅ Proper JSON field extraction and time filtering
5. ✅ Production-ready error handling and logging

**Key Innovation**: Queries are never hardcoded. All KQL is dynamically generated with embedded schema knowledge and self-correcting retry logic.
