# ADR-001: Agent-Based Development Governance Model

**Status**: Implemented  
**Date**: 2026-02-10  
**Decision Makers**: Repository Owner (implicit)

## Context

Software development projects require governance to ensure quality, consistency, and alignment with objectives. Traditional approaches use manual code reviews, documentation mandates, and team coordination processes.

## Decision

The pim-auto repository implements an **agent-based governance model** using GitHub automation and AI-powered agents to manage different phases of development.

### Implementation Details

Five specialized agent configurations are defined in `/.github/agents/`:

1. **Documentation Agent** (`documentation.agent.md`):
   - Generates HLD, LLD, ADRs, and Runbooks
   - Uses `system-discovery.skill.md` procedure
   - Enforces: "No code changes, documentation only"

2. **Testing Agent** (`testing.agent.md`):
   - Creates baseline test strategy
   - Establishes automated tests
   - Uses `test-synthesis.skill.md` procedure

3. **Modernisation Agent** (`modernisation.agent.md`):
   - Proposes target architecture
   - Plans incremental migration
   - Uses `architecture-reasoning.skill.md` and `incremental-refactoring.skill.md`

4. **Implementation Agent** (`implementation.agent.md`):
   - Executes approved migration slices
   - Delivers with tests and documentation
   - Uses `incremental-refactoring.skill.md`

5. **Intelligent Migration Agent** (`intelligent-migration.agent.md`):
   - Designs end-to-end migration program
   - Governs phased roadmap and risk controls
   - Uses `intelligent-application-migration.skill.md`

### Supporting Skills

Five skill files in `/.github/skills/` provide detailed operating procedures for these agents.

## Rationale

### Advantages

1. **Separation of Concerns**: Each agent has a specific, well-defined responsibility
2. **Automated Quality Gates**: Agents enforce documentation, testing, and architecture standards
3. **Consistency**: Skill files provide repeatable procedures across development phases
4. **Explicit Governance**: Development process is encoded rather than tribal knowledge
5. **AI Augmentation**: Agents can be AI-powered for scalable, consistent execution

### Trade-offs

1. **Setup Complexity**: Requires initial investment in agent and skill configuration
2. **Learning Curve**: Team must understand agent model and skill procedures
3. **Tool Dependency**: Relies on GitHub infrastructure and agent execution framework
4. **Rigidity Risk**: May slow down if agents are too prescriptive

## Consequences

### Positive

- Clear separation between documentation, testing, architecture, and implementation work
- Automated enforcement of development standards
- Human review still mandatory (all agents must deliver via PR)
- Scalable approach as project grows

### Negative

- Additional complexity in project structure
- Requires maintenance of agent configurations and skills
- May be overkill for simple projects

### Neutral

- Development process becomes more formalized
- Changes existing workflows for contributors

## Alternative Considered

**Traditional manual governance**: Standard code review process with documentation templates and testing guidelines.

**Rejected because**: Manual processes don't scale, are inconsistently applied, and create bottlenecks. Agent-based approach provides automation while maintaining human oversight through PR reviews.

## Compliance

- All agents must deliver output via pull requests
- Human review is mandatory before merge (stated in documentation agent instructions)
- No agent can bypass the PR + review workflow

## References

- `/.github/agents/*.agent.md`: Five agent configurations
- `/.github/skills/*.skill.md`: Five skill procedures
- Documentation agent instructions: "All output must be delivered via a pull request"
