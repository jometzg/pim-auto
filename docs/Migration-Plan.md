# Migration Plan - PIM Auto

**Document Status**: Proposed  
**Last Updated**: 2026-02-10  
**Repository**: jometzg/pim-auto  
**Purpose**: Define phased, incremental migration from specification to production-ready containerized application

## Executive Summary

This migration plan uses the **strangler pattern** to incrementally modernize the PIM Auto application from its current state (specification-only) to a production-ready containerized system. The approach prioritizes:

- **Low-risk, incremental changes**: Each slice is independently testable and reversible
- **Behavior preservation**: All functionality specified in `/README.md` is maintained
- **Early value delivery**: Each slice delivers demonstrable progress
- **Clear acceptance criteria**: Each phase has explicit entry/exit conditions

The plan is designed to be executed by the Implementation Agent with human approval at each phase boundary.

## Current State Assessment

As documented in `/docs/HLD.md` and `/docs/LLD.md`:

**What Exists**:
- ✅ Complete specification (`/README.md`)
- ✅ Agent-based governance infrastructure (`/.github/`)
- ✅ Documentation (HLD, LLD, 4 ADRs)

**What Does Not Exist**:
- ❌ Python source code
- ❌ Tests
- ❌ Dependencies (requirements.txt)
- ❌ Container configuration (Dockerfile)
- ❌ CI/CD pipeline
- ❌ Deployment infrastructure

**Target State** (per `/docs/Target-Architecture.md`):
- Containerized Python 3.11+ application
- Deployed to Azure Container Apps (production) or ACI (dev)
- Support for both interactive chat and batch modes
- Full Azure integration (OpenAI, Log Analytics, Managed Identity)
- Comprehensive test coverage
- Operational runbook and monitoring

## Migration Philosophy

### Strangler Pattern Principles

1. **Incremental**: Build new system piece by piece, not all at once
2. **Coexistence**: Old and new can run side-by-side (though in our case, "old" is just specification)
3. **Reversible**: Each step can be rolled back without catastrophic impact
4. **Testable**: Each slice is independently verifiable

### Risk Management Strategy

- **Minimize blast radius**: Small changes reduce impact of failures
- **Fail fast**: Validate early and often (tests, configuration checks)
- **Explicit rollback**: Each phase documents rollback procedure
- **Human checkpoints**: Approval required at phase boundaries

### Slice Sizing

Each slice should be:
- **Completable in 1-2 PRs**: Avoid long-lived branches
- **Testable independently**: Not dependent on future slices
- **Demonstrable**: Can show working feature or capability
- **Documentable**: Can explain what changed and why

## Migration Phases Overview

| Phase | Slice | Focus | Estimated Effort | Risk Level |
|-------|-------|-------|------------------|------------|
| **Foundation** | Slice 0 | Project structure, CI, testing baseline, container skeleton | 3-5 days | Low |
| **Core Implementation** | Slice 1 | Azure integration, core logic, basic functionality | 5-7 days | Medium |
| **Dual Mode Support** | Slice 2 | Interactive CLI and batch mode, full feature parity | 3-5 days | Low-Medium |
| **Production Readiness** | Slice 3 | Deployment automation, monitoring, runbook updates | 3-4 days | Low |
| **Validation** | Slice 4 | End-to-end testing, performance validation, documentation | 2-3 days | Low |

**Total Estimated Timeline**: 16-24 days (assuming single developer, part-time)

**Note**: These are planning estimates. Actual implementation may vary based on discovery and feedback.

---

## Slice 0: Foundation and Baseline Testing

### Purpose

Establish project infrastructure without implementing business logic. This "stabilization slice" creates the foundation for future development.

### Objectives

1. Create Python project structure
2. Set up dependency management
3. Configure linting and code quality tools
4. Establish testing framework and baseline tests
5. Create container skeleton (Dockerfile)
6. Update CI/CD pipeline to build and test
7. Document developer setup process

### Entry Criteria

✅ Target Architecture approved  
✅ Migration Plan approved  
✅ Testing Agent has created baseline test strategy (or will do so in parallel)  

### Detailed Changes

#### 1. Project Structure Creation

Create directory structure:

```
pim-auto/
├── .github/
│   ├── workflows/
│   │   └── ci.yml                    # Updated for Python/container build
│   ├── agents/                       # Existing
│   └── skills/                       # Existing
├── docs/                             # Existing
├── src/
│   └── pim_auto/
│       ├── __init__.py               # Package marker
│       ├── main.py                   # Application entry point (stub)
│       ├── config.py                 # Configuration management (stub)
│       └── core/
│           └── __init__.py           # Core modules package marker
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   ├── unit/
│   │   └── __init__.py
│   └── integration/
│       └── __init__.py
├── .gitignore                        # Python, container, IDE ignores
├── .dockerignore                     # Container build excludes
├── Dockerfile                        # Container specification
├── requirements.txt                  # Python dependencies
├── requirements-dev.txt              # Development dependencies
├── pyproject.toml                    # Python project metadata
└── README.md                         # Existing (specification)
```

#### 2. Dependency Management

**requirements.txt** (production dependencies):
```txt
# Azure SDK
azure-identity>=1.15.0
azure-monitor-query>=1.3.0
openai>=1.10.0  # Azure OpenAI support

# CLI
rich>=13.7.0  # For interactive CLI formatting
click>=8.1.7  # Command-line argument parsing

# Logging and monitoring
opencensus-ext-azure>=1.1.13  # Application Insights
python-json-logger>=2.0.7  # Structured logging
```

**requirements-dev.txt** (development dependencies):
```txt
# Testing
pytest>=8.0.0
pytest-cov>=4.1.0
pytest-asyncio>=0.23.0
pytest-mock>=3.12.0

# Linting and formatting
black>=24.1.0
flake8>=7.0.0
mypy>=1.8.0
isort>=5.13.0

# Security scanning
bandit>=1.7.6
safety>=3.0.0
```

**pyproject.toml** (project metadata):
```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "pim-auto"
version = "0.1.0"
description = "Azure PIM Activity Audit Agent"
requires-python = ">=3.11"
readme = "README.md"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-ra -q --cov=src/pim_auto --cov-report=term-missing"
testpaths = ["tests"]
```

#### 3. Container Skeleton

**Dockerfile** (initial version):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (none needed initially, but prepared for future)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check (basic)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "print('alive')" || exit 1

# Default command (will be replaced in Slice 1 with actual application)
CMD ["python", "-c", "print('PIM Auto container - not yet implemented')"]
```

**.dockerignore**:
```
.git
.github
.pytest_cache
.mypy_cache
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
docs/
tests/
*.md
.gitignore
.dockerignore
```

#### 4. CI/CD Pipeline Updates

Update `/.github/workflows/ci.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      
      - name: Run black (check only)
        run: black --check src/ tests/
      
      - name: Run flake8
        run: flake8 src/ tests/
      
      - name: Run mypy
        run: mypy src/
      
      - name: Run isort (check only)
        run: isort --check-only src/ tests/

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      
      - name: Run bandit
        run: bandit -r src/
      
      - name: Run safety check
        run: safety check --json

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests with coverage
        run: pytest --cov=src/pim_auto --cov-report=xml --cov-report=term
      
      - name: Upload coverage to Codecov (optional)
        uses: codecov/codecov-action@v3
        if: github.event_name == 'pull_request'
        with:
          files: ./coverage.xml

  build:
    runs-on: ubuntu-latest
    needs: [lint, security, test]
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          tags: pim-auto:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Test Docker image
        run: |
          docker build -t pim-auto:test .
          docker run --rm pim-auto:test
```

#### 5. Baseline Tests

Create minimal tests to validate infrastructure:

**tests/conftest.py**:
```python
"""Pytest configuration and shared fixtures."""
import pytest


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "azure_openai_endpoint": "https://test.openai.azure.com/",
        "azure_openai_deployment": "gpt-4o",
        "log_analytics_workspace_id": "test-workspace-id",
    }
```

**tests/unit/test_config.py**:
```python
"""Tests for configuration management."""


def test_sample_config_fixture(sample_config):
    """Verify sample config fixture works."""
    assert "azure_openai_endpoint" in sample_config
    assert sample_config["azure_openai_deployment"] == "gpt-4o"


def test_placeholder():
    """Placeholder test to ensure pytest works."""
    assert True
```

**tests/unit/test_main.py**:
```python
"""Tests for main entry point."""


def test_placeholder_main():
    """Placeholder test for main module."""
    # This will be replaced with real tests in Slice 1
    assert True
```

#### 6. Documentation Updates

Create **docs/Developer-Setup.md**:

```markdown
# Developer Setup Guide

## Prerequisites

- Python 3.11 or higher
- Docker Desktop
- Azure CLI (for Azure authentication)
- Git

## Initial Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jometzg/pim-auto.git
   cd pim-auto
   ```

2. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Verify installation:
   ```bash
   pytest
   black --check src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src/pim_auto

# Specific test file
pytest tests/unit/test_config.py

# Verbose output
pytest -v
```

## Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check formatting (CI mode)
black --check src/ tests/
isort --check-only src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/
```

## Building Container

```bash
# Build image
docker build -t pim-auto:local .

# Run container
docker run --rm pim-auto:local

# Interactive shell
docker run --rm -it pim-auto:local /bin/bash
```

## Azure Authentication (Local Development)

```bash
# Login to Azure
az login

# Set default subscription (if you have multiple)
az account set --subscription "Your Subscription Name"

# Verify authentication
az account show
```

## Troubleshooting

### Virtual Environment Issues

If you see "command not found" errors, ensure your virtual environment is activated:
```bash
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Dependency Conflicts

Clear and reinstall dependencies:
```bash
pip install --upgrade pip
pip install --force-reinstall -r requirements.txt
pip install --force-reinstall -r requirements-dev.txt
```

### Docker Build Failures

Clear Docker cache and rebuild:
```bash
docker builder prune -a
docker build --no-cache -t pim-auto:local .
```
```

### Exit Criteria

**Must Pass**:
- ✅ All directory structure created
- ✅ Dependencies defined and installable
- ✅ Linting passes (black, flake8, mypy, isort)
- ✅ Security checks pass (bandit, safety)
- ✅ Baseline tests pass (even if minimal)
- ✅ Docker image builds successfully
- ✅ CI/CD pipeline runs green
- ✅ Developer setup documentation complete

**Deliverables**:
- Project structure with all directories
- `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`
- `Dockerfile` and `.dockerignore`
- Updated `.github/workflows/ci.yml`
- Baseline tests in `tests/` directory
- `docs/Developer-Setup.md`

**Success Criteria**:
A developer can:
1. Clone the repo
2. Follow Developer-Setup.md
3. Run tests successfully
4. Build container successfully
5. See green CI pipeline

### Rollback Plan

**If Slice 0 fails**:
1. Delete created directories (`src/`, `tests/`)
2. Revert changes to `.github/workflows/ci.yml`
3. Remove added files (`Dockerfile`, `requirements.txt`, etc.)
4. Repository returns to specification-only state

**Risk**: Very low - no business logic implemented, only infrastructure files

---

## Slice 1: Core Azure Integration and Business Logic

### Purpose

Implement the core application functionality: Azure authentication, Log Analytics querying, Azure OpenAI integration, and basic PIM detection logic.

### Objectives

1. Implement Azure authentication (DefaultAzureCredential)
2. Create Log Analytics client wrapper
3. Create Azure OpenAI client wrapper
4. Implement PIM Detector module
5. Implement Activity Correlator module
6. Implement Query Generator module
7. Implement Risk Assessor module
8. Create comprehensive unit tests (with mocked Azure services)
9. Update container to run basic functionality

### Entry Criteria

✅ Slice 0 completed and merged  
✅ CI/CD pipeline passing  
✅ Developer environment verified  

### Detailed Changes

#### 1. Configuration Management

**src/pim_auto/config.py**:
```python
"""Configuration management for PIM Auto."""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application configuration."""
    
    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_deployment: str
    azure_openai_api_version: str = "2024-02-15-preview"
    
    # Azure Log Analytics
    log_analytics_workspace_id: str
    log_analytics_region: Optional[str] = None
    
    # Application settings
    default_scan_hours: int = 24
    log_level: str = "INFO"
    batch_output_path: Optional[str] = None
    
    @classmethod
    def from_environment(cls) -> "Config":
        """Load configuration from environment variables."""
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT",
            "LOG_ANALYTICS_WORKSPACE_ID",
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return cls(
            azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_openai_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            azure_openai_api_version=os.getenv(
                "AZURE_OPENAI_API_VERSION",
                "2024-02-15-preview"
            ),
            log_analytics_workspace_id=os.getenv("LOG_ANALYTICS_WORKSPACE_ID"),
            log_analytics_region=os.getenv("LOG_ANALYTICS_REGION"),
            default_scan_hours=int(os.getenv("DEFAULT_SCAN_HOURS", "24")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            batch_output_path=os.getenv("BATCH_OUTPUT_PATH"),
        )
    
    def validate(self) -> None:
        """Validate configuration values."""
        if not self.azure_openai_endpoint.startswith("https://"):
            raise ValueError("Azure OpenAI endpoint must start with https://")
        
        if self.default_scan_hours < 1 or self.default_scan_hours > 168:
            raise ValueError("Default scan hours must be between 1 and 168 (1 week)")
        
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {self.log_level}")
```

#### 2. Azure Client Wrappers

Create wrappers for Azure services to enable testing and encapsulate Azure SDK complexity.

**src/pim_auto/azure/auth.py**:
```python
"""Azure authentication management."""
from azure.identity import DefaultAzureCredential


def get_azure_credential() -> DefaultAzureCredential:
    """Get Azure credential using DefaultAzureCredential chain."""
    return DefaultAzureCredential()
```

**src/pim_auto/azure/log_analytics.py**:
```python
"""Azure Log Analytics client wrapper."""
from typing import List, Dict, Any
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import DefaultAzureCredential
import logging

logger = logging.getLogger(__name__)


class LogAnalyticsClient:
    """Wrapper for Azure Log Analytics queries."""
    
    def __init__(self, workspace_id: str, credential: DefaultAzureCredential):
        self.workspace_id = workspace_id
        self.client = LogsQueryClient(credential)
    
    def execute_query(self, query: str, timespan: str = "P1D") -> List[Dict[str, Any]]:
        """Execute KQL query and return results."""
        try:
            response = self.client.query_workspace(
                workspace_id=self.workspace_id,
                query=query,
                timespan=timespan
            )
            
            if response.status == LogsQueryStatus.SUCCESS:
                results = []
                for table in response.tables:
                    for row in table.rows:
                        row_dict = dict(zip([col.name for col in table.columns], row))
                        results.append(row_dict)
                return results
            else:
                logger.error(f"Query failed with status: {response.status}")
                return []
        
        except Exception as e:
            logger.error(f"Log Analytics query error: {e}")
            raise
```

**src/pim_auto/azure/openai_client.py**:
```python
"""Azure OpenAI client wrapper."""
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import logging

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Wrapper for Azure OpenAI API."""
    
    def __init__(
        self,
        endpoint: str,
        deployment: str,
        api_version: str,
        credential: DefaultAzureCredential
    ):
        token_provider = get_bearer_token_provider(
            credential,
            "https://cognitiveservices.azure.com/.default"
        )
        
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version=api_version,
        )
        self.deployment = deployment
    
    def generate_completion(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate chat completion."""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
```

#### 3. Core Business Logic Modules

**src/pim_auto/core/pim_detector.py**:
```python
"""PIM activation detection module."""
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class PIMActivation:
    """Represents a PIM activation event."""
    user_email: str
    role_name: str
    activation_reason: str
    activation_time: datetime
    duration_hours: int


class PIMDetector:
    """Detects PIM activations from Azure Log Analytics."""
    
    def __init__(self, log_analytics_client):
        self.log_analytics_client = log_analytics_client
    
    def detect_activations(self, hours: int = 24) -> List[PIMActivation]:
        """Detect PIM activations in the specified time window."""
        query = f"""
        AuditLogs
        | where TimeGenerated > ago({hours}h)
        | where OperationName == "Add member to role completed (PIM activation)"
        | project
            TimeGenerated,
            UserEmail = tostring(InitiatedBy.user.userPrincipalName),
            RoleName = tostring(TargetResources[0].displayName),
            Reason = tostring(TargetResources[0].modifiedProperties[0].newValue)
        | order by TimeGenerated desc
        """
        
        results = self.log_analytics_client.execute_query(
            query=query,
            timespan=f"PT{hours}H"
        )
        
        activations = []
        for row in results:
            activations.append(PIMActivation(
                user_email=row["UserEmail"],
                role_name=row["RoleName"],
                activation_reason=row["Reason"],
                activation_time=row["TimeGenerated"],
                duration_hours=hours,  # Simplified: assume full window
            ))
        
        logger.info(f"Detected {len(activations)} PIM activations")
        return activations
```

**src/pim_auto/core/activity_correlator.py**:
```python
"""Activity correlation module."""
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ActivityEvent:
    """Represents an Azure activity event."""
    timestamp: datetime
    operation_name: str
    resource_type: str
    resource_name: str
    status: str


class ActivityCorrelator:
    """Correlates user activities with PIM activations."""
    
    def __init__(self, log_analytics_client):
        self.log_analytics_client = log_analytics_client
    
    def get_user_activities(
        self,
        user_email: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[ActivityEvent]:
        """Get all activities for a user in the specified time range."""
        query = f"""
        AzureActivity
        | where TimeGenerated between (datetime("{start_time.isoformat()}") .. datetime("{end_time.isoformat()}"))
        | where Caller == "{user_email}"
        | project
            TimeGenerated,
            OperationName,
            ResourceType,
            Resource,
            Status = ActivityStatus
        | order by TimeGenerated asc
        """
        
        results = self.log_analytics_client.execute_query(query=query, timespan=None)
        
        activities = []
        for row in results:
            activities.append(ActivityEvent(
                timestamp=row["TimeGenerated"],
                operation_name=row["OperationName"],
                resource_type=row.get("ResourceType", "Unknown"),
                resource_name=row.get("Resource", "Unknown"),
                status=row.get("Status", "Unknown"),
            ))
        
        logger.info(f"Found {len(activities)} activities for {user_email}")
        return activities
```

**src/pim_auto/core/query_generator.py**:
```python
"""KQL query generation using Azure OpenAI."""
import logging

logger = logging.getLogger(__name__)


class QueryGenerator:
    """Generates Kusto queries using Azure OpenAI."""
    
    def __init__(self, openai_client):
        self.openai_client = openai_client
    
    def generate_query(self, natural_language: str, max_retries: int = 2) -> str:
        """Generate KQL query from natural language."""
        system_prompt = """You are an expert in Kusto Query Language (KQL) for Azure Log Analytics.
        Generate valid KQL queries based on user requests.
        Focus on AuditLogs and AzureActivity tables.
        Return only the KQL query, no explanations."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate KQL query for: {natural_language}"}
        ]
        
        for attempt in range(max_retries + 1):
            try:
                query = self.openai_client.generate_completion(
                    messages=messages,
                    temperature=0.3,  # Lower temperature for more deterministic output
                )
                
                # Basic validation: check if it looks like KQL
                if any(keyword in query for keyword in ["AuditLogs", "AzureActivity", "where", "|"]):
                    logger.info(f"Generated query on attempt {attempt + 1}")
                    return query.strip()
                else:
                    if attempt < max_retries:
                        logger.warning(f"Generated query looks invalid, retrying (attempt {attempt + 1})")
                        messages.append({"role": "assistant", "content": query})
                        messages.append({"role": "user", "content": "That doesn't look like valid KQL. Please try again."})
                    else:
                        raise ValueError(f"Failed to generate valid query after {max_retries + 1} attempts")
            
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Query generation failed (attempt {attempt + 1}): {e}")
                else:
                    raise
        
        raise ValueError("Query generation failed")
```

**src/pim_auto/core/risk_assessor.py**:
```python
"""Risk assessment module using Azure OpenAI."""
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlignmentLevel(Enum):
    """Activity alignment levels."""
    ALIGNED = "aligned"
    PARTIALLY_ALIGNED = "partially_aligned"
    NOT_ALIGNED = "not_aligned"
    UNKNOWN = "unknown"


class RiskAssessment:
    """Risk assessment result."""
    
    def __init__(self, level: AlignmentLevel, explanation: str):
        self.level = level
        self.explanation = explanation


class RiskAssessor:
    """Assesses alignment between PIM reasons and activities."""
    
    def __init__(self, openai_client):
        self.openai_client = openai_client
    
    def assess_alignment(self, pim_reason: str, activities: list) -> RiskAssessment:
        """Assess if activities align with PIM activation reason."""
        activities_text = "\n".join([
            f"- {act.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {act.operation_name} on {act.resource_type}/{act.resource_name}"
            for act in activities
        ])
        
        system_prompt = """You are a security analyst assessing Azure PIM (Privileged Identity Management) activations.
        Determine if the user's activities during their elevated access period align with their stated reason for activation.
        Respond with one of: ALIGNED, PARTIALLY_ALIGNED, NOT_ALIGNED, UNKNOWN.
        Then provide a brief explanation."""
        
        user_prompt = f"""
        PIM Activation Reason: {pim_reason}
        
        Activities during elevation:
        {activities_text if activities else "No activities recorded"}
        
        Does the activity align with the stated reason?
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.openai_client.generate_completion(
            messages=messages,
            temperature=0.5,
        )
        
        # Parse response
        response_upper = response.upper()
        if "NOT_ALIGNED" in response_upper or "NOT ALIGNED" in response_upper:
            level = AlignmentLevel.NOT_ALIGNED
        elif "PARTIALLY_ALIGNED" in response_upper or "PARTIALLY ALIGNED" in response_upper:
            level = AlignmentLevel.PARTIALLY_ALIGNED
        elif "ALIGNED" in response_upper:
            level = AlignmentLevel.ALIGNED
        else:
            level = AlignmentLevel.UNKNOWN
        
        logger.info(f"Assessment: {level.value}")
        return RiskAssessment(level=level, explanation=response)
```

#### 4. Application Entry Point

**src/pim_auto/main.py** (basic version):
```python
"""Main entry point for PIM Auto application."""
import logging
import sys
from pim_auto.config import Config
from pim_auto.azure.auth import get_azure_credential
from pim_auto.azure.log_analytics import LogAnalyticsClient
from pim_auto.azure.openai_client import OpenAIClient
from pim_auto.core.pim_detector import PIMDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main application entry point."""
    try:
        # Load and validate configuration
        logger.info("Loading configuration...")
        config = Config.from_environment()
        config.validate()
        logger.info("Configuration loaded successfully")
        
        # Initialize Azure clients
        logger.info("Initializing Azure clients...")
        credential = get_azure_credential()
        
        log_analytics = LogAnalyticsClient(
            workspace_id=config.log_analytics_workspace_id,
            credential=credential
        )
        
        openai_client = OpenAIClient(
            endpoint=config.azure_openai_endpoint,
            deployment=config.azure_openai_deployment,
            api_version=config.azure_openai_api_version,
            credential=credential
        )
        
        logger.info("Azure clients initialized successfully")
        
        # Basic functionality test: detect PIM activations
        logger.info(f"Scanning for PIM activations (last {config.default_scan_hours} hours)...")
        pim_detector = PIMDetector(log_analytics)
        activations = pim_detector.detect_activations(hours=config.default_scan_hours)
        
        logger.info(f"Found {len(activations)} PIM activations")
        for activation in activations:
            logger.info(f"  - {activation.user_email}: {activation.role_name} (Reason: {activation.activation_reason})")
        
        return 0
    
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

#### 5. Unit Tests with Mocking

Create comprehensive unit tests that mock Azure services.

**tests/unit/test_pim_detector.py**:
```python
"""Tests for PIM detector module."""
from datetime import datetime
from unittest.mock import Mock, MagicMock
import pytest

from src.pim_auto.core.pim_detector import PIMDetector, PIMActivation


@pytest.fixture
def mock_log_analytics():
    """Mock Log Analytics client."""
    client = Mock()
    client.execute_query = MagicMock(return_value=[
        {
            "TimeGenerated": datetime(2026, 2, 10, 10, 0, 0),
            "UserEmail": "john.doe@contoso.com",
            "RoleName": "Contributor",
            "Reason": "need to add a storage account"
        },
        {
            "TimeGenerated": datetime(2026, 2, 10, 11, 0, 0),
            "UserEmail": "jane.smith@contoso.com",
            "RoleName": "Owner",
            "Reason": "emergency production fix"
        }
    ])
    return client


def test_detect_activations(mock_log_analytics):
    """Test PIM activation detection."""
    detector = PIMDetector(mock_log_analytics)
    activations = detector.detect_activations(hours=24)
    
    assert len(activations) == 2
    assert activations[0].user_email == "john.doe@contoso.com"
    assert activations[0].role_name == "Contributor"
    assert activations[0].activation_reason == "need to add a storage account"
    assert activations[1].user_email == "jane.smith@contoso.com"


def test_detect_activations_empty(mock_log_analytics):
    """Test PIM detection with no results."""
    mock_log_analytics.execute_query.return_value = []
    
    detector = PIMDetector(mock_log_analytics)
    activations = detector.detect_activations(hours=24)
    
    assert len(activations) == 0
```

**tests/unit/test_risk_assessor.py**:
```python
"""Tests for risk assessor module."""
from unittest.mock import Mock
from datetime import datetime
import pytest

from src.pim_auto.core.risk_assessor import RiskAssessor, AlignmentLevel
from src.pim_auto.core.activity_correlator import ActivityEvent


@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    client = Mock()
    return client


def test_assess_aligned(mock_openai):
    """Test aligned assessment."""
    mock_openai.generate_completion.return_value = "ALIGNED: The user created a storage account as stated."
    
    assessor = RiskAssessor(mock_openai)
    activities = [
        ActivityEvent(
            timestamp=datetime(2026, 2, 10, 10, 30),
            operation_name="Create Storage Account",
            resource_type="Microsoft.Storage/storageAccounts",
            resource_name="mystorageaccount",
            status="Succeeded"
        )
    ]
    
    assessment = assessor.assess_alignment(
        pim_reason="need to add a storage account",
        activities=activities
    )
    
    assert assessment.level == AlignmentLevel.ALIGNED


def test_assess_not_aligned(mock_openai):
    """Test not aligned assessment."""
    mock_openai.generate_completion.return_value = "NOT_ALIGNED: Activities don't match the stated reason."
    
    assessor = RiskAssessor(mock_openai)
    activities = [
        ActivityEvent(
            timestamp=datetime(2026, 2, 10, 10, 30),
            operation_name="Delete Virtual Machine",
            resource_type="Microsoft.Compute/virtualMachines",
            resource_name="prod-vm-01",
            status="Succeeded"
        )
    ]
    
    assessment = assessor.assess_alignment(
        pim_reason="need to add a storage account",
        activities=activities
    )
    
    assert assessment.level == AlignmentLevel.NOT_ALIGNED
```

### Exit Criteria

**Must Pass**:
- ✅ All core modules implemented (PIM detector, activity correlator, query generator, risk assessor)
- ✅ Azure client wrappers functional
- ✅ Configuration management working
- ✅ Unit tests pass with >80% coverage
- ✅ Linting and type checking pass
- ✅ Docker image builds and runs basic functionality
- ✅ CI/CD pipeline passing
- ✅ Basic end-to-end smoke test works (with real Azure resources in dev environment)

**Deliverables**:
- Complete `src/pim_auto/` implementation
- Comprehensive unit tests with mocking
- Updated `Dockerfile` with working application
- Integration test documentation

**Success Criteria**:
A developer can:
1. Set Azure environment variables
2. Run `python src/pim_auto/main.py`
3. See PIM activations detected from their Azure tenant
4. All unit tests pass

### Rollback Plan

**If Slice 1 fails**:
1. Revert all files in `src/pim_auto/` (except `__init__.py` placeholders)
2. Revert test files in `tests/unit/`
3. Revert `Dockerfile` to Slice 0 version
4. Repository returns to Slice 0 state (infrastructure only, no business logic)

**Risk**: Medium - business logic implementation may have bugs, but limited to dev/test environments

---

## Slice 2: Dual-Mode Support (Interactive CLI and Batch Mode)

### Purpose

Implement the two operational modes specified in the requirements: interactive chat interface and batch processing mode.

### Objectives

1. Implement interactive CLI with command parsing
2. Implement conversation context management
3. Implement batch mode runner
4. Implement report generation (Markdown format)
5. Add mode router in main entry point
6. Create integration tests for both modes
7. Update documentation with usage examples

### Entry Criteria

✅ Slice 1 completed and merged  
✅ Core modules tested and working  
✅ Azure integration verified in dev environment  

### Detailed Changes

#### 1. Interactive CLI Interface

**src/pim_auto/interfaces/interactive_cli.py**:
- Command loop with `input()` or `rich` library
- Commands: `scan`, `What did <user> do?`, `assess <user>`, `exit`
- Conversation context management
- Formatted console output with emoji and colors

#### 2. Batch Mode Runner

**src/pim_auto/interfaces/batch_runner.py**:
- Automated scanning (no user input)
- Iterate through all detected PIM activations
- Collect activities and assessments for each user
- Generate comprehensive Markdown report

#### 3. Report Generator

**src/pim_auto/reporting/markdown_generator.py**:
- Format PIM activations as Markdown table
- Format activity timelines
- Format risk assessments with color coding
- Support output to file or stdout

#### 4. Updated Main Entry Point

**src/pim_auto/main.py** (full version):
- Parse `--mode` flag (interactive vs. batch)
- Route to appropriate interface
- Handle errors and logging per mode

### Exit Criteria

**Must Pass**:
- ✅ Interactive mode works: user can scan, query, assess
- ✅ Batch mode works: automated report generation
- ✅ Both modes tested via integration tests
- ✅ Documentation updated with examples
- ✅ CI/CD pipeline passing

**Deliverables**:
- `src/pim_auto/interfaces/` implementation
- `src/pim_auto/reporting/` implementation
- Integration tests
- Usage documentation

### Rollback Plan

**If Slice 2 fails**:
- Revert interface and reporting modules
- Revert main.py to Slice 1 version (basic scan only)
- Core functionality (Slice 1) remains intact

**Risk**: Low - interface layer is separate from core logic

---

## Slice 3: Production Readiness (Deployment and Monitoring)

### Purpose

Prepare the application for production deployment with comprehensive monitoring, operational runbook, and deployment automation.

### Objectives

1. Create Azure deployment scripts (Bicep or Terraform)
2. Integrate Application Insights for monitoring
3. Implement structured logging (JSON format)
4. Add health check endpoints
5. Create deployment documentation
6. Update operational runbook
7. Set up monitoring dashboards and alerts

### Entry Criteria

✅ Slice 2 completed and merged  
✅ Both operational modes working  
✅ Application tested in dev environment  

### Detailed Changes

#### 1. Infrastructure as Code

**infrastructure/bicep/main.bicep**:
- Azure Container Registry
- Azure Container Apps (or ACI)
- Managed Identity
- RBAC role assignments
- Application Insights

#### 2. Monitoring Integration

- Application Insights SDK integration
- Custom metrics (PIM detections, assessments, API calls)
- Distributed tracing
- Alert rules

#### 3. Operational Documentation

- Update `/docs/Runbook.md` with deployment procedures
- Troubleshooting guide
- Monitoring dashboard setup

### Exit Criteria

**Must Pass**:
- ✅ Application deploys to Azure successfully
- ✅ Monitoring and logging working
- ✅ Health checks functional
- ✅ Runbook complete
- ✅ Alerts configured

**Deliverables**:
- IaC templates (Bicep/Terraform)
- Updated runbook
- Monitoring setup guide

### Rollback Plan

**If Slice 3 fails**:
- Remove Azure resources via IaC
- Application remains deployable via Docker (manual deployment)

**Risk**: Low - deployment automation doesn't affect application functionality

---

## Slice 4: End-to-End Validation and Documentation

### Purpose

Comprehensive testing, validation, and documentation finalization before production release.

### Objectives

1. Run end-to-end tests in staging environment
2. Performance testing (query latency, OpenAI costs)
3. Security review (RBAC, secrets, container scanning)
4. Final documentation review and updates
5. User acceptance testing (UAT) with sample scenarios
6. Create release notes

### Entry Criteria

✅ Slice 3 completed and merged  
✅ Application deployed to staging environment  
✅ All previous acceptance criteria met  

### Activities

1. **End-to-End Testing**:
   - Test interactive mode with real user scenarios
   - Test batch mode with scheduled execution
   - Verify report accuracy against manual audit

2. **Performance Validation**:
   - Measure query execution times
   - Calculate OpenAI token usage and costs
   - Verify acceptable response times

3. **Security Review**:
   - Verify RBAC permissions (least privilege)
   - Scan container for vulnerabilities
   - Review logging (no sensitive data leaks)
   - Audit authentication flow

4. **Documentation Finalization**:
   - Update all docs with actual implementation details
   - Create user guide with screenshots
   - Finalize runbook with actual commands
   - Update README.md with deployment instructions

### Exit Criteria

**Must Pass**:
- ✅ All end-to-end tests pass
- ✅ Performance acceptable (defined SLAs)
- ✅ Security review complete with no high-severity issues
- ✅ Documentation complete and accurate
- ✅ User acceptance criteria met

**Deliverables**:
- E2E test results
- Performance test report
- Security audit report
- Final documentation set
- Release notes (v1.0.0)

### Rollback Plan

**If Slice 4 identifies critical issues**:
- Address issues in hotfix branch
- Re-test and re-validate
- Do NOT proceed to production until all issues resolved

**Risk**: Very low - this is validation phase, not implementation

---

## Risk Assessment and Mitigation

### Technical Risks

| Risk | Impact | Probability | Mitigation | Contingency |
|------|--------|-------------|------------|-------------|
| Azure OpenAI quota limits | High | Medium | Request quota increase early, implement caching | Use throttling, retry logic |
| Log Analytics schema changes | High | Low | Version KQL queries, add schema validation | Quick hotfix if schema breaks |
| Python dependency vulnerabilities | Medium | Medium | Automated scanning (Dependabot), regular updates | Security patches via CI/CD |
| Container security issues | High | Low | Automated scanning, minimal base image | Rebuild with patched base image |
| Test environment availability | Medium | Low | Use dedicated dev/test Azure resources | Have backup test environment |

### Project Risks

| Risk | Impact | Probability | Mitigation | Contingency |
|------|--------|-------------|------------|-------------|
| Scope creep during implementation | Medium | Medium | Strict adherence to specification, change control | Defer non-critical features to future slices |
| Implementation takes longer than estimated | Low | High | Realistic estimates, buffer time, frequent progress reviews | Adjust timeline, prioritize critical slices |
| Azure service costs exceed budget | Medium | Medium | Cost monitoring, usage alerts, query optimization | Implement caching, reduce query frequency |
| Insufficient Azure permissions in production | High | Low | Test RBAC early, document required permissions | Work with Azure admins to fix permissions |
| Team lacks Azure or Python expertise | Medium | Low | Training, documentation, use of AI agents for guidance | Engage external expertise if needed |

### Operational Risks

| Risk | Impact | Probability | Mitigation | Contingency |
|------|--------|-------------|------------|-------------|
| Application misconfiguration in production | High | Medium | Configuration validation, IaC, testing | Runbook for quick reconfiguration |
| Azure service outage | High | Low | Monitor Azure status, implement retry logic | Accept temporary downtime, alert users |
| False positives in risk assessment | Medium | High | Tune AI prompts, allow human review | Iterative improvement based on feedback |
| User adoption challenges | Medium | Medium | Documentation, training, user feedback | Iterate on UX based on feedback |

---

## Acceptance Criteria Summary

The migration plan is considered successful if:

✅ **All slices completed**: Slice 0 through Slice 4  
✅ **All functionality implemented**: Matches README.md specification  
✅ **Both modes working**: Interactive and batch modes operational  
✅ **Tests passing**: Unit, integration, and E2E tests green  
✅ **Deployed to Azure**: Working in production environment  
✅ **Monitoring active**: Logs, metrics, alerts configured  
✅ **Documentation complete**: All docs updated and accurate  
✅ **No high-severity security issues**: Security review passed  
✅ **User acceptance**: Sample users can successfully use the application  
✅ **Rollback capability verified**: Tested rollback procedure  

---

## Next Actions for Implementation Agent

Once this Migration Plan is approved:

1. **Start with Slice 0**:
   - Create project structure
   - Set up dependencies and tooling
   - Configure CI/CD pipeline
   - Deliver via PR for review

2. **After Slice 0 approval, proceed to Slice 1**:
   - Implement core Azure integration
   - Implement business logic modules
   - Create comprehensive tests
   - Deliver via PR for review

3. **Continue sequentially** through remaining slices

4. **At each phase boundary**:
   - Verify exit criteria
   - Get human approval
   - Update this document with actual results
   - Proceed to next slice

---

## References

- `/README.md`: Original specification (functional requirements)
- `/docs/Target-Architecture.md`: Target architecture (this plan implements)
- `/docs/HLD.md`: Current state high-level design
- `/docs/LLD.md`: Current state low-level design
- `/docs/ADR/ADR-001-agent-based-governance.md`: Development governance model
- `/docs/ADR/ADR-002-specification-first-development.md`: Spec-first approach
- `/docs/ADR/ADR-003-azure-native-architecture.md`: Azure dependencies
- `/docs/ADR/ADR-004-dual-mode-operation.md`: Interactive and batch modes
- `/.github/agents/implementation.agent.md`: Implementation agent instructions
- `/.github/agents/testing.agent.md`: Testing agent instructions
- `/.github/skills/incremental-refactoring.skill.md`: Refactoring methodology

---

## Appendix: Glossary

- **Slice**: A small, incremental unit of work that delivers verifiable value
- **Strangler Pattern**: Incremental modernization approach (gradually replace old system)
- **Baseline Testing**: Minimal tests that validate infrastructure (before business logic)
- **Entry Criteria**: Conditions that must be met before starting a slice
- **Exit Criteria**: Conditions that must be met before completing a slice
- **Rollback Plan**: Procedure to undo changes if a slice fails
- **IaC**: Infrastructure as Code (Bicep, Terraform)
- **E2E**: End-to-end (full user workflow testing)
- **UAT**: User Acceptance Testing
- **RBAC**: Role-Based Access Control (Azure permissions)
- **KQL**: Kusto Query Language (Azure Log Analytics)
