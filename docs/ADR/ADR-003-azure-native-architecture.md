# ADR-003: Azure-Native Architecture

**Status**: Specified (Not Yet Implemented)  
**Date**: 2026-02-10  
**Decision Makers**: Repository Owner (implicit)

## Context

The PIM Activity Audit Agent needs:
1. AI/ML capabilities for natural language processing and query generation
2. Access to Azure AD PIM activation logs
3. Access to Azure resource activity logs
4. Secure authentication without managing credentials

These capabilities could be provided by:
- Cloud-native Azure services
- Self-hosted open-source alternatives
- Hybrid approach (some cloud, some local)

## Decision

The application adopts an **Azure-native architecture** with hard dependencies on Azure platform services.

### Core Dependencies (from README.md specification)

1. **Azure OpenAI Service**:
   - Purpose: Natural language understanding and Kusto query generation
   - Model: GPT-4o deployment required
   - No fallback to OpenAI.com or other providers

2. **Azure Log Analytics**:
   - Purpose: Source of truth for PIM activations and Azure activities
   - Tables: AuditLogs, AzureActivity
   - No local database or alternative data source

3. **Azure Authentication (DefaultAzureCredential)**:
   - Purpose: Secure credential-free authentication
   - Supports: Managed Identity (production), Azure CLI (local dev)
   - No username/password or API key options

## Rationale

### Advantages

1. **Integrated Security**: Azure AD/Managed Identity eliminates credential management
2. **Data Locality**: PIM logs are already in Azure, no data export needed
3. **Compliance**: Keeps security audit data within Azure boundary
4. **Operational Simplicity**: No infrastructure to manage beyond configuration
5. **Feature Alignment**: Azure OpenAI is tightly integrated with Azure security model

### Trade-offs

1. **Vendor Lock-In**: Cannot run without Azure subscription
2. **Cost Model**: Usage-based pricing for OpenAI and Log Analytics queries
3. **Service Availability**: Dependent on Azure service uptime
4. **Development Environment**: Requires Azure subscription even for local development
5. **Testing Complexity**: Integration tests need Azure resources or extensive mocking

## Consequences

### Positive

- Simple authentication model (no secrets to manage)
- Direct access to source data (no ETL pipelines)
- Leverages Azure's enterprise security features
- Aligns with PIM usage (organizations using PIM are already on Azure)

### Negative

- Cannot run offline or in non-Azure environments
- Azure service costs may be unpredictable (especially AI queries)
- Multi-cloud organizations cannot use this tool for non-Azure PIM
- Requires Azure expertise from developers and operators

### Neutral

- Development requires Azure subscription
- Testing strategy must account for Azure service mocking
- Local development uses Azure CLI authentication

## Technical Implications

### Required Azure Resources

To run this application, an organization must provision:

1. **Azure OpenAI Service**:
   - GPT-4o model deployment
   - Sufficient quota for query generation workload
   - Same region as Log Analytics (recommended) for latency

2. **Log Analytics Workspace**:
   - Connected to Azure AD (for AuditLogs)
   - Connected to Azure subscriptions (for AzureActivity)
   - Retention policy appropriate for audit requirements

3. **Azure AD/Entra ID**:
   - PIM enabled (prerequisite for monitoring)
   - Appropriate RBAC roles:
     - Log Analytics Reader (minimum)
     - Potentially higher for action group integration

### Cost Structure

- **Azure OpenAI**: Per-token pricing for GPT-4o (variable based on usage)
- **Log Analytics**: Per-GB ingestion + per-query execution cost
- **Authentication**: No direct cost (included with Azure AD)

### Failure Modes

The application will fail completely if:
- Azure OpenAI endpoint is unavailable or quota exceeded
- Log Analytics workspace is inaccessible
- Azure authentication fails (expired credentials, insufficient permissions)

No degraded operation mode is specified.

## Alternative Architectures Considered

### Alternative 1: Multi-Cloud with Open-Source AI

Use open-source LLM (Llama, Mistral) hosted locally or on other cloud providers.

**Rejected because**: 
- PIM logs are Azure-specific anyway
- Managing LLM infrastructure adds complexity
- Azure OpenAI provides enterprise-grade compliance
- Specification explicitly requires Azure OpenAI

### Alternative 2: Hybrid with Local Database

Export logs to local database, reduce Azure query costs.

**Rejected because**:
- Adds ETL complexity
- Duplicates security audit data (compliance risk)
- Increases latency
- Specification calls for real-time querying

### Alternative 3: OpenAI.com Instead of Azure OpenAI

Use OpenAI's hosted service instead of Azure OpenAI.

**Rejected because**:
- Data residency concerns (sending audit logs to OpenAI)
- No Azure AD integration
- Separate billing/security model
- Specification explicitly requires Azure OpenAI

## Local Development Impact

Developers must:
1. Have an Azure subscription (personal or shared dev environment)
2. Install Azure CLI and authenticate locally
3. Configure environment variables for Azure endpoints
4. Accept that "fully local" development is not possible

Testing implications:
- Unit tests must mock Azure SDK calls
- Integration tests may require Azure sandbox environment
- E2E tests require real Azure resources (or very sophisticated mocks)

## Migration/Portability Considerations

If the organization needs to migrate away from Azure in the future:
- PIM monitoring would need complete redesign (PIM is Azure-specific)
- AI query generation could be ported to other LLM providers
- Activity log querying would need equivalent data source

**Assessment**: Low portability is acceptable since PIM itself is Azure-only.

## References

- `/README.md`: Specification explicitly requires "Azure OpenAI service" and "Log Analytics workspace"
- `DefaultAzureCredential` pattern: Azure SDK authentication standard
- Non-functional requirement #3: "Must authenticate securely using Azure DefaultAzureCredential"
