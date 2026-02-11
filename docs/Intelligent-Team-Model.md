# Intelligent Team Model - PIM Auto

**Document Status**: Active  
**Last Updated**: 2026-02-11  
**Repository**: jometzg/pim-auto  
**Programme Lead**: TBD

## Executive Summary

This document defines the **AI-augmented team structure** for delivering the PIM Auto migration. It specifies roles, responsibilities, decision authority, and expected productivity gains from GitHub Copilot and specialized AI agents.

### Team Philosophy

- **Small, cross-functional team**: Minimize coordination overhead
- **AI augmentation, not replacement**: Humans make decisions, AI accelerates execution
- **Clear accountability**: Every deliverable has a named owner
- **Explicit decision rights**: No ambiguity about who approves what

### Expected Productivity Impact

**Baseline** (traditional development without AI):
- Slice 0: 5 days
- Slice 1: 7 days
- Slice 2: 5 days
- Slice 3: 4 days
- Slice 4: 3 days
- **Total: 24 days**

**With AI Augmentation**:
- Slice 0: 3 days (-40% time)
- Slice 1: 4 days (-43% time)
- Slice 2: 3 days (-40% time)
- Slice 3: 2 days (-50% time)
- Slice 4: 2 days (-33% time)
- **Total: 14 days (-42% overall)**

---

## Team Structure

### Core Team Roles

| Role | Count | Commitment | Primary Responsibilities | AI Augmentation |
|------|-------|------------|--------------------------|-----------------|
| **Executive Sponsor** | 1 | 5-10% | Funding approval, go/no-go decisions, escalation resolution | None - strategic decision-making |
| **Programme Lead** | 1 | 20-30% | Timeline management, risk tracking, stakeholder communication | M365 Copilot for status reports, documentation |
| **Technical Lead / Architect** | 1 | 50-80% | Architecture decisions, code review, technical approvals | GitHub Copilot for code review, documentation |
| **Developer** | 1-2 | 100% | Implementation, testing, documentation | **GitHub Copilot** (code generation), **Implementation Agent** (autonomous coding) |
| **DevOps Engineer** | 1 | 20-40% | CI/CD pipeline, Azure deployment, monitoring setup | GitHub Copilot for IaC, automation scripts |
| **QA / Test Engineer** | 1 | 30-50% | Test strategy, test execution, quality gates | **Testing Agent** (test synthesis), GitHub Copilot for test code |

**Total Team Size**: 4-5 people (including part-time roles)

**Total Effort**: ~2.5 FTE across 14 days = **35 person-days** (vs. 48 without AI augmentation)

---

## Detailed Role Definitions

### 1. Executive Sponsor

**Decision Authority**: ⭐⭐⭐⭐⭐ (Highest)

**Responsibilities**:
- Approve programme budget and timeline
- Make go/no-go decisions at major phase boundaries (Slice 2→3, Slice 4→Production)
- Resolve escalations that exceed Tech Lead authority
- Sign off on production deployment

**Key Deliverables**:
- Programme charter approval
- Phase gate approvals (Slice 2→3, 4→Production)
- Budget allocation decisions

**AI Augmentation**: None
- Strategic decisions require human judgment
- Risk acceptance requires accountability

**Success Metrics**:
- Clear, timely decisions at phase gates
- No scope creep without explicit approval
- Budget variance within ±10%

---

### 2. Programme Lead / Project Manager

**Decision Authority**: ⭐⭐⭐⭐ (High)

**Responsibilities**:
- Manage programme timeline and milestones
- Track risk register and mitigation actions
- Coordinate team activities and stakeholder communication
- Escalate blockers to Executive Sponsor
- Update programme status weekly

**Key Deliverables**:
- Weekly status reports
- Updated risk register
- Timeline and milestone tracking
- Stakeholder communication (emails, presentations)

**AI Augmentation**: **M365 Copilot**
- **Use for**: Drafting status reports, meeting summaries, stakeholder emails
- **Productivity gain**: 30-40% time savings on administrative tasks
- **Example prompt**: "Summarize this week's progress on Slice 1: [paste git commits and test results]. Highlight risks and blockers."

**Success Metrics**:
- Status reports delivered on time (weekly)
- Risk register current (updated within 48 hours of issue identification)
- Stakeholder satisfaction >80%

---

### 3. Technical Lead / Architect

**Decision Authority**: ⭐⭐⭐⭐ (High - technical decisions)

**Responsibilities**:
- Review and approve architectural decisions (ADRs)
- Approve slice completion (gate reviews: Slice 0→1, 1→2, 2→3)
- Conduct code reviews (human review after AI code review)
- Resolve technical escalations
- Ensure alignment with Target Architecture

**Key Deliverables**:
- ADR approvals
- Code review approvals on all PRs
- Technical risk assessments
- Architecture compliance validation

**AI Augmentation**: **GitHub Copilot + Code Review Tool**
- **Use for**: 
  - Initial code review (automated via code_review tool)
  - Documentation generation
  - Test case suggestions
  - Refactoring recommendations
- **Productivity gain**: 40-50% time savings on code review (AI filters out 80% of simple issues)
- **Example workflow**:
  1. Implementation agent creates PR
  2. AI code_review tool provides initial feedback
  3. Developer addresses AI feedback
  4. Tech Lead performs final human review (20% of original effort)

**Success Metrics**:
- Code review turnaround <24 hours
- Zero critical security vulnerabilities in production
- Architecture conformance on all PRs

---

### 4. Developer

**Decision Authority**: ⭐⭐ (Low - implementation details only)

**Responsibilities**:
- Implement code changes for assigned slices
- Write unit and integration tests
- Fix bugs identified in testing or code review
- Update documentation (code comments, README updates)
- Respond to code review feedback

**Key Deliverables**:
- Implemented slices (Python code, tests)
- Unit test coverage >80%
- Updated documentation per slice
- Bug fixes

**AI Augmentation**: **GitHub Copilot + Implementation Agent** (primary beneficiaries)
- **GitHub Copilot** (inline code suggestions):
  - Code completion (functions, classes, tests)
  - Boilerplate generation (imports, docstrings, type hints)
  - Test case generation from function signatures
  - **Productivity gain**: 50-60% faster coding for repetitive tasks
  
- **Implementation Agent** (autonomous slice execution):
  - Given slice specification, implements entire slice autonomously
  - Generates code, tests, documentation
  - Runs CI pipeline, fixes issues
  - **Productivity gain**: 70-80% time savings on well-specified slices
  
**Example workflow (Slice 1)**:
1. Tech Lead assigns Slice 1 to Implementation Agent
2. Implementation Agent reads Migration-Plan.md, creates code, tests
3. Implementation Agent runs linting, testing, fixes issues
4. Implementation Agent creates PR with all changes
5. Developer reviews PR (10% of normal implementation time)
6. Developer addresses any implementation agent errors or gaps
7. Code review tool provides feedback
8. Developer fixes issues, Tech Lead approves

**Success Metrics**:
- Test coverage >80% on new code
- Linting passes (ruff, mypy)
- Zero P0 bugs in production
- Slice implementation time within estimates

---

### 5. DevOps Engineer

**Decision Authority**: ⭐⭐⭐ (Medium - infrastructure decisions)

**Responsibilities**:
- Maintain CI/CD pipeline (.github/workflows/ci.yml)
- Configure Azure deployment (Container Apps, IaC)
- Set up monitoring and logging (Application Insights, Log Analytics)
- Manage environment configurations (dev, staging, production)
- Troubleshoot deployment issues

**Key Deliverables**:
- CI/CD pipeline operational (Slice 0)
- Azure Container Apps deployment (Slice 3)
- Monitoring dashboards (Slice 3)
- Deployment runbook updates
- Environment configuration management

**AI Augmentation**: **GitHub Copilot**
- **Use for**: 
  - IaC code generation (Bicep, Terraform)
  - CI/CD pipeline configuration (GitHub Actions YAML)
  - Shell scripts for automation
  - Dockerfile optimization
- **Productivity gain**: 40-50% time savings on IaC and automation scripts
- **Example prompt**: "Generate Bicep template for Azure Container Apps deployment with managed identity and Log Analytics integration"

**Success Metrics**:
- CI/CD pipeline uptime >99%
- Deployment success rate >95%
- Mean time to deployment (MTTD) <15 minutes
- Zero production incidents caused by deployment issues

---

### 6. QA / Test Engineer

**Decision Authority**: ⭐⭐⭐ (Medium - quality gates)

**Responsibilities**:
- Define test strategy (Test-Strategy.md)
- Review and validate test coverage
- Execute integration and E2E tests
- Identify quality gaps and risks
- Approve slice quality before production (quality gate)

**Key Deliverables**:
- Test strategy document (Slice 0)
- Integration test suite (Slice 2)
- E2E test suite (Slice 4)
- Quality gate approvals per slice
- Bug reports and test results

**AI Augmentation**: **Testing Agent + GitHub Copilot**
- **Testing Agent** (autonomous test generation):
  - Generates test cases from code specifications
  - Creates unit tests, integration tests
  - Suggests edge cases and negative test scenarios
  - **Productivity gain**: 60-70% time savings on test case creation
  
- **GitHub Copilot** (inline test suggestions):
  - Test boilerplate (fixtures, mocks, assertions)
  - Parametrized test generation
  - **Productivity gain**: 40-50% time savings on test implementation

**Example workflow**:
1. Developer implements feature
2. Testing Agent analyzes code, generates test cases
3. QA reviews test cases (adds missing edge cases)
4. Developer runs tests, fixes failures
5. QA validates coverage and quality gate

**Success Metrics**:
- Test coverage >80% (unit), >60% (integration)
- Zero critical bugs reach production
- Quality gate review turnaround <24 hours
- Test suite execution time <5 minutes (unit), <15 minutes (integration)

---

## Accountability Matrix (RACI)

| Activity | Sponsor | Prog Lead | Tech Lead | Developer | DevOps | QA |
|----------|---------|-----------|-----------|-----------|--------|-----|
| **Programme Charter** | A | R | C | I | I | I |
| **Slice 0: Foundation** | I | A | A/R | R | R | C |
| **Slice 1: Core Logic** | I | A | A | R | C | C/R |
| **Slice 2: Dual-Mode** | I | A | A | R | C | C/R |
| **Slice 3: Production** | A | R | A | C | R | C |
| **Slice 4: Validation** | A | R | A | C | C | R |
| **Code Review** | - | - | A/R | I | - | C |
| **Architecture Decisions** | I | C | A/R | I | C | I |
| **CI/CD Pipeline** | - | C | C | I | A/R | I |
| **Production Deployment** | A | R | C | I | R | C |
| **Risk Management** | A | R | C | I | I | I |

**Legend**:
- **R** = Responsible (does the work)
- **A** = Accountable (final decision authority)
- **C** = Consulted (provides input)
- **I** = Informed (kept in the loop)

---

## Escalation Paths

### Technical Blockers
```
Developer → Implementation Agent (retry/fix) → Tech Lead → Programme Lead → Sponsor
```

**SLA**: 
- Level 1 (Developer → Tech Lead): 4 hours
- Level 2 (Tech Lead → Programme Lead): 24 hours
- Level 3 (Programme Lead → Sponsor): 48 hours

### Scope Changes
```
Developer/QA → Tech Lead → Programme Lead → Sponsor (if budget impact >10%)
```

**SLA**:
- Level 1 (Tech Lead decision): Same day
- Level 2 (Programme Lead decision): 2 business days
- Level 3 (Sponsor decision): 5 business days

### Security Issues
```
Code Review Tool → Developer (fix) → Tech Lead (review) → Security Review (if critical)
```

**SLA**:
- Critical: Fix within 24 hours, block production deployment
- High: Fix before next slice, can proceed with approval
- Medium/Low: Track in backlog, address in next release

### Timeline Delays
```
Tech Lead (identifies) → Programme Lead (assesses impact) → Sponsor (approves mitigation)
```

**SLA**:
- Timeline variance >20%: Escalate within 1 business day
- Sponsor decision on mitigation: Within 3 business days

---

## Communication Plan

### Daily
- **Stand-up** (async via Slack/Teams): Developer + Tech Lead
  - What I completed yesterday
  - What I'm working on today
  - Any blockers

### Weekly
- **Status Report** (Programme Lead → Sponsor + stakeholders)
  - Progress summary (slices completed, in progress)
  - Risk register update
  - Timeline tracking (actual vs. planned)
  - Next week's plan

### Per Slice (Phase Gates)
- **Slice Review Meeting** (all roles)
  - Demo implemented functionality
  - Review exit criteria compliance
  - Go/no-go decision for next slice
  - Risk assessment update

---

## AI Tool Training and Adoption

### GitHub Copilot
- **Training**: 2-hour workshop on effective prompt engineering
- **Best practices**:
  - Write clear function/class names and docstrings (Copilot context)
  - Review and validate all AI suggestions (never blindly accept)
  - Use Copilot for boilerplate, humans for business logic
- **Metrics**: Track Copilot acceptance rate (target: 30-40%)

### Implementation Agent
- **Training**: 1-hour workshop on slice specification format
- **Best practices**:
  - Provide clear, detailed slice specifications (see Migration-Plan.md)
  - Review agent output before approving PR
  - Use agent for well-defined tasks, humans for ambiguous requirements
- **Metrics**: Track agent success rate per slice (target: >80%)

### Code Review Tool
- **Training**: 30-minute demo of tool output
- **Best practices**:
  - Run code review before human review
  - Address all legitimate AI feedback
  - Flag false positives for tool improvement
- **Metrics**: Track % of PRs passing AI review on first attempt (target: >70%)

---

## Success Metrics

### Team Productivity
- **Velocity**: Slices completed per week (target: 1 slice per 3-5 days)
- **AI Augmentation Impact**: Actual vs. baseline timeline (target: >30% time savings)
- **Code Quality**: Test coverage, linting pass rate, production bugs (target: >80% coverage, <5 P2+ bugs/slice)

### Team Collaboration
- **Code Review Turnaround**: Time from PR creation to approval (target: <24 hours)
- **Escalation Response**: Time to resolution per SLA (target: 100% SLA compliance)
- **Stakeholder Satisfaction**: Survey after each slice (target: >80%)

### Delivery Success
- **On-Time Delivery**: Slices completed within estimated timeline (target: >80%)
- **Quality Gates**: % of slices passing exit criteria on first attempt (target: >70%)
- **Rollback Events**: Number of rollbacks required (target: 0)

---

## Conclusion

This intelligent team model balances:
1. **Small team size** (4-5 people) to minimize coordination
2. **AI augmentation** (42% productivity gain) to maximize efficiency
3. **Clear accountability** (RACI matrix) to avoid confusion
4. **Explicit decision rights** (authority levels) to speed approvals
5. **Structured escalation** (SLAs) to resolve blockers quickly

**Key Success Factors**:
- Humans make strategic and architectural decisions
- AI accelerates implementation and testing
- Clear accountability prevents bottlenecks
- Explicit communication plan maintains alignment

**Next Actions**:
1. Assign specific people to named roles
2. Schedule initial training on AI tools
3. Confirm escalation paths and SLAs
4. Begin Slice 1 execution with Implementation Agent
