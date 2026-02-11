# Intelligent Migration Plan - PIM Auto

**Document Status**: Active  
**Last Updated**: 2026-02-11  
**Repository**: jometzg/pim-auto  
**Programme Lead**: TBD  
**Review Cycle**: After each slice completion

## Executive Summary

This plan defines the **programme-level governance** for migrating the PIM Auto application from specification to production-ready containerized system. It establishes risk controls, decision gates, and success metrics aligned with Chaos Report research to maximize delivery success probability.

### Key Programme Objectives

1. **Minimize delivery risk** through incremental, testable slices
2. **Maximize ROI** through AI-augmented team productivity
3. **Maintain transparency** with explicit decision gates and metrics
4. **Enable rollback** at every phase boundary
5. **Preserve behavior** without introducing regressions

### Success Probability Enhancement

This programme applies evidence-based practices from the Standish Group Chaos Report to address the top project failure factors:

| Risk Factor (Chaos Report) | Mitigation Strategy | Implementation |
|---------------------------|---------------------|----------------|
| Lack of executive support | Explicit sponsor role with sign-off gates | Human approval required at each phase boundary |
| User involvement | Clear acceptance criteria per slice | Developer testing with real Azure resources |
| Scope clarity | Fixed 5-slice roadmap with entry/exit criteria | See Migration Phases below |
| Team size/skills | Small, AI-augmented team model | See Intelligent-Team-Model.md |
| Delivery methodology | Incremental strangler pattern | See detailed slice definitions |

**Baseline Success Probability**: Industry average for custom software projects: **31% deliver on time, on budget, with required features** (Chaos Report 2020)

**Target Success Probability**: **>80%** through slice-based delivery, AI augmentation, and explicit risk controls

---

## Migration Objectives

### Primary Objectives

1. **Functional Completeness**: Implement all 10 features specified in `/README.md`
   - PIM activation detection
   - AI-powered query generation
   - Self-correcting queries
   - Interactive chat interface
   - Activity correlation
   - Risk assessment
   - Markdown report generation
   - Secure authentication
   - Batch mode
   - Comprehensive logging

2. **Non-Functional Compliance**: Meet all 10 non-functional requirements
   - Python 3.11+
   - Azure OpenAI integration
   - Secure authentication (DefaultAzureCredential)
   - Error handling and logging
   - Dual-mode operation (interactive + batch)
   - Markdown reporting
   - Modularity and maintainability
   - Performance (concurrent users)
   - Comprehensive testing
   - Clear documentation

3. **Operational Readiness**: Production-grade deployment capability
   - Containerized deployment to Azure Container Apps
   - Health checks and monitoring
   - Operational runbook
   - Rollback procedures

### Secondary Objectives

1. **Team Capability Building**: Establish repeatable AI-augmented delivery pattern
2. **Documentation Excellence**: Maintain up-to-date, factual system documentation
3. **Risk Posture**: Zero unaddressed security vulnerabilities at production deployment

---

## Phased Roadmap

The migration follows a **5-slice incremental approach** using the strangler pattern. Each slice is independently testable and reversible.

### Slice Definitions

| Slice | Phase | Focus | Deliverables | Risk | Duration |
|-------|-------|-------|-------------|------|----------|
| **0** | Foundation | Project structure, CI, baseline tests, container skeleton | Dockerfile, pyproject.toml, CI pipeline, Developer-Setup.md, baseline tests | Low | 3-5 days |
| **1** | Core Implementation | Azure integration, core business logic | Azure client wrappers, 4 core modules, unit tests (>80% coverage) | Medium | 5-7 days |
| **2** | Dual-Mode Support | Interactive CLI and batch mode | CLI interface, batch mode, full feature parity | Low-Medium | 3-5 days |
| **3** | Production Readiness | Deployment automation, monitoring | Container Apps deployment, monitoring, runbook updates | Low | 3-4 days |
| **4** | Validation | End-to-end testing, performance validation | E2E tests, performance benchmarks, final documentation | Low | 2-3 days |

**Total Timeline**: 16-24 days (single developer, part-time) or 8-12 days (full-time with AI augmentation)

### Current Status

- ✅ **Slice 0**: COMPLETED (committed ac933fc)
  - Docker infrastructure established
  - CI/CD pipeline operational
  - Baseline tests passing (3/3)
  - Developer setup documented
  
- 🎯 **Slice 1**: IN PROGRESS (this document establishes governance for execution)
  - Entry criteria met
  - Governance framework established
  - Ready for implementation agent execution

---

## Explicit Success Criteria Per Phase

### Slice 0 Success Criteria (ACHIEVED)

**Must Pass**:
- ✅ Docker image builds without errors
- ✅ Container runs successfully
- ✅ CI/CD pipeline executes (lint, test, build)
- ✅ All baseline tests pass (3/3)
- ✅ Developer can follow setup guide and run tests locally

**Deliverables**:
- ✅ Dockerfile with non-root user
- ✅ pyproject.toml with all dev dependencies
- ✅ CI workflow (.github/workflows/ci.yml)
- ✅ Baseline unit tests (tests/unit/)
- ✅ Developer-Setup.md

### Slice 1 Success Criteria (TARGET)

**Must Pass**:
- ✅ All core modules implemented (4 modules: PIM detector, activity correlator, query generator, risk assessor)
- ✅ Azure client wrappers functional (auth, log analytics, OpenAI)
- ✅ Configuration management working (environment variable based)
- ✅ Unit tests pass with >80% coverage
- ✅ Linting and type checking pass (ruff, mypy)
- ✅ Docker image builds and runs basic functionality
- ✅ CI/CD pipeline passing (all gates green)
- ✅ Basic smoke test with real Azure resources (dev environment)

**Deliverables**:
- Complete `src/pim_auto/` implementation
- Comprehensive unit tests with Azure service mocking
- Updated Dockerfile with working application
- Integration test documentation

**Success Validation**:
A developer can:
1. Set Azure environment variables (AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, LOG_ANALYTICS_WORKSPACE_ID)
2. Run `python src/pim_auto/main.py`
3. See PIM activations detected from their Azure tenant
4. All unit tests pass (pytest with >80% coverage)

### Slice 2 Success Criteria (FUTURE)

**Must Pass**:
- ✅ Interactive CLI mode functional
- ✅ Batch mode functional
- ✅ Mode selection working (--mode flag)
- ✅ All 10 features implemented and testable
- ✅ Integration tests pass
- ✅ User experience documented

**Deliverables**:
- CLI interface implementation
- Batch mode implementation
- Updated tests for both modes
- Updated README with usage examples

### Slice 3 Success Criteria (FUTURE)

**Must Pass**:
- ✅ Deployment to Azure Container Apps succeeds
- ✅ Health checks operational
- ✅ Monitoring configured (Log Analytics, Application Insights)
- ✅ Runbook includes deployment procedures
- ✅ Rollback tested and documented

**Deliverables**:
- Azure deployment scripts/IaC
- Updated runbook
- Monitoring dashboard definitions
- Deployment checklist

### Slice 4 Success Criteria (FUTURE)

**Must Pass**:
- ✅ End-to-end tests pass in production-like environment
- ✅ Performance benchmarks meet targets (concurrent users, query latency)
- ✅ All documentation current and accurate
- ✅ Security scan clean (CodeQL, dependency scanning)
- ✅ Production deployment approved

**Deliverables**:
- E2E test suite
- Performance test results
- Security assessment report
- Production deployment approval

---

## Governance Framework

### Human Decision Gates

Each slice requires **explicit human approval** before proceeding to next slice:

| Gate | Decision Authority | Criteria | Artifacts Required |
|------|-------------------|----------|-------------------|
| **Slice 0 → 1** | Tech Lead / Architect | Foundation stable, CI green | Passing CI pipeline, Docker build success |
| **Slice 1 → 2** | Tech Lead + Product Owner | Core logic functional, tests passing | Unit test report (>80% coverage), smoke test results |
| **Slice 2 → 3** | Tech Lead + Product Owner | Feature complete, UX validated | Integration test results, user acceptance |
| **Slice 3 → 4** | Tech Lead + Operations | Deployment successful, monitoring active | Deployment logs, monitoring dashboard |
| **Slice 4 → Production** | Product Owner + Sponsor | All success criteria met, security approved | Security scan clean, performance benchmarks, sponsor sign-off |

### Review Cadences

- **Daily**: Implementation agent progress updates (via PR comments)
- **Per Slice**: Human approval gate review
- **Weekly**: Programme status update (risk register, timeline)
- **Monthly**: ROI and cost tracking review

### Escalation Paths

1. **Technical Blockers**: Implementation agent → Documentation agent (for discovery) → Tech Lead
2. **Scope Changes**: Product Owner → Programme Lead → Sponsor
3. **Security Issues**: Security scan → Tech Lead → Security Review (if high/critical)
4. **Timeline Delays**: Tech Lead → Programme Lead → Sponsor

### Rollback Strategy

Each slice maintains an **independent rollback path**:

- **Slice 1 Rollback**: Revert to Slice 0 (infrastructure only, no business logic)
  - Revert all `src/pim_auto/` files except placeholders
  - Revert test files in `tests/unit/`
  - Revert Dockerfile to Slice 0 version
  - Risk: Low (no production deployment yet)

- **Slice 2 Rollback**: Revert to Slice 1 (core logic only, no dual-mode)
  - Revert CLI interface additions
  - Revert batch mode additions
  - Keep core modules and Azure clients
  - Risk: Low-Medium (loss of user interface work)

- **Slice 3 Rollback**: Revert to Slice 2 (local/dev only, no production deployment)
  - Remove Azure Container Apps resources
  - Keep application code
  - Risk: Medium (potential Azure resource cleanup)

- **Slice 4 Rollback**: Revert to Slice 3 (production deployment, basic monitoring)
  - Disable E2E tests
  - Keep core functionality
  - Risk: Low (documentation and test removal only)

### Audit and Telemetry

- **Git History**: All changes tracked via PR commits
- **CI/CD Logs**: Build, test, lint results retained
- **Code Review**: All PRs reviewed by code_review tool + human approval
- **Security Scanning**: CodeQL and dependency scanning on every PR
- **Test Coverage**: Coverage reports tracked over time (target: >80%)

---

## AI Augmentation Positioning

### Role of AI Tools (GitHub Copilot, Implementation Agent)

- **Drafting Engine**: Generate initial code implementations, tests, documentation
- **Accelerator**: Speed up repetitive tasks (test case generation, boilerplate code)
- **Quality Checker**: Code review automation, linting, security scanning
- **NOT Decision Authority**: Humans approve phase gates, architecture changes, production deployments

### Human-AI Collaboration Model

```
Human Roles                     AI Roles
─────────────────────          ─────────────────────
- Strategy and priorities  ←→  - Implementation suggestions
- Architecture decisions   ←→  - Code generation
- Risk acceptance          ←→  - Risk identification
- Production approval      ←→  - Quality automation
- Scope changes            ←→  - Test case generation
```

### Productivity Expectations

See `/docs/ROI-and-Budget.md` for detailed productivity assumptions and ROI model.

---

## Risk Management

See `/docs/Risk-and-Governance.md` for detailed risk register and control mechanisms.

---

## Conclusion

This intelligent migration plan provides:
1. **Clear roadmap** with 5 defined slices and explicit success criteria
2. **Risk mitigation** aligned with Chaos Report research
3. **Transparent governance** with human decision gates at phase boundaries
4. **AI augmentation** positioned as accelerator, not decision authority
5. **Rollback capability** at every phase

**Next Actions**:
1. ✅ Slice 0 complete (human approved)
2. 🎯 Execute Slice 1 via implementation agent
3. Human review and approval before Slice 2

**Programme Success**: Measured by on-time, on-budget delivery with all 10 features functional and production-ready deployment capability established.
