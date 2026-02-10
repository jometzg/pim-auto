# ADR-007: Configuration Management Strategy

**Status**: Proposed  
**Date**: 2026-02-10  
**Decision Makers**: Modernization Agent (pending human approval)

## Context

The PIM Auto application requires configuration for:
- Azure service endpoints (OpenAI, Log Analytics)
- Operational parameters (scan window, log level)
- Deployment-specific settings (batch output path)
- Secrets management (if any)

The application will run in multiple environments:
- Local development (developer laptops)
- CI/CD pipelines (GitHub Actions)
- Azure Container Instances or Apps (dev, staging, production)

Different environments require different configuration values, but the application code must remain the same across all environments.

Additionally, per ADR-003 (Azure-Native Architecture), the application uses DefaultAzureCredential for authentication, which means NO API keys or connection strings should be stored.

## Decision

Adopt **Environment Variable-Based Configuration** following the **12-Factor App** methodology:

### Configuration Source Priority

1. **Environment Variables** (primary source):
   - Required for all deployments
   - Set by container platform or shell environment
   - No default values for secrets or endpoints

2. **Validation at Startup**:
   - Application validates all required configuration present
   - Fails fast with clear error messages
   - Logs configuration (redacting sensitive values)

3. **No Configuration Files**:
   - No `config.json`, `appsettings.json`, or `.env` files committed to repo
   - `.env` files MAY be used locally (gitignored) but are NOT the primary mechanism

### Required Configuration Parameters

| Parameter | Environment Variable | Type | Required | Default | Example |
|-----------|---------------------|------|----------|---------|---------|
| Azure OpenAI Endpoint | `AZURE_OPENAI_ENDPOINT` | URL | Yes | None | `https://my-openai.openai.azure.com/` |
| Azure OpenAI Deployment | `AZURE_OPENAI_DEPLOYMENT` | String | Yes | None | `gpt-4o` |
| Azure OpenAI API Version | `AZURE_OPENAI_API_VERSION` | String | No | `2024-02-15-preview` | `2024-02-15-preview` |
| Log Analytics Workspace ID | `LOG_ANALYTICS_WORKSPACE_ID` | GUID | Yes | None | `abc12345-...` |
| Log Analytics Region | `LOG_ANALYTICS_REGION` | String | No | None | `eastus` |
| Default Scan Hours | `DEFAULT_SCAN_HOURS` | Integer | No | `24` | `24` |
| Log Level | `LOG_LEVEL` | String | No | `INFO` | `INFO`, `DEBUG`, `WARNING` |
| Batch Output Path | `BATCH_OUTPUT_PATH` | Path | No | stdout | `/output/report.md` |

### Secrets Management

**No Secrets Required**: The application uses Azure managed identity (DefaultAzureCredential), which eliminates the need for:
- API keys
- Connection strings
- Passwords
- Service principal credentials

If future requirements introduce secrets (unlikely), use Azure Key Vault with managed identity access.

### Configuration Class Design

```python
from dataclasses import dataclass
import os

@dataclass
class Config:
    """Application configuration loaded from environment."""
    
    azure_openai_endpoint: str
    azure_openai_deployment: str
    azure_openai_api_version: str = "2024-02-15-preview"
    log_analytics_workspace_id: str
    log_analytics_region: str | None = None
    default_scan_hours: int = 24
    log_level: str = "INFO"
    batch_output_path: str | None = None
    
    @classmethod
    def from_environment(cls) -> "Config":
        """Load configuration from environment variables with validation."""
        required_vars = {
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT",
            "LOG_ANALYTICS_WORKSPACE_ID",
        }
        
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please set these variables before running the application."
            )
        
        return cls(
            azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_openai_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            # ... (other parameters)
        )
    
    def validate(self) -> None:
        """Validate configuration values."""
        if not self.azure_openai_endpoint.startswith("https://"):
            raise ValueError("Azure OpenAI endpoint must use HTTPS")
        
        if self.default_scan_hours < 1 or self.default_scan_hours > 168:
            raise ValueError("Scan hours must be between 1 and 168 (1 week)")
        
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {self.log_level}")
```

## Rationale

### Advantages of Environment Variables

1. **12-Factor Compliance**:
   - Standard cloud-native configuration pattern
   - Language-agnostic (works with any runtime)
   - Supported by all container platforms

2. **Environment Separation**:
   - Different values per environment (dev, staging, prod)
   - No risk of committing production config to Git
   - Clear separation between code and configuration

3. **Container-Friendly**:
   - Docker, ACI, ACA all support environment variables
   - Easy to set via container platform UIs or IaC
   - No file mounting or volume management needed

4. **Security**:
   - No secrets in code or config files
   - Environment variables can be set securely (Key Vault references in ACA)
   - Azure managed identity eliminates most secrets

5. **Simplicity**:
   - No configuration file parsing logic
   - Standard Python `os.getenv()` API
   - Easy to understand and debug

### Trade-offs

1. **Limited Structure**:
   - Environment variables are flat (no nested objects)
   - Mitigated by: Simple configuration needs (no deep nesting required)

2. **Type Safety**:
   - Environment variables are always strings
   - Mitigated by: Type conversion and validation in Config class

3. **Local Development**:
   - Developer must set environment variables manually
   - Mitigated by: Documentation, example `.env.example` file (not committed)

4. **Visibility**:
   - Environment variables visible to process and child processes
   - Mitigated by: No secrets in environment variables (managed identity)

## Consequences

### Positive

- **No configuration drift**: Code is identical across environments
- **No secrets in Git**: Impossible to commit secrets accidentally
- **Easy CI/CD**: GitHub Actions can set environment variables easily
- **Cloud-native**: Aligns with Azure Container Apps best practices
- **Testable**: Easy to mock configuration in tests

### Negative

- **Developer setup**: Each developer must set environment variables
  - Mitigation: Clear documentation in Developer-Setup.md
  - Mitigation: Example `.env.example` file (not committed, not loaded by app)
- **No hierarchical config**: Cannot nest configuration objects
  - Mitigation: Flat configuration is sufficient for this application

### Neutral

- **Configuration changes require restart**: Not configuration hot-reload
  - Acceptable: Configuration rarely changes, restarts are fast (~5 seconds)

## Implementation Details

### Local Development Setup

**Developer Setup Guide** includes:

```bash
# Set environment variables (option 1: directly)
export AZURE_OPENAI_ENDPOINT="https://my-openai.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="gpt-4o"
export LOG_ANALYTICS_WORKSPACE_ID="abc12345-..."

# Or (option 2: source from file - not committed)
# Create .env file (NOT committed to Git):
# AZURE_OPENAI_ENDPOINT=https://my-openai.openai.azure.com/
# AZURE_OPENAI_DEPLOYMENT=gpt-4o
# LOG_ANALYTICS_WORKSPACE_ID=abc12345-...

# Then source it:
export $(cat .env | xargs)

# Run application
python -m src.pim_auto.main
```

**`.env.example`** (committed to Git as template):
```
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Log Analytics Configuration
LOG_ANALYTICS_WORKSPACE_ID=your-workspace-id-here
LOG_ANALYTICS_REGION=eastus

# Application Settings
DEFAULT_SCAN_HOURS=24
LOG_LEVEL=INFO
BATCH_OUTPUT_PATH=/output/report.md
```

**`.gitignore`** includes:
```
.env
.env.local
```

### Container Deployment

**Docker Run** (local testing):
```bash
docker run \
  -e AZURE_OPENAI_ENDPOINT="https://..." \
  -e AZURE_OPENAI_DEPLOYMENT="gpt-4o" \
  -e LOG_ANALYTICS_WORKSPACE_ID="abc123..." \
  pim-auto:latest
```

**Azure Container Apps** (production):
```bash
# Via CLI
az containerapp create \
  --name pim-auto \
  --resource-group my-rg \
  --environment my-env \
  --image myacr.azurecr.io/pim-auto:1.0.0 \
  --env-vars \
    AZURE_OPENAI_ENDPOINT=https://... \
    AZURE_OPENAI_DEPLOYMENT=gpt-4o \
    LOG_ANALYTICS_WORKSPACE_ID=abc123... \
  --registry-server myacr.azurecr.io \
  --managed-identity system
```

**Via Bicep IaC**:
```bicep
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'pim-auto'
  properties: {
    configuration: {
      secrets: []  // No secrets needed (managed identity)
    }
    template: {
      containers: [
        {
          name: 'pim-auto'
          image: 'myacr.azurecr.io/pim-auto:1.0.0'
          env: [
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: 'https://my-openai.openai.azure.com/'
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT'
              value: 'gpt-4o'
            }
            {
              name: 'LOG_ANALYTICS_WORKSPACE_ID'
              value: logAnalyticsWorkspace.properties.customerId
            }
            {
              name: 'LOG_LEVEL'
              value: 'INFO'
            }
          ]
        }
      ]
    }
  }
}
```

### CI/CD Pipeline

**GitHub Actions** workflow:
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      # Test environment uses mock values
      AZURE_OPENAI_ENDPOINT: "https://test-openai.openai.azure.com/"
      AZURE_OPENAI_DEPLOYMENT: "gpt-4o"
      LOG_ANALYTICS_WORKSPACE_ID: "test-workspace-id"
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: pytest  # Tests use environment variables or mocks
```

### Configuration Validation

Application validates configuration at startup:

```python
def main():
    try:
        # Load configuration
        config = Config.from_environment()
        config.validate()
        logger.info("Configuration loaded and validated successfully")
        
        # Log configuration (redact sensitive values if any)
        logger.info(f"Azure OpenAI Endpoint: {config.azure_openai_endpoint}")
        logger.info(f"Log Analytics Workspace: {config.log_analytics_workspace_id[:8]}...")
        logger.info(f"Default Scan Hours: {config.default_scan_hours}")
        logger.info(f"Log Level: {config.log_level}")
        
        # Continue with application logic...
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your environment variables and try again.")
        sys.exit(1)
```

If configuration is invalid, application exits immediately with clear error message. No silent failures.

## Alternatives Considered

### Alternative 1: Configuration Files (JSON/YAML)

Use `config.json` or `appsettings.json` for configuration.

**Rejected because**:
- Risk of committing secrets to Git
- Must manage different config files per environment
- Requires mounting config files in containers
- Not aligned with 12-factor app principles
- Adds complexity (file parsing, validation)

### Alternative 2: Azure App Configuration Service

Use Azure App Configuration for centralized configuration management.

**Rejected because**:
- Overkill for simple application (11 configuration parameters)
- Adds dependency on another Azure service
- Increases complexity and cost
- Configuration rarely changes (not dynamic)
- Environment variables are sufficient

### Alternative 3: Command-Line Arguments

Pass configuration via command-line flags.

**Rejected because**:
- Not suitable for containerized deployments
- Docker/ACA cannot easily pass many command-line arguments
- Environment variables are more flexible
- Mixing modes (--mode batch) with config flags is confusing

### Alternative 4: Hardcoded Configuration

Hardcode configuration in source code.

**Rejected because**:
- Violates separation of code and configuration
- Requires code changes for different environments
- Cannot change configuration without rebuilding
- Unacceptable security practice

## Alignment with Existing ADRs

- **ADR-003 (Azure-Native)**: Managed identity eliminates secrets, simplifies configuration
- **ADR-004 (Dual-Mode Operation)**: Mode selection via command-line flag (not configuration)
- **ADR-005 (Containerization)**: Environment variables are container-native configuration method

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Developer forgets to set environment variables | Clear error messages at startup, detailed Developer-Setup.md |
| Production misconfiguration | Validation at startup, IaC templates with correct values |
| Secrets accidentally in environment variables | Use managed identity (no secrets), code review checks |
| Configuration drift between environments | IaC templates version-controlled, automated deployments |

## Testing Strategy

### Unit Tests

Mock configuration in tests:
```python
@pytest.fixture
def test_config():
    return Config(
        azure_openai_endpoint="https://test.openai.azure.com/",
        azure_openai_deployment="gpt-4o",
        log_analytics_workspace_id="test-workspace-id",
    )

def test_pim_detector(test_config):
    # Use test_config in tests
    ...
```

### Integration Tests

Set environment variables in CI pipeline:
```yaml
env:
  AZURE_OPENAI_ENDPOINT: "https://test.openai.azure.com/"
  # ...
```

### Configuration Validation Tests

```python
def test_config_missing_required_var(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    
    with pytest.raises(ValueError, match="Missing required environment variables"):
        Config.from_environment()

def test_config_invalid_endpoint():
    config = Config(
        azure_openai_endpoint="http://insecure.com",  # Not HTTPS
        # ...
    )
    
    with pytest.raises(ValueError, match="must use HTTPS"):
        config.validate()
```

## Success Criteria

This ADR is successfully implemented when:

✅ All configuration loaded from environment variables  
✅ No configuration files committed to Git (except `.env.example`)  
✅ Configuration validated at startup with clear error messages  
✅ Documentation includes configuration setup instructions  
✅ Developer-Setup.md has example `.env` configuration  
✅ IaC templates include all required environment variables  
✅ Tests mock configuration appropriately  

## Documentation Requirements

### Developer-Setup.md

- List all environment variables
- Provide example values
- Explain how to set variables (export, .env file)
- Troubleshooting section for common config errors

### Runbook.md

- Production environment variables
- How to update configuration in Azure Container Apps
- Validation steps after config changes

### README.md

- Link to configuration documentation
- Prerequisites section mentions environment variables

## Review and Approval

- **Proposed by**: Modernization Agent
- **Review Status**: Pending human review
- **Approval Date**: TBD
- **Implementation Status**: Not yet started (will begin in Slice 1)

## References

- [The Twelve-Factor App - Configuration](https://12factor.net/config)
- [Azure Container Apps - Environment Variables](https://learn.microsoft.com/en-us/azure/container-apps/environment-variables)
- [Python dataclasses documentation](https://docs.python.org/3/library/dataclasses.html)
- `/docs/Migration-Plan.md`: Slice 1 configuration implementation details
