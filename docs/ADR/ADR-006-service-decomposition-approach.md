# ADR-006: Service Decomposition Approach

**Status**: Proposed  
**Date**: 2026-02-10  
**Decision Makers**: Modernization Agent (pending human approval)

## Context

The PIM Auto application, as specified in `/README.md`, describes a system with multiple distinct responsibilities:
- PIM activation detection
- Azure activity correlation
- AI-powered query generation
- Risk assessment
- Report generation
- User interface (CLI)

A key architectural question is: Should we build this as a monolith or decompose it into microservices from the start?

Additionally, the agent-based governance model (ADR-001) anticipates future modernization and migration activities, suggesting that the architecture should support evolution over time.

## Decision

Adopt a **"Modular Monolith First, Service Extraction Later"** approach:

### Phase 1: Containerized Modular Monolith (Slice 0-2)

Build the application as a **single container** with clear **internal module boundaries**:

1. **Module-Based Organization**:
   - `/src/pim_auto/core/pim_detector.py` - PIM Detection Module
   - `/src/pim_auto/core/activity_correlator.py` - Activity Correlation Module
   - `/src/pim_auto/core/query_generator.py` - Query Generation Module
   - `/src/pim_auto/core/risk_assessor.py` - Risk Assessment Module
   - `/src/pim_auto/reporting/markdown_generator.py` - Report Generation Module
   - `/src/pim_auto/interfaces/` - CLI and Batch interfaces

2. **Clear Module Contracts**:
   - Each module has well-defined inputs/outputs
   - Minimal coupling between modules
   - Dependencies flow in one direction (no circular dependencies)

3. **Shared Azure Clients**:
   - All modules access same Azure resources (Log Analytics, OpenAI)
   - No data duplication or inter-module communication complexity
   - Simplified authentication (single managed identity)

### Phase 2: Potential Service Extraction (Future, Not Initial Plan)

If and when needed (based on scale, team size, or operational requirements):

1. **Extract AI Services**:
   - Query Generator + Risk Assessor → AI Service
   - Reason: High Azure OpenAI cost, potential for caching/optimization
   - Communication: REST API with JSON contracts

2. **Extract Data Access Services**:
   - PIM Detector → PIM Service
   - Activity Correlator → Activity Service
   - Reason: Independent scaling, specialized query optimization
   - Communication: REST API with JSON contracts

3. **Add API Gateway**:
   - Centralized routing, authentication, rate limiting
   - Support for web UI and external integrations

**Important**: Service extraction is **NOT part of the initial migration plan** (Slices 0-4). It is a future possibility that the architecture prepares for but does not implement.

## Rationale

### Advantages of Monolith-First Approach

1. **Simpler Initial Implementation**:
   - Single codebase, single deployment artifact
   - No inter-service communication complexity
   - Easier debugging (single process, unified logging)
   - Faster development (no API contracts between services)

2. **Lower Operational Overhead**:
   - One container to deploy, monitor, scale
   - Single CI/CD pipeline
   - Simpler failure modes
   - Reduced cost (no service mesh, API gateways, etc.)

3. **Flexibility to Evolve**:
   - Clear module boundaries enable future extraction
   - Can extract services when justified by real needs
   - Avoid premature optimization (YAGNI principle)

4. **Aligned with Current Team**:
   - Easier for single developer or small team
   - Lower cognitive load
   - Standard Python application patterns

5. **Matches Current Scale**:
   - PIM activations are relatively low-volume (typically <100/day)
   - No performance bottlenecks expected
   - Monolith can handle expected load

### Trade-offs

1. **Future Extraction Effort**:
   - If service extraction is needed, requires refactoring
   - Mitigated by clear module boundaries

2. **All-or-Nothing Deployment**:
   - Cannot deploy modules independently
   - Mitigated by good testing and gradual rollout practices

3. **Shared Resource Contention**:
   - All modules run in same container (CPU, memory)
   - Mitigated by proper resource allocation and monitoring

## Consequences

### Positive

- **Faster Time to Value**: Production-ready application in fewer slices
- **Lower Complexity**: Less infrastructure to manage
- **Better Performance**: No network latency between modules
- **Easier Testing**: Integration tests simpler (no service mocking)
- **Cost Efficiency**: Single container, single Azure OpenAI instance

### Negative

- **Scaling Limitations**: Cannot scale individual modules independently
  - Mitigation: Monolith can still scale horizontally (multiple container instances)
  - Reality: Current scale doesn't require fine-grained scaling
- **Deployment Coupling**: All modules deploy together
  - Mitigation: Good testing, feature flags, gradual rollout
  - Reality: Low deployment frequency expected (stable monitoring tool)

### Neutral

- **Module Boundaries Must Be Respected**: Requires discipline
  - Enforcement: Code reviews, linting rules, architectural guidelines
- **Future Service Extraction Possible**: Architecture supports it
  - Condition: Only if justified by real operational needs

## Module Dependency Rules

To prepare for potential future extraction, modules must follow these rules:

### Dependency Direction

```
┌─────────────────────────────────────────┐
│         Interfaces Layer                │
│   (Interactive CLI, Batch Runner)       │
└──────────────┬──────────────────────────┘
               │ depends on
┌──────────────▼──────────────────────────┐
│         Core Logic Layer                │
│  (PIM Detector, Activity Correlator,    │
│   Query Generator, Risk Assessor)       │
└──────────────┬──────────────────────────┘
               │ depends on
┌──────────────▼──────────────────────────┐
│         Azure Integration Layer         │
│  (OpenAI Client, Log Analytics Client,  │
│   Authentication)                       │
└─────────────────────────────────────────┘
```

**Rule**: Dependencies only flow downward. No circular dependencies.

### Module Isolation Rules

1. **No Direct Module-to-Module Calls** (except via defined interfaces):
   - PIM Detector does NOT directly call Activity Correlator
   - Orchestration happens at Interface Layer (CLI or Batch Runner)

2. **Shared Data Only Through Parameters**:
   - No global state between modules
   - No shared mutable data structures
   - Pass data explicitly via function parameters

3. **Independent Azure Client Wrappers**:
   - Each module can have its own Azure client instance
   - Clients are stateless and independently testable

4. **No Cross-Module Imports** (within Core Layer):
   - `pim_detector.py` does NOT import `activity_correlator.py`
   - Prevents tight coupling

### Testing Isolation

- Each module has independent unit tests
- Modules can be tested with mocked dependencies
- Integration tests orchestrate multiple modules

## When to Extract Services (Future Decision Criteria)

Service extraction should only be considered if ONE OR MORE of the following conditions are met:

1. **Performance Bottleneck**:
   - Specific module becomes performance bottleneck
   - Independent scaling would provide significant benefit
   - Example: AI services need more resources than data access services

2. **Team Scaling**:
   - Team grows beyond 5-7 developers
   - Ownership boundaries need to be enforced
   - Multiple teams need independent deployment cycles

3. **Cost Optimization**:
   - Azure OpenAI costs exceed budget due to redundant queries
   - Caching or query optimization requires dedicated service
   - Separate service enables better cost tracking

4. **Operational Independence**:
   - Different modules have different SLAs or availability requirements
   - Failure isolation needed (one module failure shouldn't affect others)
   - Different deployment cadences required

5. **External Integration**:
   - Other systems need programmatic access to specific functionality
   - API exposure needed for third-party tools
   - Example: SIEM integration requires REST API

**Important**: None of these conditions exist today. Do NOT extract services prematurely.

## Alternatives Considered

### Alternative 1: Microservices from Day One

Build separate services for PIM Detector, Activity Correlator, AI Services, etc.

**Rejected because**:
- Premature optimization (YAGNI violation)
- High operational overhead for small team
- Network latency between services
- Complex inter-service authentication
- Increased cost (multiple containers, API gateway)
- Longer time to production
- Current scale doesn't justify complexity

### Alternative 2: Serverless Functions

Use Azure Functions for each module.

**Rejected because**:
- Interactive CLI mode requires stateful sessions (not suitable for Functions)
- Conversation context management difficult in serverless
- Cold start latency unacceptable for interactive mode
- ADR-004 requires dual-mode operation (CLI + batch) in unified deployment

### Alternative 3: Completely Unstructured Monolith

No module boundaries, all code in single file or mixed structure.

**Rejected because**:
- Unmaintainable as codebase grows
- Testing becomes difficult
- No clear separation of concerns
- Future service extraction impossible
- Violates good software engineering practices

## Implementation Guidelines

### Directory Structure (Enforced)

```
src/pim_auto/
├── main.py                  # Entry point, mode router
├── config.py                # Configuration management
├── azure/                   # Azure Integration Layer
│   ├── auth.py
│   ├── log_analytics.py
│   └── openai_client.py
├── core/                    # Core Logic Layer (NO cross-imports within core/)
│   ├── pim_detector.py
│   ├── activity_correlator.py
│   ├── query_generator.py
│   └── risk_assessor.py
├── interfaces/              # Interface Layer
│   ├── interactive_cli.py
│   └── batch_runner.py
└── reporting/               # Reporting Layer
    └── markdown_generator.py
```

### Code Review Checklist

When reviewing code, verify:
- ✅ No circular dependencies between modules
- ✅ Clear module responsibilities (single responsibility principle)
- ✅ Modules communicate via defined interfaces (function parameters)
- ✅ No global state or shared mutable data
- ✅ Each module has independent unit tests
- ✅ Dependencies flow downward only

### Refactoring Plan (If Service Extraction Needed)

If future conditions warrant service extraction:

1. **Identify Service Boundary**: Choose module(s) to extract
2. **Define API Contract**: REST API specification (OpenAPI)
3. **Implement Service**: Extract module into separate codebase
4. **Deploy Service**: Deploy as separate container
5. **Update Monolith**: Replace module with service client
6. **Gradual Rollout**: Feature flag for service vs. monolith
7. **Validate**: Performance, reliability, cost impact
8. **Commit**: Remove old module code, use service exclusively

## Alignment with Existing ADRs

- **ADR-001 (Agent-Based Governance)**: Modular structure supports future implementation agents
- **ADR-002 (Specification-First)**: Implements specified features without premature optimization
- **ADR-003 (Azure-Native)**: Monolith maintains direct Azure integration (no added complexity)
- **ADR-004 (Dual-Mode Operation)**: Single container supports both modes efficiently
- **ADR-005 (Containerization)**: Monolith fits well in single container model

## Success Criteria

This ADR is successfully implemented when:

✅ All modules have clear, documented responsibilities  
✅ Module boundaries are enforced (no violations in code review)  
✅ Each module has >80% test coverage independently  
✅ No circular dependencies between modules  
✅ Application performs well within single container  
✅ Code structure enables future service extraction (if needed)  

## Review Schedule

This decision should be reviewed:
- After 6 months of production operation
- If performance issues arise
- If team size exceeds 5 developers
- If Azure OpenAI costs exceed budget

At review, assess: Should we extract services, or continue with monolith?

## References

- `/docs/Target-Architecture.md`: Service boundaries section
- `/docs/Migration-Plan.md`: Slice 1-2 implementation details
- Martin Fowler: [Monolith First](https://martinfowler.com/bliki/MonolithFirst.html)
- Sam Newman: *Building Microservices* (Chapter on when to extract services)
- YAGNI Principle: "You Aren't Gonna Need It"

## Review and Approval

- **Proposed by**: Modernization Agent
- **Review Status**: Pending human review
- **Approval Date**: TBD
- **Implementation Status**: Not yet started (will begin in Slice 0)
