# Low-Level Design (LLD) - PIM Auto

**Document Status**: Current State (As-Is)  
**Last Updated**: 2026-02-10  
**Repository**: jometzg/pim-auto

## Purpose

This Low-Level Design document provides a detailed technical view of the **current state** of the pim-auto repository. It catalogs what exists today at the file, class, and method level.

## Repository Structure

```
pim-auto/
├── .git/                           # Git repository metadata
├── .github/                        # GitHub automation and configuration
│   ├── workflows/
│   │   └── ci.yml                 # CI/CD pipeline configuration
│   ├── agents/
│   │   ├── documentation.agent.md          # Documentation agent config
│   │   ├── testing.agent.md                # Testing agent config
│   │   ├── modernisation.agent.md          # Architecture agent config
│   │   ├── implementation.agent.md         # Implementation agent config
│   │   └── intelligent-migration.agent.md  # Migration orchestration agent
│   └── skills/
│       ├── system-discovery.skill.md               # Current system documentation
│       ├── test-synthesis.skill.md                 # Test creation guidelines
│       ├── architecture-reasoning.skill.md         # Architecture analysis
│       ├── incremental-refactoring.skill.md        # Refactoring methodology
│       └── intelligent-application-migration.skill.md  # Migration design
└── README.md                       # Application specification document
```

## Key Files Analysis

### 1. README.md

**Path**: `/README.md`  
**Type**: Markdown specification document  
**Size**: 4,200 bytes  
**Purpose**: Comprehensive specification of intended Azure PIM Activity Audit Agent

**Content Structure**:
- Title and overview (lines 1-9)
- Features list: 10 bullet points (lines 10-19)
- Non-functional requirements: 10 numbered items (lines 21-31)
- Prerequisites: 4 bullet points (lines 33-38)
- Usage examples: Interactive chat mode (lines 40-69) and batch mode (lines 71-81)

**Key Information Extracted**:
- Target language: Python 3.11+
- AI service: Azure OpenAI with GPT-4o
- Data sources: Azure Log Analytics (AuditLogs, AzureActivity tables)
- Authentication: DefaultAzureCredential pattern
- Operational modes: Interactive chat and batch processing

**Coupling Notes**: 
- No code implementation to couple with
- README exists in isolation

### 2. .github/workflows/ci.yml

**Path**: `/.github/workflows/ci.yml`  
**Type**: GitHub Actions workflow configuration  
**Purpose**: CI/CD automation (content not analyzed in detail)

### 3. Agent Configuration Files

Five agent files define specialized AI agents for different development phases:

#### 3.1 documentation.agent.md
**Path**: `/.github/agents/documentation.agent.md`  
**Purpose**: Defines the documentation agent that generates HLD, LLD, ADRs, and Runbooks  
**Referenced Skill**: `system-discovery.skill.md`  
**Outputs**: 
- `/docs/HLD.md`
- `/docs/LLD.md`
- `/docs/ADR/` directory
- `/docs/Runbook.md`

#### 3.2 testing.agent.md
**Path**: `/.github/agents/testing.agent.md`  
**Purpose**: Test strategy and automated test creation  
**Referenced Skill**: `test-synthesis.skill.md`

#### 3.3 modernisation.agent.md
**Path**: `/.github/agents/modernisation.agent.md`  
**Purpose**: Architecture proposal and migration planning  
**Referenced Skills**: `architecture-reasoning.skill.md`, `incremental-refactoring.skill.md`

#### 3.4 implementation.agent.md
**Path**: `/.github/agents/implementation.agent.md`  
**Purpose**: Implements approved migration slices with tests and documentation  
**Referenced Skill**: `incremental-refactoring.skill.md`

#### 3.5 intelligent-migration.agent.md
**Path**: `/.github/agents/intelligent-migration.agent.md`  
**Purpose**: End-to-end migration program design and governance  
**Referenced Skill**: `intelligent-application-migration.skill.md`

### 4. Skill Definition Files

Five skill files provide detailed operating procedures:

#### 4.1 system-discovery.skill.md
**Path**: `/.github/skills/system-discovery.skill.md`  
**Purpose**: Procedure for documenting current system state  
**Execution Steps**: 6 phases
1. Repo Orientation
2. Domain Boundary Mapping
3. Flow Tracing
4. Data Model & Persistence analysis
5. External Dependencies identification
6. Evidence-Based Output production

**Output Requirements**:
- System Inventory list
- Domain Map
- Key Flows with file paths
- Coupling Hotspots

#### 4.2 test-synthesis.skill.md
**Path**: `/.github/skills/test-synthesis.skill.md`  
**Purpose**: Guidelines for baseline test strategy creation

#### 4.3 architecture-reasoning.skill.md
**Path**: `/.github/skills/architecture-reasoning.skill.md`  
**Purpose**: Target architecture proposals and migration planning

#### 4.4 incremental-refactoring.skill.md
**Path**: `/.github/skills/incremental-refactoring.skill.md`  
**Purpose**: Methodology for reversible migration implementation

#### 4.5 intelligent-application-migration.skill.md
**Path**: `/.github/skills/intelligent-application-migration.skill.md`  
**Purpose**: End-to-end migration program design

## Classes and Services per Domain

### Current State: No Implementation

**Status**: No Python classes, services, or modules exist in the repository.

### Specified Domains (from README.md)

While no code exists, the README specification implies the following logical domains:

#### 1. PIM Detection Domain
**Responsibility**: Scan Azure Log Analytics for privilege elevations  
**Specified Operations**:
- Query AuditLogs table for PIM activations
- Extract user identities and elevation timestamps
- Extract activation reasons

#### 2. AI Query Generation Domain
**Responsibility**: Generate and correct Kusto queries using Azure OpenAI  
**Specified Operations**:
- Generate KQL queries from natural language
- Self-correct failed queries
- Maintain query context

#### 3. Activity Correlation Domain
**Responsibility**: Track Azure resource changes during elevation periods  
**Specified Operations**:
- Query AzureActivity table
- Filter by user and time range
- Aggregate activity timeline

#### 4. Risk Assessment Domain
**Responsibility**: Evaluate activity alignment with stated reasons  
**Specified Operations**:
- Compare stated reason with actual activities
- Generate alignment assessment
- Flag mismatches for investigation

#### 5. Reporting Domain
**Responsibility**: Generate Markdown-formatted activity reports  
**Specified Operations**:
- Format PIM activations list
- Format activity timelines
- Generate risk assessment summaries

#### 6. Interface Domain
**Responsibility**: Handle user interaction (chat and batch modes)  
**Specified Operations**:
- Parse user commands
- Manage conversation context
- Display formatted results

## Request and Execution Flows

### Current State: No Executable Flows

Since no code exists, there are no actual execution flows to trace.

### Specified Flows (from README.md)

The README provides two example flows:

#### Flow 1: Interactive Chat - Scan Command
```
User Input: "scan"
    ↓
[PIM Detection Domain]
    ↓ Query Log Analytics AuditLogs
    ↓
[Result Processing]
    ↓ Extract elevated users, reasons, timestamps
    ↓
[Display to User]
    Output: List of users with elevation details
```

**Example Output**: 
```
Found 2 elevated users:
1. john.doe@contoso.com. Reason "need to add a storage account"(activated 2 hours ago)
2. jane.smith@contoso.com Reason "need to add an NSG rule"(activated 5 hours ago)
```

#### Flow 2: Interactive Chat - Activity Query
```
User Input: "What did john.doe@contoso.com do?"
    ↓
[AI Query Generation Domain]
    ↓ Generate Kusto query for user activities
    ↓
[Activity Correlation Domain]
    ↓ Query AzureActivity table
    ↓ Filter by user + elevation time range
    ↓
[Result Formatting]
    ↓ Format as timeline
    ↓
[Display to User]
    Output: Timestamped activity list
```

**Example Output**:
```
📋 Activities for john.doe@contoso.com during elevation:

[2026-02-05 10:30:15] Created resource group 'rg-production'
[2026-02-05 10:35:22] Deployed App Service 'app-web-prod'
[2026-02-05 11:15:08] Modified Network Security Group rules
```

#### Flow 3: Interactive Chat - Alignment Assessment
```
User Input: "do their activity align with the reason they gave for activation?"
    ↓
[Risk Assessment Domain]
    ↓ Compare stated reason vs actual activities
    ↓ Apply AI reasoning
    ↓
[Generate Assessment]
    ↓
[Display to User]
    Output: Alignment verdict with explanation
```

**Example Output**:
```
1. john.doe@contoso.com activities do not align with the reason for activation. 
   The user created a resource group and deployed an App Service, which is not 
   related to adding a storage account. This may warrant further investigation.
```

#### Flow 4: Batch Mode
```
Application Start: python main.py --mode batch
    ↓
[PIM Detection Domain]
    ↓ Scan last 24 hours
    ↓
[Activity Correlation Domain]
    ↓ For each elevated user:
    ↓   - Query activities
    ↓   - Build timeline
    ↓
[Risk Assessment Domain]
    ↓ Assess each user's alignment
    ↓
[Reporting Domain]
    ↓ Generate Markdown report
    ↓
[Output]
    Write to stdout or file
```

## Data Access Patterns

### Current State: No Data Access

No database connections, ORM models, or data access code exists.

### Specified Patterns (from README.md)

The specification implies the following data access patterns:

#### Azure Log Analytics - AuditLogs Table
**Purpose**: PIM activation detection  
**Query Pattern**: Time-based filtering for privilege elevation events  
**Expected Fields**:
- User identity
- Activation timestamp
- Activation reason
- Role/permission granted

#### Azure Log Analytics - AzureActivity Table
**Purpose**: Resource change tracking  
**Query Pattern**: User + time range filtering  
**Expected Fields**:
- Timestamp
- User/caller identity
- Operation type
- Resource details
- Result/status

#### Query Technology
**Language**: Kusto Query Language (KQL)  
**Execution**: Via Azure Log Analytics API  
**Error Handling**: AI-powered self-correction for failed queries

## Coupling Hotspots and Complexity Indicators

### Current Codebase: Zero Coupling

Since no implementation exists, there is no code coupling to analyze.

### Potential Future Coupling Risks (from Specification)

Based on the README specification, the following coupling risks should be monitored during implementation:

#### 1. Azure Service Dependencies
**Risk Level**: High  
**Nature**: The application will be tightly coupled to three Azure services:
- Azure OpenAI: Critical for AI functionality
- Azure Log Analytics: Critical for data access
- Azure AD/Managed Identity: Critical for authentication

**Impact**: Application cannot function without these services. No local development fallbacks specified.

#### 2. Kusto Query Language
**Risk Level**: Medium  
**Nature**: Query generation and parsing tied to KQL syntax  
**Impact**: Changes to KQL schema or syntax could break query generation

#### 3. Natural Language Processing
**Risk Level**: Medium  
**Nature**: Dependency on GPT-4o model behavior  
**Impact**: Model updates or changes could affect query quality or system behavior

#### 4. Log Analytics Schema
**Risk Level**: High  
**Nature**: Hardcoded dependency on AuditLogs and AzureActivity table schemas  
**Impact**: Schema changes by Microsoft could break the application

#### 5. Chat State Management
**Risk Level**: Low-Medium  
**Nature**: Context-aware conversation requires state management  
**Impact**: Complex flow control in interactive mode

## Integration Points

### Current State: No Integrations

No external system integrations are implemented.

### Specified Integrations (from README.md)

#### 1. Azure OpenAI API
**Purpose**: Natural language understanding and KQL generation  
**Authentication**: DefaultAzureCredential  
**Model**: GPT-4o  
**Operations**: Chat completions, query generation, self-correction

#### 2. Azure Log Analytics API
**Purpose**: Query execution  
**Authentication**: DefaultAzureCredential  
**Operations**: KQL query execution on AuditLogs and AzureActivity tables

#### 3. Azure Monitor Action Groups (implied)
**Purpose**: Report distribution  
**Authentication**: DefaultAzureCredential  
**Operations**: Alert/report delivery

## Testing Strategy

### Current State: No Tests

No test files, test frameworks, or testing infrastructure exists.

### Testing Implications

When implementation begins, the following testing challenges will need to be addressed:

1. **Azure Service Mocking**: Tests will need to mock Azure OpenAI, Log Analytics, and authentication
2. **KQL Query Validation**: Tests should validate generated KQL syntax
3. **AI Response Testing**: Non-deterministic AI outputs require special test approaches
4. **End-to-End Flows**: Interactive chat flows need integration testing
5. **Batch Mode**: Automated mode requires different test approach than interactive

## Configuration Management

### Current State: No Configuration

No configuration files exist (no `.env`, `config.json`, `appsettings.json`, etc.)

### Specified Configuration Needs (from README.md)

The specification implies the following configuration requirements:

1. **Azure OpenAI**:
   - Endpoint URL
   - API version
   - Deployment name (GPT-4o)

2. **Log Analytics**:
   - Workspace ID
   - Workspace region

3. **Time Parameters**:
   - Default scan window (24 hours mentioned in examples)
   - Query timeout settings

4. **Operational Mode**:
   - Interactive vs. batch mode selection

## Dependencies

### Current State: No Dependencies

No `requirements.txt`, `Pipfile`, `pyproject.toml`, or similar dependency manifest exists.

### Specified Dependencies (from README.md)

The specification indicates these Python package dependencies:

1. **Azure SDK**:
   - `azure-identity`: For DefaultAzureCredential
   - `azure-monitor-query`: For Log Analytics queries
   - `azure-openai` or `openai`: For GPT-4o API access

2. **Python Version**:
   - Python 3.11 or higher (strict requirement)

3. **Development Tools** (implied):
   - Azure CLI: For local authentication
   - Markdown rendering: For report generation

## Error Handling

### Current State: No Implementation

No error handling code exists.

### Specified Requirements (from README.md)

The specification includes:
- "Must handle and log errors gracefully" (Non-functional requirement #4)
- "Self-correcting queries" feature: AI fixes failed KQL queries
- "Meaningful feedback to the user" requirement

## Security Considerations

### Current State: No Security Implementation

No security code exists.

### Specified Security Model (from README.md)

- **Authentication**: DefaultAzureCredential pattern
  - Supports managed identities (production)
  - Supports Azure CLI (local development)
- **Authorization**: Inherits from Azure AD identity permissions
- **Secrets Management**: No hardcoded credentials (uses Azure credential chain)

## Performance Characteristics

### Current State: Not Applicable

No code to measure performance.

### Specified Requirements (from README.md)

- "Handle multiple concurrent users in interactive mode without performance degradation" (Non-functional requirement #8)
- Batch mode suggests ability to process multiple users in single execution

## Complexity Metrics

### Current Repository
- **Lines of Code**: 0 (Python)
- **Number of Classes**: 0
- **Number of Functions**: 0
- **Cyclomatic Complexity**: N/A
- **Files**: 12 total (1 README, 1 CI workflow, 5 agents, 5 skills)

### README Specification Complexity
- **Word Count**: ~1,000 words
- **Feature Count**: 10 features listed
- **Non-functional Requirements**: 10 items
- **Usage Examples**: 2 modes with detailed examples

## Development Environment

### Current State

No development environment is configured. Missing:
- Virtual environment setup
- Dependency installation
- IDE configuration
- Linting/formatting tools
- Pre-commit hooks

### Build Process

**Current State**: Not applicable - no build process exists.

### Deployment

**Current State**: Not applicable - no deployment artifacts exist.

## Naming Conventions

### Current State

Only file naming conventions are observable:

- **Markdown files**: lowercase with hyphens (e.g., `system-discovery.skill.md`)
- **Agent files**: `<purpose>.agent.md` pattern
- **Skill files**: `<purpose>.skill.md` pattern
- **Workflow files**: lowercase with hyphens (e.g., `ci.yml`)

### Future Conventions

Python conventions should follow PEP 8 when implementation begins (implied by "maintainable" requirement).

## Summary

The pim-auto repository is currently in a **pre-implementation state**. It contains:

✅ **What Exists**:
- Comprehensive specification (README.md)
- Agent-based governance model (.github/agents/)
- Skill-based procedures (.github/skills/)
- CI workflow skeleton

❌ **What Does Not Exist**:
- Python source code
- Tests
- Dependencies
- Configuration
- Build process
- Deployment artifacts

**Next Steps for Implementation**:
1. Create project structure (`src/`, `tests/`, etc.)
2. Define dependencies (`requirements.txt` or `pyproject.toml`)
3. Implement core domains per specification
4. Add tests per testing agent guidelines
5. Configure Azure service connections
6. Implement CI/CD pipeline

## References

- `/README.md`: Complete application specification
- `/.github/skills/system-discovery.skill.md`: This documentation procedure
- `/.github/agents/implementation.agent.md`: Implementation agent for building the application
