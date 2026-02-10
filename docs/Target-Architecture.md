# Target Architecture - PIM Auto

**Document Status**: Proposed  
**Last Updated**: 2026-02-10  
**Repository**: jometzg/pim-auto  
**Purpose**: Define the target containerized architecture for incremental modernization

## Executive Summary

This document proposes a target architecture for the PIM Auto application that enables:
- Container-based deployment for portability and operational consistency
- Modular service boundaries aligned with domain responsibilities
- Incremental migration from specification to production-ready system
- Preservation of all specified behavior in the monolith specification (README.md)

The architecture supports both operational modes (interactive chat and batch) while preparing for future service extraction through clear internal boundaries.

## Current State Reference

As documented in `/docs/HLD.md`, the repository currently contains:
- Complete specification in `/README.md`
- Agent-based governance infrastructure
- No implementation code

This target architecture describes the **intended state** after initial implementation and subsequent incremental modernization.

## Architectural Principles

1. **Container-First**: All components deployed as containers for consistency
2. **Strangler Pattern**: Incremental extraction, starting with monolith
3. **Behavior Preservation**: No functional changes during modernization
4. **Azure-Native**: Maintain Azure service dependencies (per ADR-003)
5. **Dual-Mode Support**: Both interactive and batch modes (per ADR-004)

## Target Service Boundaries

### Phase 1: Containerized Monolith (Slice 0-1)

The initial implementation will be a single containerized Python application with clear internal module boundaries.

```
┌─────────────────────────────────────────────────────────────┐
│           PIM Auto Container (Monolith)                      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  CLI Interface Layer                                  │  │
│  │  - Interactive mode handler                           │  │
│  │  - Batch mode handler                                 │  │
│  │  - Mode router (main.py)                              │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │  Core Application Logic                              │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │ PIM         │  │ Activity     │  │ Risk       │  │  │
│  │  │ Detector    │  │ Correlator   │  │ Assessor   │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────┘  │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌──────────────┐                  │  │
│  │  │ Query       │  │ Report       │                  │  │
│  │  │ Generator   │  │ Generator    │                  │  │
│  │  └─────────────┘  └──────────────┘                  │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │  Azure Integration Layer                             │  │
│  │  - OpenAI client wrapper                             │  │
│  │  - Log Analytics client wrapper                      │  │
│  │  - Authentication (DefaultAzureCredential)           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼────┐   ┌───▼─────┐   ┌──▼──────┐
    │ Azure   │   │   Log   │   │  Azure  │
    │ OpenAI  │   │Analytics│   │   AD    │
    └─────────┘   └─────────┘   └─────────┘
```

### Internal Module Boundaries (Logical Services)

Even within the monolith, code will be organized into clear modules that represent future service boundaries:

#### 1. PIM Detection Module
**Responsibility**: Detect and extract PIM activations from Azure Log Analytics  
**Inputs**: Time range (default: 24 hours)  
**Outputs**: List of PIM activations with user, reason, timestamp  
**External Dependencies**: Azure Log Analytics (AuditLogs table)  
**Future State**: Could be extracted as a standalone service

#### 2. Activity Correlation Module
**Responsibility**: Query and aggregate Azure resource activities for specific users and time ranges  
**Inputs**: User identity, time range  
**Outputs**: Timestamped activity timeline  
**External Dependencies**: Azure Log Analytics (AzureActivity table)  
**Future State**: Could be extracted as a standalone service

#### 3. Query Generation Module
**Responsibility**: Generate and self-correct Kusto queries using Azure OpenAI  
**Inputs**: Natural language queries or structured query requests  
**Outputs**: Valid KQL queries  
**External Dependencies**: Azure OpenAI Service  
**Future State**: Could be extracted as a standalone AI service

#### 4. Risk Assessment Module
**Responsibility**: Evaluate alignment between stated PIM reasons and actual activities  
**Inputs**: PIM reason (text), Activity timeline (list)  
**Outputs**: Alignment assessment (aligned, partially aligned, not aligned) with explanation  
**External Dependencies**: Azure OpenAI Service (for reasoning)  
**Future State**: Could be extracted as a standalone service

#### 5. Report Generation Module
**Responsibility**: Format data into Markdown reports  
**Inputs**: PIM activations, activities, assessments  
**Outputs**: Markdown-formatted reports  
**External Dependencies**: None (pure formatting)  
**Future State**: Could be extracted as a template service

#### 6. Interface Modules
**Responsibility**: Handle user interaction in both modes  
**Components**:
- Interactive CLI: Command parsing, conversation context, console output
- Batch Runner: Automated scanning, file output
**External Dependencies**: None (OS-level I/O)  
**Future State**: Could support additional interfaces (Web UI, API)

### Phase 2: Potential Service Extraction (Future)

While not implemented in the initial modernization, the architecture prepares for potential future extraction:

```
┌────────────────┐      ┌───────────────────┐      ┌──────────────┐
│  CLI Frontend  │─────▶│  API Gateway      │◀─────│ Web UI       │
│  Container     │      │  Container        │      │ Container    │
└────────────────┘      └─────────┬─────────┘      └──────────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
         ┌───────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
         │ PIM          │  │ Activity   │  │ Report     │
         │ Detector     │  │ Correlator │  │ Generator  │
         │ Service      │  │ Service    │  │ Service    │
         └──────────────┘  └────────────┘  └────────────┘
                    │              │
                    └──────┬───────┘
                           │
                  ┌────────▼────────┐
                  │  AI Services    │
                  │  Container      │
                  │  - Query Gen    │
                  │  - Risk Assess  │
                  └─────────────────┘
```

**Note**: Service extraction is NOT part of the initial migration plan. This diagram shows potential future state only.

## Container Deployment Model

### Slice 0-1: Single Container Deployment

**Container Specification**:
- **Base Image**: `python:3.11-slim` (official Python image, security-maintained)
- **Application Code**: `/app` directory
- **Configuration**: Environment variables
- **Secrets**: Azure Key Vault or Azure Container Apps secrets
- **Health Check**: HTTP endpoint `/health` (for batch mode, simple liveness check)
- **Logging**: Stdout/stderr (captured by container platform)

**Dockerfile Structure** (to be created):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY main.py .

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Default to interactive mode
CMD ["python", "main.py"]
```

### Deployment Targets

#### Option 1: Azure Container Instances (ACI) - Recommended for Slice 0-1
**Pros**:
- Simplest deployment model
- Pay-per-second billing
- Suitable for batch mode (scheduled Azure Logic Apps or Functions trigger)
- Quick iteration during development

**Cons**:
- Limited orchestration features
- Not suitable for high-scale interactive mode

**Use Case**: Initial implementation, development, and testing

#### Option 2: Azure Container Apps (ACA) - Recommended for Production
**Pros**:
- Built-in scaling (can scale to zero for cost savings)
- Managed ingress for interactive mode (HTTPS endpoints)
- Integrated with Azure Monitor and Log Analytics
- Dapr support for future service-to-service communication
- Job support for batch mode

**Cons**:
- Slightly more complex setup than ACI
- Requires more Azure configuration

**Use Case**: Production deployment supporting both interactive and batch modes

#### Option 3: Azure Kubernetes Service (AKS)
**Pros**:
- Full orchestration capabilities
- Prepared for multi-service architecture
- Industry-standard platform

**Cons**:
- Significant operational overhead
- Overkill for single container
- Higher cost and complexity

**Use Case**: Only if organization already operates AKS and has expertise

**Recommendation**: Start with ACI for Slice 0-1, migrate to ACA when ready for production.

## Routing and Configuration Approach

### Slice 0-1: Direct Container Access

Since we start with a monolith, routing is minimal:

**Interactive Mode**:
- Direct execution: `docker run -it pim-auto:latest`
- Or via Azure Container Apps console: `az containerapp exec`
- Or via web-based terminal (ACA feature)

**Batch Mode**:
- Scheduled trigger: Azure Logic Apps or Azure Functions timer trigger
- Container run: `docker run pim-auto:latest --mode batch`
- Output: Stdout captured by Azure Monitor

### Configuration Management

**Configuration Sources** (in priority order):
1. Environment variables (12-factor app pattern)
2. Azure Key Vault for secrets (optional, via managed identity)
3. Default values in code

**Required Configuration**:

| Parameter | Environment Variable | Example | Required | Notes |
|-----------|---------------------|---------|----------|-------|
| Azure OpenAI Endpoint | `AZURE_OPENAI_ENDPOINT` | `https://my-openai.openai.azure.com/` | Yes | |
| Azure OpenAI Deployment | `AZURE_OPENAI_DEPLOYMENT` | `gpt-4o` | Yes | Model name |
| Azure OpenAI API Version | `AZURE_OPENAI_API_VERSION` | `2024-02-15-preview` | No | Defaults to latest |
| Log Analytics Workspace ID | `LOG_ANALYTICS_WORKSPACE_ID` | `abc123...` | Yes | |
| Log Analytics Region | `LOG_ANALYTICS_REGION` | `eastus` | No | Defaults to same as OpenAI |
| Default Scan Window (hours) | `DEFAULT_SCAN_HOURS` | `24` | No | Defaults to 24 |
| Log Level | `LOG_LEVEL` | `INFO` | No | Defaults to INFO |
| Output Path (batch mode) | `BATCH_OUTPUT_PATH` | `/output/report.md` | No | Defaults to stdout |

**Authentication Configuration**:
- No configuration needed - DefaultAzureCredential handles automatic credential chain
- Local dev: Uses Azure CLI credentials
- Azure deployment: Uses managed identity

**Secrets Management**:
- **NOT stored in environment variables**: API keys (none used - managed identity)
- **NOT committed to Git**: Any connection strings or credentials
- **Stored in Azure Key Vault**: If customer requires explicit secret storage
- **Injected at runtime**: Via Azure Container Apps secret references

### Configuration Validation

The application will validate configuration at startup:
- Check all required environment variables are present
- Test Azure OpenAI connection
- Test Log Analytics connection
- Fail fast with clear error messages if misconfigured

## Data Access Strategy

### No Application Database

Unlike typical applications, PIM Auto is **stateless** and does not maintain its own database.

**Data Sources** (external):
1. **Azure Log Analytics**: Source of truth for all PIM and activity data
2. **Azure OpenAI**: Stateless AI service (conversation context stored in application memory during interactive sessions)

### Shared Azure Resources (Initial State)

All modules access the same Azure resources:
- Same Log Analytics workspace
- Same Azure OpenAI endpoint
- Same managed identity for authentication

This "shared data source" approach is acceptable because:
- PIM Auto is a read-only monitoring tool (no writes to Azure)
- No data ownership conflicts between modules
- Simplifies initial implementation
- Reduces operational complexity

### Data Flow Patterns

#### PIM Detection Flow
```
PIM Detector Module
  → Azure Log Analytics API (KQL query on AuditLogs)
  → Parse results
  → Return structured PIM activation list
```

#### Activity Correlation Flow
```
Activity Correlator Module
  → Azure Log Analytics API (KQL query on AzureActivity)
  → Parse results
  → Return structured activity timeline
```

#### AI Query Generation Flow
```
Query Generator Module
  → Azure OpenAI API (Chat completion with KQL context)
  → Receive generated query
  → Validate syntax (basic checks)
  → If fails: Self-correct via OpenAI
  → Return valid KQL query
```

#### Risk Assessment Flow
```
Risk Assessor Module
  → Azure OpenAI API (Chat completion with alignment prompt)
  → Receive alignment assessment
  → Parse and structure result
  → Return assessment object
```

### Future Data Strategy (Phase 2+)

If services are extracted in the future:
- Each service continues to access Azure resources directly (no data replication)
- Service-to-service calls use REST APIs with contract definitions
- Optional: Introduce caching layer (Redis) for query results to reduce costs
- Optional: Event-driven architecture for asynchronous processing

### Data Consistency Considerations

Since PIM Auto queries Azure Log Analytics:
- **Latency**: Log ingestion may have delays (typically 5-15 minutes)
- **Eventual Consistency**: Activity logs may not reflect the absolute current state
- **Retention**: Historical queries limited by workspace retention policy (default: 30-90 days)

These are acceptable trade-offs for an audit/monitoring tool.

## Security Architecture

### Authentication

**Azure Managed Identity** (production):
- Container runs with system-assigned or user-assigned managed identity
- No credentials in code or configuration
- RBAC permissions granted at Azure resource level

**Azure CLI** (local development):
- Developer authenticates via `az login`
- DefaultAzureCredential automatically uses CLI credentials
- No separate auth configuration needed

### Authorization

**Required Azure RBAC Roles**:
| Azure Resource | Required Role | Purpose |
|----------------|---------------|---------|
| Log Analytics Workspace | Log Analytics Reader | Query AuditLogs and AzureActivity tables |
| Azure OpenAI | Cognitive Services OpenAI User | Generate queries and assessments |

**Principle of Least Privilege**: Container identity should have ONLY these permissions, nothing more.

### Network Security

**Initial Deployment (Slice 0-1)**:
- Container accesses Azure services via public endpoints (HTTPS)
- Azure services protected by Azure AD authentication
- No application-level network controls needed

**Future Considerations**:
- Private endpoints for Azure services (if organization requires network isolation)
- VNET integration for containers
- Network security groups (NSGs) as needed

### Container Security

- **Non-root user**: Container runs as non-root user (UID 1000)
- **Minimal base image**: Use slim Python image, remove unnecessary packages
- **Dependency scanning**: Use automated tools (Dependabot, Snyk) for vulnerability detection
- **Image scanning**: Scan container images for CVEs before deployment
- **Regular updates**: Rebuild images with latest base image patches

### Secrets Management

- **No secrets in code**: Enforce via code review and static analysis
- **No secrets in Git**: Enforce via pre-commit hooks and GitHub secret scanning
- **No secrets in environment variables**: Use Key Vault references if secrets are needed
- **Audit trail**: All access to Azure resources logged via Azure Monitor

## Observability and Operations

### Logging

**Application Logs**:
- Structured logging using Python `logging` module
- JSON format for machine parsing
- Log to stdout/stderr (container best practice)
- Captured by container platform (ACI/ACA → Azure Monitor)

**Log Levels**:
- `DEBUG`: Detailed query generation, API calls
- `INFO`: User interactions, PIM detections, assessments
- `WARNING`: Failed queries, self-corrections
- `ERROR`: Unrecoverable errors, authentication failures
- `CRITICAL`: Application crashes

**Sensitive Data Handling**:
- Do NOT log user personal information beyond what's necessary
- Redact sensitive PIM activity details in logs
- Log query metadata, not full query results

### Metrics

**Recommended Metrics** (to be exposed via Azure Monitor):
- PIM activations detected (count per scan)
- Azure OpenAI API calls (count, latency, errors)
- Log Analytics queries (count, latency, errors)
- Risk assessments generated (count by alignment level)
- Batch mode execution time (duration)
- Interactive mode session duration (time)

**Instrumentation**:
- Use Azure Monitor Application Insights SDK
- Emit custom metrics for domain events
- Track dependencies (Azure services)

### Health Checks

**Liveness Check** (basic):
- HTTP endpoint: `GET /health`
- Returns: `200 OK` with `{"status": "alive"}`
- Purpose: Container platform determines if container is running

**Readiness Check** (advanced):
- HTTP endpoint: `GET /ready`
- Tests: Azure OpenAI reachable, Log Analytics reachable
- Returns: `200 OK` if ready, `503 Service Unavailable` if not
- Purpose: Don't route traffic until dependencies are available

**Startup Check**:
- Validate configuration at startup
- Fail fast if misconfigured (exit code 1)
- Log clear error messages for troubleshooting

### Monitoring and Alerts

**Recommended Alerts**:
1. Container crash/restart (critical)
2. Azure OpenAI API errors >10% (warning)
3. Log Analytics query failures >5% (warning)
4. Batch mode execution failures (warning)
5. High-risk PIM activities detected (info - business alert)

**Dashboards**:
- Azure Monitor dashboard with:
  - Container health status
  - API call success rates
  - Query execution times
  - PIM detection trends

## Deployment Pipeline

### Continuous Integration (CI)

**Build Stage**:
1. Checkout code
2. Run linters (flake8, black, mypy)
3. Run unit tests (pytest)
4. Build container image
5. Scan image for vulnerabilities
6. Push image to Azure Container Registry (ACR)

**Quality Gates**:
- All tests pass
- Code coverage >80%
- No high/critical vulnerabilities
- Linting passes

### Continuous Deployment (CD)

**Deployment Stages**:
1. **Dev Environment**:
   - Automatic deployment on merge to main branch
   - Azure Container Instance or ACA (dev environment)
   - Uses dev Azure resources (separate Log Analytics, OpenAI)

2. **Staging Environment** (optional):
   - Manual approval required
   - Tests against production-like Azure resources
   - Run smoke tests

3. **Production Environment**:
   - Manual approval required
   - Deploy to Azure Container Apps (production)
   - Blue/green deployment for zero downtime
   - Rollback capability

### Rollback Strategy

**Container Rollback**:
- Keep last 3 container image versions in ACR
- Rollback = redeploy previous image tag
- Test rollback procedure regularly

**Configuration Rollback**:
- Use infrastructure-as-code (Bicep or Terraform)
- Version control for infrastructure changes
- Rollback = reapply previous IaC version

**Emergency Rollback Procedure**:
1. Identify issue (monitoring alerts)
2. Decision: Rollback or hotfix forward
3. If rollback: Redeploy previous known-good image
4. Verify: Check health endpoints and monitoring
5. Post-mortem: Document and improve

## Cost Considerations

### Compute Costs

**Azure Container Instances** (dev/test):
- ~$0.0001 per vCPU-second + memory costs
- Suitable for low-volume interactive testing
- Batch mode: Pay only for execution time

**Azure Container Apps** (production):
- Consumption plan: $0.000012 per vCPU-second + memory
- Can scale to zero when not in use (batch mode)
- Free tier: 180,000 vCPU-seconds/month

### Azure Service Costs

**Azure OpenAI** (primary cost driver):
- GPT-4o: ~$0.01-0.03 per 1K tokens (input + output)
- Estimate: 5-10 queries per PIM activation
- Cost depends on PIM activation volume

**Log Analytics**:
- Query costs: $0.25 per GB scanned (Pay-as-you-go)
- Retention costs: Based on workspace retention policy
- Typical query: <100 MB per scan

**Estimated Monthly Costs** (example):
- 100 PIM activations/month
- 10 queries per activation (1,000 total)
- 50,000 tokens per query (average)
- OpenAI: 50M tokens × $0.02 = **~$1,000/month**
- Log Analytics: 1,000 queries × 0.05 GB × $0.25 = **~$13/month**
- Container Apps: Free tier or **~$20/month**
- **Total: ~$1,033/month** (OpenAI dominates cost)

**Cost Optimization**:
- Cache query results to reduce redundant OpenAI calls
- Optimize prompts to reduce token usage
- Use batch mode at off-peak hours for lower priority scans
- Monitor costs via Azure Cost Management

## Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Runtime** | Python | 3.11+ | Application language (per spec) |
| **Container** | Docker | Latest | Packaging and deployment |
| **Hosting** | Azure Container Apps | N/A | Production container platform |
| **AI** | Azure OpenAI | GPT-4o | Query generation and risk assessment |
| **Data** | Azure Log Analytics | N/A | PIM and activity data source |
| **Auth** | DefaultAzureCredential | Azure SDK | Credential management |
| **Logging** | Python logging + App Insights | Latest | Observability |
| **Testing** | pytest | Latest | Unit and integration tests |
| **Linting** | flake8, black, mypy | Latest | Code quality |
| **IaC** | Bicep or Terraform | Latest | Infrastructure deployment |

## Risks and Mitigations

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Azure OpenAI quota limits | High | Medium | Implement retry logic, request quota increase, cache results |
| Log Analytics query timeouts | Medium | Low | Optimize queries, implement pagination, add timeout handling |
| Container platform issues | High | Low | Use managed Azure services (ACA), implement health checks, monitoring |
| Python dependency vulnerabilities | Medium | Medium | Regular dependency updates, automated scanning, use virtual environments |
| Azure service outages | High | Low | Implement graceful degradation, clear error messages, retry logic |

### Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Misconfiguration | High | Medium | Configuration validation at startup, infrastructure-as-code, documentation |
| Cost overruns | Medium | Medium | Cost alerts, query optimization, batch mode scheduling |
| Insufficient Azure permissions | High | Medium | Clear RBAC documentation, permission testing in CI/CD |
| Lack of runbook procedures | Medium | Low | Create runbook (separate document), training for operators |

### Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| False positives in risk assessment | Medium | Medium | Tune prompts, allow human review, document limitations |
| Missed PIM violations | High | Low | Regular testing, validation against known scenarios |
| User adoption challenges | Medium | Medium | Documentation, training, user feedback iteration |

## Future Architecture Evolution

### Potential Phase 2 Changes (Not in Initial Plan)

If the application needs to scale or handle additional requirements:

1. **Service Extraction**:
   - Extract PIM Detector as standalone service
   - Benefits: Independent scaling, separate deployment cycles
   - Trigger: Interactive mode has >100 concurrent users

2. **API Layer**:
   - Add REST API for programmatic access
   - Benefits: Integration with other tools (SIEM, ticketing systems)
   - Trigger: External systems need to consume PIM data

3. **Web UI**:
   - Add browser-based interface
   - Benefits: Wider user access, better UX
   - Trigger: Non-technical users need access

4. **Event-Driven Architecture**:
   - Real-time PIM activation detection via Azure Event Grid
   - Benefits: Immediate alerting instead of periodic scanning
   - Trigger: Need sub-minute detection latency

5. **Data Caching**:
   - Add Redis cache for query results
   - Benefits: Reduce Azure OpenAI costs, improve response time
   - Trigger: OpenAI costs exceed budget

6. **Multi-Tenancy**:
   - Support multiple organizations in single deployment
   - Benefits: SaaS delivery model
   - Trigger: Multiple customers want hosted solution

**Important**: These are future possibilities, NOT part of the initial modernization plan.

## Compliance and Governance

### Documentation Requirements

- **This Document**: Target Architecture (commit to repo)
- **Migration Plan**: Phased implementation steps (separate document)
- **ADRs**: Architectural decision records (separate files)
- **Runbook**: Operational procedures (existing, may need updates)
- **API Documentation**: Once API layer is added (future)

### Review and Approval Process

Per agent-based governance (ADR-001):
1. Modernization agent creates architecture documents
2. Documents delivered via pull request
3. Human review and approval required
4. No implementation begins without approval
5. Architecture is living documentation (updated as system evolves)

### Change Management

**Architecture Changes**:
- Significant changes require new ADR
- Minor updates: Update this document with changelog
- All changes: Git-tracked, PR-reviewed

**Version Control**:
- This document is versioned via Git
- Tag releases with semantic versioning
- Maintain changelog of architecture decisions

## Acceptance Criteria

This target architecture meets acceptance criteria if:

✅ **Service boundaries are defined**: Clear modules with responsibilities  
✅ **Container deployment model is specified**: Docker-based, Azure Container Apps  
✅ **Routing and configuration approach is documented**: Environment variables, managed identity  
✅ **Data access strategy is clear**: Direct Azure access, no application database  
✅ **Plan is achievable**: Uses existing Azure stack, Python skills  
✅ **No code changes proposed**: This is planning documentation only  
✅ **First slice is identified**: See Migration Plan (separate document)  

## References

- `/README.md`: Original application specification
- `/docs/HLD.md`: High-level design (current state)
- `/docs/LLD.md`: Low-level design (current state)
- `/docs/ADR/ADR-001-agent-based-governance.md`: Agent model
- `/docs/ADR/ADR-002-specification-first-development.md`: Spec-first approach
- `/docs/ADR/ADR-003-azure-native-architecture.md`: Azure dependencies
- `/docs/ADR/ADR-004-dual-mode-operation.md`: Interactive and batch modes
- `/docs/Migration-Plan.md`: Phased implementation plan (to be created)
- `/.github/agents/modernisation.agent.md`: This agent's instructions
- `/.github/skills/architecture-reasoning.skill.md`: Architecture methodology

## Glossary

- **ACA**: Azure Container Apps
- **ACI**: Azure Container Instances
- **ADR**: Architecture Decision Record
- **IaC**: Infrastructure as Code
- **KQL**: Kusto Query Language (Azure Log Analytics)
- **PIM**: Privileged Identity Management (Azure AD feature)
- **RBAC**: Role-Based Access Control
- **Strangler Pattern**: Incremental modernization approach (extract piece by piece)
