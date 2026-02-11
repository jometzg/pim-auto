# Risk and Governance - PIM Auto Migration

**Document Status**: Active  
**Last Updated**: 2026-02-11  
**Repository**: jometzg/pim-auto  
**Risk Owner**: Programme Lead  
**Review Cycle**: Weekly + after incidents

## Executive Summary

This document defines the **risk management framework** and **governance controls** for the PIM Auto migration programme. It maps risks to Chaos Report failure patterns and establishes human-in-the-loop decision points to maximize delivery success.

### Risk Posture

**Approach**: **Risk-averse with controlled innovation**
- Prioritize delivery certainty over speed
- No production deployment without security clearance
- Human approval required at all phase boundaries
- Rollback capability maintained at every stage

**Risk Tolerance**:
- **Technical Risk**: Medium (accept moderate technical complexity for quality gains)
- **Schedule Risk**: Low (prefer timeline extension over cutting corners)
- **Security Risk**: Zero tolerance (no production deployment with open critical/high vulnerabilities)
- **Scope Risk**: Low (fixed scope based on README.md specification)

---

## Chaos Report Failure Mapping

The Standish Group Chaos Report identifies top factors for project failure. This section maps each factor to our specific risks and controls.

### 1. Lack of Executive Support

**Chaos Report Finding**: Projects without active executive support have **3x higher failure rate**

**Risk in PIM Auto**:
- Executive sponsor assigned but not actively engaged
- Budget approval unclear or delayed
- Production deployment blocked by lack of executive sign-off

**Controls**:
| Control | Type | Responsibility | Frequency |
|---------|------|----------------|-----------|
| Executive Sponsor assignment documented | Preventive | Programme Lead | Once (programme start) |
| Phase gate sign-offs required (Slice 2→3, 4→Prod) | Detective | Executive Sponsor | Per phase (2 gates) |
| Weekly status report to sponsor | Detective | Programme Lead | Weekly |
| Budget variance escalation (>10%) | Detective | Programme Lead | As needed |

**Mitigation**:
- If sponsor unresponsive: Programme Lead escalates to sponsor's manager within 48 hours
- If budget blocked: Reduce scope (defer Slice 4 validation) or extend timeline

---

### 2. Lack of User Involvement

**Chaos Report Finding**: Projects without user feedback have **2.5x higher failure rate**

**Risk in PIM Auto**:
- Application built without end-user validation
- UX issues discovered only after production deployment
- Feature misalignment with actual user needs

**Controls**:
| Control | Type | Responsibility | Frequency |
|---------|------|----------------|-----------|
| Developer testing with real Azure tenant | Preventive | Developer | Per slice |
| Acceptance criteria include UX validation | Preventive | QA | Slice 2 (CLI/batch modes) |
| Demo to internal stakeholders before production | Detective | Programme Lead | Slice 4 |
| Production pilot with limited users | Preventive | Programme Lead | Before full rollout |

**Mitigation**:
- If UX issues found: Create fast-follow PR within 1 week
- If feature misalignment: Escalate to Executive Sponsor for scope decision (add to backlog vs. delay production)

---

### 3. Unclear or Changing Scope

**Chaos Report Finding**: Projects with scope creep have **2x higher failure rate**

**Risk in PIM Auto**:
- Scope drift beyond README.md specification
- "Nice-to-have" features added without approval
- Timeline extended due to uncontrolled scope growth

**Controls**:
| Control | Type | Responsibility | Frequency |
|---------|------|----------------|-----------|
| Fixed scope baseline (README.md specification) | Preventive | Tech Lead | Once (programme start) |
| Slice definitions locked (Migration-Plan.md) | Preventive | Tech Lead | Once (programme start) |
| Scope change approval required (Executive Sponsor) | Preventive | Programme Lead | As needed |
| Backlog for "out-of-scope" features | Preventive | Programme Lead | As needed |

**Mitigation**:
- If scope change requested: Programme Lead assesses impact (timeline, budget, risk)
- If change approved: Update Migration-Plan.md, adjust timeline, re-baseline
- If change rejected: Add to backlog for future release

---

### 4. Inadequate Team Skills

**Chaos Report Finding**: Projects with skill gaps have **2.2x higher failure rate**

**Risk in PIM Auto**:
- Developer lacks Azure integration experience
- Team unfamiliar with AI-augmented workflows
- DevOps engineer unfamiliar with Azure Container Apps

**Controls**:
| Control | Type | Responsibility | Frequency |
|---------|------|----------------|-----------|
| AI tool training (GitHub Copilot, agents) | Preventive | Programme Lead | Once (programme start) |
| Tech Lead code review (all PRs) | Detective | Tech Lead | Per PR |
| Pair programming for complex Azure integrations | Preventive | Tech Lead + Developer | As needed |
| Knowledge transfer sessions | Preventive | Tech Lead | Weekly |

**Mitigation**:
- If skill gap identified: Schedule 1:1 knowledge transfer session within 48 hours
- If severe skill gap: Engage external consultant or extend timeline for training

---

### 5. Unrealistic Schedule

**Chaos Report Finding**: Projects with unrealistic timelines have **2x higher failure rate**

**Risk in PIM Auto**:
- AI productivity assumptions too optimistic
- Timeline underestimates integration complexity
- External dependencies (Azure service availability) cause delays

**Controls**:
| Control | Type | Responsibility | Frequency |
|---------|------|----------------|-----------|
| Conservative baseline estimates (without AI) | Preventive | Tech Lead | Once (programme start) |
| AI productivity tracking (actual vs. expected) | Detective | Programme Lead | Weekly |
| Timeline variance monitoring (>20% = escalation) | Detective | Programme Lead | Weekly |
| Contingency buffer (20% added to timeline) | Preventive | Programme Lead | Once (programme start) |

**Mitigation**:
- If timeline variance >20%: Programme Lead escalates to Executive Sponsor within 1 business day
- If delay unavoidable: Reduce scope (defer Slice 4) or extend timeline with sponsor approval

---

### 6. Poor Quality Control

**Chaos Report Finding**: Projects without rigorous testing have **2.5x higher failure rate**

**Risk in PIM Auto**:
- Insufficient test coverage (<80%)
- Security vulnerabilities reach production
- Manual testing skipped due to time pressure

**Controls**:
| Control | Type | Responsibility | Frequency |
|---------|------|----------------|-----------|
| Test coverage requirement (>80% unit, >60% integration) | Preventive | QA | Per slice |
| Automated linting and type checking (ruff, mypy) | Preventive | CI/CD pipeline | Per commit |
| CodeQL security scanning | Detective | CI/CD pipeline | Per PR |
| Human code review after AI review | Detective | Tech Lead | Per PR |
| Quality gate approval (QA sign-off) | Preventive | QA | Per slice |

**Mitigation**:
- If test coverage <80%: Block slice completion, add tests
- If critical security vulnerability found: Block production deployment, fix within 24 hours
- If quality gate fails: Implement corrective actions, re-test, escalate if >2 failures

---

## Risk Register

### Active Risks (Slice 4 Execution)

| Risk ID | Description | Category | Probability | Impact | Severity | Owner | Mitigation |
|---------|-------------|----------|-------------|--------|----------|-------|------------|
| R-007 | E2E tests fail to validate production-ready behavior | Testing | Low | Medium | **Medium** | QA | Comprehensive test scenarios, realistic staging data |
| R-008 | Performance targets not met in validation testing | Performance | Low | Medium | **Medium** | Developer | Optimize queries, adjust targets with Tech Lead approval |
| R-009 | Security issues discovered late in Slice 4 review | Security | Low | High | **Medium** | Tech Lead | Continuous security scanning, early review processes |
| R-010 | UAT reveals critical usability or functionality gaps | User Acceptance | Low | High | **Medium** | Product Owner | Early UAT planning, representative user participation |
| R-011 | Documentation inaccuracies delay production approval | Documentation | Medium | Low | **Low** | Tech Lead | Parallel documentation validation, command testing |
| R-012 | Executive Sponsor delays final production approval | Governance | Low | Medium | **Low** | Prog Lead | Pre-scheduled approval meeting, clear success criteria |

### Historical Risks (Closed)

| Risk ID | Description | Status | Date Closed | Outcome |
|---------|-------------|--------|-------------|---------|
| R-001 | Azure OpenAI service quota insufficient | ✅ Closed | Slice 1 | Pre-allocated quota, no issues |
| R-002 | Log Analytics workspace lacks required audit logs | ✅ Closed | Slice 1 | Verified in dev tenant |
| R-003 | Implementation agent generates non-functional code | ✅ Closed | Slice 2 | Human review effective, quality maintained |
| R-004 | Timeline delay due to overestimated AI productivity | ✅ Closed | Slice 3 | AI productivity met expectations (42% gain) |
| R-005 | Security vulnerability in dependencies | ✅ Closed | Slice 3 | Continuous scanning, zero critical issues |
| R-006 | Scope creep from "nice-to-have" features | ✅ Closed | Slice 3 | Strict scope control maintained |

**Legend**:
- **Probability**: Low (<20%), Medium (20-50%), High (>50%)
- **Impact**: Low (minor delay), Medium (1 slice delay), High (2+ slices delay), Critical (programme failure)
- **Severity**: Low, Medium, **High**, **Critical** (product of Probability × Impact)

### Risk Monitoring

- **Weekly review**: Programme Lead updates risk register
- **New risk identification**: Any team member can raise, Programme Lead assesses
- **Risk closure**: When mitigation complete and risk no longer applicable
- **Escalation**: High/Critical risks escalated to Executive Sponsor within 24 hours

---

## Control Mechanisms

### 1. Code Quality Gates

**Automated Controls** (every PR):
```
PR Submitted
  ↓
Linting Check (ruff) → FAIL = Block merge
  ↓
Type Check (mypy) → FAIL = Block merge
  ↓
Unit Tests → FAIL = Block merge
  ↓
Test Coverage Check (>80%) → FAIL = Block merge
  ↓
Security Scan (CodeQL) → Critical/High = Block merge
  ↓
AI Code Review → Issues = Developer addresses
  ↓
Human Code Review (Tech Lead) → Approve = Merge allowed
```

**Quality Thresholds**:
- Test coverage: >80% (unit), >60% (integration)
- Linting: 0 errors (warnings allowed with Tech Lead approval)
- Type checking: 0 errors
- Security: 0 critical/high vulnerabilities

---

### 2. Phase Gate Approvals

**Human-in-the-Loop Decision Points**:

| Phase Gate | Decision Authority | Go Criteria | No-Go Actions |
|------------|-------------------|-------------|---------------|
| **Slice 0 → 1** | Tech Lead | Foundation stable, CI green, Docker builds | Fix issues, re-test, re-approve |
| **Slice 1 → 2** | Tech Lead + Product Owner | Core logic functional, tests passing (>80%), smoke test passes | Fix bugs, improve coverage, re-approve |
| **Slice 2 → 3** | Tech Lead + Product Owner | Feature complete, UX validated, integration tests pass | Address UX issues, add missing tests |
| **Slice 3 → 4** | Tech Lead + Operations | Deployment successful, monitoring active, runbook updated | Fix deployment issues, complete monitoring |
| **Slice 4 → Production** | Executive Sponsor | All success criteria met, security cleared, pilot successful | Address blockers, extend pilot, re-approve |

**Approval Workflow**:
1. Developer/Implementation Agent: PR created
2. AI tools: Automated checks pass
3. Developer: Addresses AI code review feedback
4. Tech Lead: Human code review and approval
5. QA: Quality gate validation (per slice)
6. Sponsor: Phase gate approval (major gates only)

**Rejection Criteria**:
- Critical/high security vulnerabilities unresolved
- Test coverage <80% (unit)
- Core functionality broken or untested
- Architecture misalignment (violates ADRs or Target-Architecture.md)

---

### 3. Security Controls

**Defence in Depth**:

| Layer | Control | Tool/Process | Frequency |
|-------|---------|--------------|-----------|
| **Code** | Static analysis | CodeQL | Per PR |
| **Code** | Linting (security patterns) | ruff (security rules) | Per commit |
| **Dependencies** | Vulnerability scanning | `pip audit` / GitHub Dependabot | Daily |
| **Container** | Image scanning | Docker Scout / Trivy | Per build |
| **Deployment** | Managed identity (no secrets in code) | Azure DefaultAzureCredential | Always |
| **Runtime** | Log Analytics monitoring | Azure Monitor alerts | Continuous |

**Security Incident Response**:
1. **Critical vulnerability detected**: Block all deployments, fix within 24 hours
2. **High vulnerability detected**: Fix before next slice, can proceed with Tech Lead approval
3. **Medium/Low vulnerability detected**: Track in backlog, address in next release or patch

---

### 4. Rollback Controls

**Rollback Decision Matrix**:

| Trigger | Authority | Rollback Action | Recovery Time |
|---------|-----------|-----------------|---------------|
| Critical production bug (P0) | Tech Lead | Rollback to previous slice | <1 hour |
| High security vulnerability (unpatched) | Tech Lead | Rollback to previous slice | <4 hours |
| Performance degradation (>50%) | Tech Lead + Operations | Rollback to previous slice | <2 hours |
| Deployment failure (Azure infra) | DevOps | Rollback deployment, retry | <1 hour |

**Rollback Testing**:
- Rollback procedures tested during Slice 3 (deployment)
- Rollback documentation in Runbook.md
- Rollback validated before production deployment (Slice 4)

---

## Human-in-the-Loop Decision Points

### 1. Architecture Decisions

**When**: Introducing new patterns, libraries, or Azure services not in Target-Architecture.md

**Process**:
1. Developer/Implementation Agent proposes change (via PR or ADR)
2. Tech Lead reviews against Target-Architecture.md and ADRs
3. Tech Lead approves or rejects with rationale
4. If approved: Update ADR and Target-Architecture.md

**Decision Criteria**:
- Alignment with Target-Architecture.md
- Compliance with ADRs (especially ADR-003 Azure-native, ADR-007 config management)
- Impact on testability and modularity
- Security implications

---

### 2. Scope Changes

**When**: Request to add/remove features beyond README.md specification

**Process**:
1. Requestor documents proposed change (user story, impact, rationale)
2. Programme Lead assesses impact (timeline, budget, risk)
3. Programme Lead presents to Executive Sponsor
4. Sponsor approves/rejects/defers
5. If approved: Update Migration-Plan.md, adjust timeline, communicate to team

**Decision Criteria**:
- Business value vs. implementation cost
- Impact on timeline (>20% increase = rejection unless critical)
- Risk to current delivery (high = rejection)
- Availability of resources

---

### 3. Production Deployment

**When**: Slice 4 complete, ready for production

**Process**:
1. QA validates all exit criteria met
2. Tech Lead reviews security scan (must be clean)
3. Programme Lead confirms pilot results (internal users)
4. Programme Lead presents readiness report to Executive Sponsor
5. Executive Sponsor approves/rejects/delays
6. If approved: DevOps executes production deployment
7. Operations monitors for 48 hours post-deployment

**Decision Criteria**:
- All exit criteria met (Slice 4)
- Security scan clean (0 critical/high)
- Pilot successful (0 P0 bugs, positive feedback)
- Runbook complete and tested
- Rollback plan validated
- Monitoring operational

---

## Audit and Compliance

### Audit Trail

**What**: All decisions, changes, and approvals tracked
**Where**: 
- Git commits and PR history
- ADRs for architecture decisions
- Risk register updates (weekly)
- Phase gate approvals (documented in PR comments)

**Retention**: Permanent (Git history maintained)

### Compliance Requirements

**Internal**:
- Code review on all PRs (human approval required)
- Security scanning on all PRs (CodeQL)
- Test coverage >80% on all new code

**External** (if applicable):
- Data privacy (no PII logged without consent)
- Azure compliance (use managed identity, no secrets in code)
- Open-source licensing (all dependencies reviewed)

---

## Telemetry and Monitoring

### Programme-Level Metrics (Weekly)

| Metric | Target | Current | Trend | Owner |
|--------|--------|---------|-------|-------|
| Slices completed | 1 per 3-5 days | TBD | - | Prog Lead |
| Timeline variance | <20% | TBD | - | Prog Lead |
| Budget variance | <10% | TBD | - | Prog Lead |
| Test coverage | >80% | TBD | - | QA |
| Security vulnerabilities (critical/high) | 0 | TBD | - | Tech Lead |
| AI productivity gain | >30% | TBD | - | Prog Lead |

### Risk Metrics (Weekly)

| Metric | Target | Current | Owner |
|--------|--------|---------|-------|
| Open high/critical risks | 0 | TBD | Prog Lead |
| Risk closure rate | >90% within 2 weeks | TBD | Prog Lead |
| Escalations | <2 per slice | TBD | Prog Lead |

---

## Governance Responsibilities

| Responsibility | Owner | Frequency | Artifact |
|----------------|-------|-----------|----------|
| **Update risk register** | Programme Lead | Weekly | Risk-and-Governance.md |
| **Review security scans** | Tech Lead | Per PR | CodeQL report |
| **Approve phase gates** | Tech Lead / Sponsor | Per phase | PR comment / email |
| **Track programme metrics** | Programme Lead | Weekly | Status report |
| **Conduct code reviews** | Tech Lead | Per PR | PR approval |
| **Validate quality gates** | QA | Per slice | Test reports |
| **Monitor production** | Operations | Continuous | Azure Monitor dashboards |

---

## Lessons Learned

**Post-Slice Review** (after each slice):
1. What went well?
2. What could be improved?
3. What did we learn about AI augmentation?
4. Any new risks identified?
5. Action items for next slice

**Post-Programme Review** (after production deployment):
1. Final timeline vs. baseline (actual AI productivity gain)
2. Final budget vs. baseline
3. Final quality metrics (test coverage, production bugs)
4. Risk management effectiveness (risks materialized vs. mitigated)
5. Recommendations for future AI-augmented projects

---

## Conclusion

This risk and governance framework provides:
1. **Explicit mapping** to Chaos Report failure factors with targeted mitigations
2. **Control mechanisms** at code, phase, and programme levels
3. **Human-in-the-loop** decision points for critical choices
4. **Audit trail** for all decisions and changes
5. **Clear accountability** for risk management and quality

**Risk Posture**: Risk-averse with zero tolerance for security issues
**Decision Authority**: Distributed (Tech Lead for technical, Sponsor for strategic)
**Rollback Capability**: Maintained at every phase boundary

**Next Actions**:
1. ✅ Risk register established (6 initial risks)
2. 🎯 Weekly risk review scheduled
3. 🎯 Phase gate approval process confirmed with Tech Lead and Sponsor
4. 🎯 Security scan baseline established (Slice 1)
