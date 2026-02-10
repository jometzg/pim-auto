# High-Level Design (HLD) - PIM Auto

**Document Status**: Current State (As-Is)  
**Last Updated**: 2026-02-10  
**Repository**: jometzg/pim-auto

## Executive Summary

This document describes the **current state** of the pim-auto repository. As of this documentation date, the repository is in a **planning/specification phase** and contains no implemented source code. This HLD reflects what exists today, not the intended future implementation.

## System Overview

The pim-auto repository currently contains:
- A comprehensive README.md specification (`/README.md`)
- GitHub workflow configurations (`/.github/workflows/ci.yml`)
- Agent configuration files (`/.github/agents/`)
- Skill definition files (`/.github/skills/`)

The README.md describes a **proposed** Azure PIM Activity Audit Agent - an intelligent monitoring tool for Azure Privileged Identity Management activations. However, this application is not yet implemented.

## Major Components

### 1. Documentation Assets (IMPLEMENTED)

**Location**: `/README.md`

The repository contains a detailed specification document that describes:
- Purpose: Azure PIM activity monitoring and correlation
- Features: 10 proposed capabilities including PIM detection, AI-powered query generation, activity correlation
- Non-functional requirements: 10 requirements covering Python 3.11+, Azure OpenAI, authentication, modularity
- Prerequisites: Azure services needed (OpenAI, Log Analytics)
- Usage examples: Interactive chat mode and batch mode scenarios

### 2. GitHub Automation Infrastructure (IMPLEMENTED)

**Location**: `/.github/`

#### Workflows
- `/.github/workflows/ci.yml`: CI/CD pipeline configuration

#### Agent Configurations
Five agent definition files exist:
- `/.github/agents/documentation.agent.md`: Documentation generation agent
- `/.github/agents/testing.agent.md`: Test synthesis agent
- `/.github/agents/modernisation.agent.md`: Architecture modernisation agent
- `/.github/agents/implementation.agent.md`: Implementation agent
- `/.github/agents/intelligent-migration.agent.md`: Migration orchestration agent

#### Skill Definitions
Five skill files provide operating procedures:
- `/.github/skills/system-discovery.skill.md`: Current system documentation procedure
- `/.github/skills/test-synthesis.skill.md`: Test creation guidelines
- `/.github/skills/architecture-reasoning.skill.md`: Architecture analysis procedure
- `/.github/skills/incremental-refactoring.skill.md`: Refactoring methodology
- `/.github/skills/intelligent-application-migration.skill.md`: Migration program design

### 3. Application Code (NOT IMPLEMENTED)

**Status**: Does not exist

According to the README specification, the following components are planned but not yet implemented:
- Python 3.11+ source code
- Azure OpenAI integration
- Log Analytics query engine
- Interactive chat interface
- Batch processing mode
- Report generation
- Authentication layer

## Data Stores and External Dependencies

### Current State
No data stores or external dependencies are currently implemented in the codebase.

### Specified Dependencies (from README.md)
The README indicates future dependencies on:
- **Azure OpenAI Service**: For GPT-4o model deployment
- **Azure Log Analytics**: For AuditLogs and AzureActivity table access
- **Azure CLI**: For local development authentication
- **Python 3.11+**: Runtime environment

## Runtime Assumptions

### Current State
The repository does not currently run as an application. There is no:
- Python code to execute
- Dependencies to install
- Services to start
- Ports to bind

### Specified Runtime Model (from README.md)
The README describes two intended operational modes:
1. **Interactive Chat Mode**: User-driven queries via CLI
2. **Batch Mode**: Automated scanning triggered via `python main.py --mode batch`

## Architecture Diagram

```
Current State:
┌─────────────────────────────────────────┐
│     pim-auto Repository (Empty)         │
│                                          │
│  ├─ README.md (Specification)           │
│  ├─ .github/                            │
│  │   ├─ workflows/ci.yml                │
│  │   ├─ agents/ (5 files)               │
│  │   └─ skills/ (5 files)               │
│  └─ .git/                               │
└─────────────────────────────────────────┘

Planned State (per README.md):
┌────────────────────────────────────────────────────────────┐
│                    PIM Auto Application                     │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐   ┌──────────────┐  │
│  │   Chat UI    │    │  Batch Mode  │   │   Reports    │  │
│  └──────┬───────┘    └──────┬───────┘   └──────▲───────┘  │
│         │                   │                   │          │
│         └───────────┬───────┘                   │          │
│                     │                           │          │
│            ┌────────▼────────────┐              │          │
│            │  Query Orchestrator │──────────────┘          │
│            └────────┬────────────┘                         │
│                     │                                      │
│         ┌───────────┼───────────┐                         │
│         │           │           │                         │
│    ┌────▼────┐ ┌───▼─────┐ ┌──▼──────┐                  │
│    │ Azure   │ │  Log    │ │  AI     │                  │
│    │ OpenAI  │ │Analytics│ │ Agent   │                  │
│    └─────────┘ └─────────┘ └─────────┘                  │
└────────────────────────────────────────────────────────────┘
```

## System Integration Points

### Current State
No integration points exist in the current codebase.

### Specified Integrations (from README.md)
- Azure OpenAI API: Natural language processing and Kusto query generation
- Azure Log Analytics API: Query execution for AuditLogs and AzureActivity
- Azure Monitor Action Groups: Alert/report delivery (mentioned in overview)

## Deployment Model

### Current State
Not applicable - no deployable artifacts exist.

### Specified Model (from README.md)
- Supports Azure Managed Identity authentication
- Supports Azure CLI authentication for local development
- Uses DefaultAzureCredential pattern

## Known Limitations

1. **No Implementation**: The repository contains only specifications and automation infrastructure, no application code
2. **No Tests**: No test files or test infrastructure exists
3. **No Dependencies**: No requirements.txt, pyproject.toml, or similar dependency manifest
4. **No Build Process**: No build scripts or compilation steps defined
5. **CI Workflow Status**: The ci.yml workflow exists but its configuration is unknown (file not analyzed in detail)

## Technical Debt Observations

1. **Specification-Implementation Gap**: Large gap between detailed README specification and empty codebase
2. **No Project Structure**: No directory layout for src/, tests/, config/, etc.
3. **No Development Setup**: No setup.py, pyproject.toml, or developer onboarding guide
4. **No License File**: No LICENSE file present
5. **No Contributing Guide**: No CONTRIBUTING.md for external contributors

## Security Considerations

### Current State
No security concerns in current state as no code exists.

### Specified Security Model (from README.md)
- Azure DefaultAzureCredential for secure authentication
- Managed identity support for production
- Azure CLI authentication for local development

## Compliance and Governance

The repository includes a comprehensive agent-based governance model through:
- `/github/agents/`: 5 specialized agent configurations
- `/.github/skills/`: 5 skill-based procedures

This suggests a structured approach to future development with clear role separation and automated quality gates.

## Future State References

This HLD intentionally **does not** describe the future architecture. For planned features and capabilities, refer to:
- `/README.md`: Complete specification of intended functionality
- `/.github/agents/modernisation.agent.md`: Architecture planning agent
- `/.github/skills/intelligent-application-migration.skill.md`: Migration methodology

## Glossary

- **PIM**: Privileged Identity Management (Azure AD feature)
- **Kusto**: Query language for Azure Log Analytics
- **ADR**: Architecture Decision Record
- **HLD**: High-Level Design
- **LLD**: Low-Level Design
