# Test Strategy - PIM Auto

**Document Status**: Baseline  
**Last Updated**: 2026-02-10  
**Repository**: jometzg/pim-auto  
**Purpose**: Define testing approach to protect current behavior and enable confident modernization

## Executive Summary

This test strategy establishes a safety net for the PIM Auto application modernization. Given the current state (specification-only, no implementation), this strategy defines:

1. **Test pyramid approach** for future implementation
2. **Critical flows** that must be covered
3. **Baseline test infrastructure** to support incremental development
4. **Known gaps** and limitations

The strategy follows the strangler pattern from `/docs/Migration-Plan.md`, ensuring each implementation slice is independently testable.

## Current State

**Status**: Pre-implementation (Slice 0)

**What Exists**:
- ✅ Specification (`/README.md`)
- ✅ Documentation (`/docs/HLD.md`, `/docs/LLD.md`)
- ✅ Migration plan (`/docs/Migration-Plan.md`)

**What Does Not Exist**:
- ❌ Python source code
- ❌ Test infrastructure
- ❌ CI/CD pipeline

## Test Pyramid Approach

We follow a standard test pyramid with emphasis on integration tests given the Azure-dependent nature of the application.

```
         /\
        /  \      E2E Tests (10%)
       /____\     - Full workflow validation
      /      \    - Manual/exploratory testing
     /        \   
    /__________\  Integration Tests (30%)
   /            \ - Azure service mocking
  /              \- API/service level tests
 /________________\
/                  \ Unit Tests (60%)
|                  | - Pure logic
|                  | - Domain behaviors
|__________________|
```

### Unit Tests (60% of test coverage)

**Scope**: Pure logic without external dependencies

**Target Components** (future implementation):
- KQL query generation logic
- Activity correlation algorithms
- Risk assessment logic
- Date/time range calculations
- Report formatting functions
- Input validation

**Characteristics**:
- Fast execution (< 100ms per test)
- No external dependencies
- Deterministic results
- High code coverage (>80% for core logic)

**Technology**: pytest with unittest.mock

### Integration Tests (30% of test coverage)

**Scope**: Component interactions and Azure service integration

**Target Components** (future implementation):
- Azure OpenAI integration
- Log Analytics query execution
- Authentication flow (DefaultAzureCredential)
- Chat interface state management
- Batch mode orchestration

**Characteristics**:
- Mock Azure services (using responses/pytest-mock)
- Test realistic data flows
- Validate error handling
- Moderate execution time (< 5s per test)

**Technology**: pytest with mocked Azure SDK calls

### End-to-End Tests (10% of test coverage)

**Scope**: Full user workflows from entry to output

**Target Scenarios** (future implementation):
- Interactive chat: scan → query → alignment check
- Batch mode: automated scan with report generation
- Error recovery scenarios

**Characteristics**:
- May require Azure sandbox environment
- Slower execution (> 5s per test)
- Focus on happy paths and critical failure modes
- Manual validation component

**Technology**: pytest with optional Azure sandbox

## Critical Flows

These flows **must** be covered by automated tests before production deployment:

### 1. PIM Activation Detection (Priority: Critical)

**Description**: Scan Azure Log Analytics for privilege elevations

**Test Coverage Required**:
- ✅ Query AuditLogs table for PIM activations
- ✅ Extract user identities correctly
- ✅ Parse activation timestamps
- ✅ Extract activation reasons
- ✅ Handle empty results gracefully
- ✅ Handle malformed log entries

**Test Type**: Integration (mocked Azure Log Analytics)

**Acceptance Criteria**: 
- Tests pass with representative AuditLogs sample data
- Error cases handled without crashes

### 2. AI Query Generation (Priority: Critical)

**Description**: Generate KQL queries using Azure OpenAI

**Test Coverage Required**:
- ✅ Generate valid KQL syntax from natural language
- ✅ Handle query generation failures
- ✅ Self-correction on failed queries
- ✅ Context awareness in multi-turn conversations
- ✅ Rate limiting and retry logic

**Test Type**: Integration (mocked Azure OpenAI)

**Acceptance Criteria**:
- Generated queries are syntactically valid KQL
- Self-correction reduces error rate
- Rate limits are respected

### 3. Activity Correlation (Priority: Critical)

**Description**: Track Azure resource changes during elevation periods

**Test Coverage Required**:
- ✅ Query AzureActivity table for user actions
- ✅ Filter by time range correctly
- ✅ Aggregate activities into timeline
- ✅ Handle concurrent users
- ✅ Handle missing or incomplete activity logs

**Test Type**: Integration (mocked Azure Log Analytics)

**Acceptance Criteria**:
- Activity timeline matches log entries
- Time range filtering is accurate
- No data loss or corruption

### 4. Risk Assessment (Priority: High)

**Description**: Evaluate activity alignment with stated reasons

**Test Coverage Required**:
- ✅ Compare stated reason with actual activities
- ✅ Generate alignment assessment (full/partial/no alignment)
- ✅ Provide reasoning for assessment
- ✅ Handle edge cases (no activities, no reason given)

**Test Type**: Unit + Integration

**Acceptance Criteria**:
- Alignment assessments are consistent
- Reasoning is understandable
- Edge cases don't crash

### 5. Interactive Chat Mode (Priority: High)

**Description**: Natural language interface with context awareness

**Test Coverage Required**:
- ✅ Parse user commands correctly
- ✅ Maintain conversation context across turns
- ✅ Display formatted results
- ✅ Handle 'scan', 'query', 'exit' commands
- ✅ Graceful error messages

**Test Type**: Integration + E2E

**Acceptance Criteria**:
- All commands work as specified in README
- Context is preserved across conversation
- User experience is smooth

### 6. Batch Mode (Priority: High)

**Description**: Automated scanning with report generation

**Test Coverage Required**:
- ✅ Scan last 24 hours without user interaction
- ✅ Process multiple elevated users
- ✅ Generate Markdown report
- ✅ Handle no-activations scenario
- ✅ Complete within reasonable time (< 5 minutes)

**Test Type**: Integration + E2E

**Acceptance Criteria**:
- Batch mode runs unattended
- Report format matches specification
- Performance is acceptable

### 7. Authentication (Priority: Critical)

**Description**: Secure Azure authentication using DefaultAzureCredential

**Test Coverage Required**:
- ✅ Managed identity authentication (production)
- ✅ Azure CLI authentication (local dev)
- ✅ Credential chain fallback
- ✅ Handle authentication failures
- ✅ Token refresh

**Test Type**: Integration (may require real Azure)

**Acceptance Criteria**:
- Both auth methods work
- Failures are handled gracefully
- Security best practices followed

### 8. Health Endpoint (Priority: Medium)

**Description**: Basic health check for deployment validation

**Test Coverage Required**:
- ✅ Returns 200 OK when healthy
- ✅ Returns non-200 when dependencies unavailable
- ✅ Includes dependency status in response

**Test Type**: Integration

**Acceptance Criteria**:
- Health check is fast (< 1s)
- Accurately reflects system state

## Known Gaps and Limitations

### Baseline Phase (Current)

1. **No Production Code**: Tests will be skeleton/placeholder until implementation exists
2. **No Azure Integration**: Cannot test real Azure services until credentials configured
3. **AI Non-Determinism**: OpenAI responses are non-deterministic, requiring special test approaches
4. **Performance Testing**: Not included in baseline, to be added in Slice 3
5. **Security Testing**: CodeQL will be used, but manual security review needed
6. **Load Testing**: Multi-user scenarios not covered in baseline

### Future Phases

1. **E2E Azure Tests**: Require Azure sandbox environment (cost implications)
2. **Production Monitoring**: Test strategy doesn't cover operational metrics
3. **Disaster Recovery**: DR procedures not covered by automated tests
4. **Compliance Validation**: PIM audit requirements need manual validation

## Test Infrastructure

### Testing Framework

**Primary**: pytest 7.4+

**Rationale**:
- Industry standard for Python
- Rich plugin ecosystem
- Excellent mocking support
- Fixtures for setup/teardown
- Parameterized tests
- Clear output

### Mocking Strategy

**Azure SDK Mocking**:
- Use `unittest.mock` for Azure SDK calls
- Create fixtures for common responses
- Maintain realistic sample data

**OpenAI Mocking**:
- Mock chat completion responses
- Simulate token limits
- Test retry logic

**Log Analytics Mocking**:
- Mock KQL query responses
- Use real AuditLogs/AzureActivity schema
- Test with edge cases (empty, malformed, large datasets)

### Test Data Management

**Approach**: Fixture-based with version control

**Location**: `/tests/fixtures/`

**Files**:
- `audit_logs_sample.json`: Representative PIM activation logs
- `activity_logs_sample.json`: Representative Azure activity logs
- `openai_responses.json`: Sample AI responses
- `kql_queries.json`: Valid and invalid KQL examples

**Principles**:
- Use real Azure log schema
- Anonymize any real data
- Cover happy path and edge cases
- Keep files small and focused

### CI/CD Integration

**GitHub Actions Workflow**: `/.github/workflows/ci.yml`

**Triggers**:
- Pull request to main branch
- Push to main branch
- Manual workflow dispatch

**Steps**:
1. Checkout code
2. Set up Python 3.11
3. Install dependencies (`pip install -r requirements-dev.txt`)
4. Run linters (ruff, black)
5. Run tests with coverage (`pytest --cov`)
6. Upload coverage report
7. Build Docker image (smoke test)

**Quality Gates**:
- All tests must pass
- Coverage must be ≥ 80%
- No linting errors
- Docker build must succeed

## Test Execution

### Local Development

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_pim_detection.py

# Run specific test
pytest tests/test_pim_detection.py::test_scan_activations

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### CI Environment

Tests run automatically on every pull request via GitHub Actions.

**View Results**:
- Check the "Actions" tab in GitHub
- Review test output in workflow logs
- Download coverage reports from artifacts

**Troubleshooting**:
- Ensure all dependencies in requirements-dev.txt
- Check Python version (3.11+)
- Verify test fixtures are committed

## Test Maintenance

### Adding New Tests

1. **Identify the behavior** to test (from specification or ticket)
2. **Choose test type** (unit, integration, E2E)
3. **Write test following conventions**:
   - Name: `test_<behavior>_<scenario>`
   - Arrange-Act-Assert pattern
   - Single assertion per test (prefer)
   - Descriptive failure messages
4. **Add to appropriate test file**:
   - Unit tests: `tests/unit/test_<module>.py`
   - Integration tests: `tests/integration/test_<component>.py`
   - E2E tests: `tests/e2e/test_<workflow>.py`
5. **Update fixtures if needed**
6. **Run tests locally** before committing
7. **Document any new test data** requirements

### Updating Existing Tests

1. **Understand why test needs change** (behavior change vs. test fix)
2. **Update test to match new behavior**
3. **Ensure test still follows conventions**
4. **Check for other tests** affected by same change
5. **Run full test suite** to catch regressions
6. **Update documentation** if test strategy changes

### Deprecating Tests

1. **Mark test with `@pytest.mark.skip`** with reason
2. **Create ticket** to remove or replace test
3. **Document in PR** why test is being deprecated
4. **Remove after safe period** (1-2 sprints)

## Appendix A: Testing Conventions

### Naming

- Test files: `test_<module_under_test>.py`
- Test functions: `test_<behavior>_<scenario>`
- Test classes: `Test<ModuleName>`
- Fixtures: descriptive noun (e.g., `mock_openai_client`, `sample_audit_log`)

### Organization

```
tests/
├── unit/
│   ├── test_kql_generator.py
│   ├── test_risk_assessor.py
│   └── test_report_formatter.py
├── integration/
│   ├── test_azure_openai.py
│   ├── test_log_analytics.py
│   └── test_auth.py
├── e2e/
│   ├── test_chat_workflow.py
│   └── test_batch_workflow.py
├── fixtures/
│   ├── audit_logs_sample.json
│   ├── activity_logs_sample.json
│   └── openai_responses.json
└── conftest.py  # Shared fixtures
```

### Patterns

**Arrange-Act-Assert**:
```python
def test_scan_finds_elevated_users():
    # Arrange
    mock_client = create_mock_log_analytics()
    scanner = PIMScanner(mock_client)
    
    # Act
    results = scanner.scan(hours=24)
    
    # Assert
    assert len(results) == 2
    assert results[0].user == "john.doe@contoso.com"
```

**Parameterized Tests**:
```python
@pytest.mark.parametrize("hours,expected_count", [
    (24, 2),
    (48, 5),
    (0, 0),
])
def test_scan_with_different_time_ranges(hours, expected_count):
    # Test implementation
    pass
```

**Fixtures**:
```python
@pytest.fixture
def sample_audit_log():
    return {
        "user": "john.doe@contoso.com",
        "timestamp": "2026-02-05T10:00:00Z",
        "reason": "need to add a storage account"
    }
```

## Appendix B: Test Coverage Targets

| Component | Target Coverage | Priority |
|-----------|----------------|----------|
| KQL Generation | 90% | Critical |
| PIM Detection | 85% | Critical |
| Activity Correlation | 85% | Critical |
| Risk Assessment | 80% | High |
| Report Generation | 75% | High |
| Chat Interface | 70% | High |
| Batch Mode | 80% | High |
| Authentication | 85% | Critical |
| Error Handling | 80% | High |

**Overall Target**: ≥ 80% code coverage

## Appendix C: Slice-by-Slice Test Plan

### Slice 0: Foundation (Current)

**Focus**: Test infrastructure setup

**Deliverables**:
- [x] Test-Strategy.md (this document)
- [ ] pytest configuration
- [ ] Basic project structure validation test
- [ ] CI workflow with test execution
- [ ] Documentation: how to run tests

**Acceptance**: CI workflow runs successfully (even with minimal tests)

### Slice 1: Core Implementation

**Focus**: Core logic with comprehensive tests

**Deliverables**:
- Unit tests for PIM detection
- Unit tests for activity correlation
- Integration tests for Azure SDK (mocked)
- Fixtures for sample data

**Acceptance**: >80% coverage of implemented code

### Slice 2: Dual Mode Support

**Focus**: Chat and batch mode workflows

**Deliverables**:
- Integration tests for chat interface
- E2E test for batch mode
- State management tests

**Acceptance**: Both modes testable end-to-end

### Slice 3: Production Readiness

**Focus**: Deployment and operational testing

**Deliverables**:
- Health endpoint tests
- Container startup tests
- Performance baseline tests
- Security scan (CodeQL)

**Acceptance**: Deployment to test environment succeeds

### Slice 4: Validation

**Focus**: Final validation and documentation

**Deliverables**:
- E2E test in Azure sandbox
- Test report and coverage analysis
- Test maintenance documentation

**Acceptance**: All critical flows covered and passing

## References

- `/README.md`: Application specification
- `/docs/HLD.md`: High-level design
- `/docs/LLD.md`: Low-level design
- `/docs/Migration-Plan.md`: Phased implementation plan
- `/.github/skills/test-synthesis.skill.md`: Testing guidelines
