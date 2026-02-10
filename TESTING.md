# Testing Guide - PIM Auto

This guide explains how to run tests for the PIM Auto application.

## Quick Start

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src/pim_auto --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Organization

Tests are organized by type:

- `tests/unit/` - Fast, isolated unit tests for pure logic
- `tests/integration/` - Tests that mock Azure services
- `tests/e2e/` - End-to-end workflow tests
- `tests/fixtures/` - Shared test data

## Running Specific Tests

```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run a specific test file
pytest tests/unit/test_pim_detection.py

# Run a specific test function
pytest tests/unit/test_pim_detection.py::test_pim_detection_placeholder

# Run tests matching a pattern
pytest -k "detection"

# Run tests with specific marker
pytest -m unit
```

## Test Markers

Use markers to filter tests:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow running tests

Example:
```bash
# Run only unit tests
pytest -m unit

# Run everything except slow tests
pytest -m "not slow"
```

## Verbose Output

```bash
# Show detailed test output
pytest -v

# Show print statements
pytest -s

# Both verbose and prints
pytest -v -s
```

## Coverage

```bash
# Run with coverage
pytest --cov=src/pim_auto

# Generate HTML report
pytest --cov=src/pim_auto --cov-report=html

# Generate XML report (for CI)
pytest --cov=src/pim_auto --cov-report=xml

# Show missing lines
pytest --cov=src/pim_auto --cov-report=term-missing
```

## Debugging Failed Tests

```bash
# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l

# Increase verbosity
pytest -vv
```

## Linting and Formatting

```bash
# Run ruff linter
ruff check src/ tests/

# Auto-fix issues with ruff
ruff check --fix src/ tests/

# Check code formatting with black
black --check src/ tests/

# Auto-format code with black
black src/ tests/

# Run type checker
mypy src/
```

## Continuous Integration

Tests run automatically on:
- Pull requests to main branch
- Pushes to main branch
- Manual workflow dispatch

View CI results in the GitHub Actions tab.

### CI Quality Gates

All of these must pass:
- ✅ All tests pass
- ✅ Code coverage ≥ 80%
- ✅ No linting errors
- ✅ Code is formatted correctly
- ✅ Project structure is valid

## Test Development Guidelines

### Writing Good Tests

1. **Name tests descriptively**: `test_scan_finds_elevated_users`
2. **Use Arrange-Act-Assert pattern**:
   ```python
   def test_example():
       # Arrange: Set up test data
       data = {"key": "value"}
       
       # Act: Call the function
       result = process(data)
       
       # Assert: Verify the result
       assert result == expected
   ```
3. **One assertion per test** (preferred, not strict)
4. **Use fixtures for shared setup**
5. **Keep tests independent** - no test should depend on another

### Using Fixtures

Common fixtures are defined in `tests/conftest.py`:

```python
def test_example(sample_audit_log):
    # sample_audit_log is automatically provided
    assert sample_audit_log["user"] == "john.doe@contoso.com"
```

### Parameterized Tests

For testing multiple scenarios:

```python
@pytest.mark.parametrize("input,expected", [
    (24, "ago(24h)"),
    (48, "ago(48h)"),
    (1, "ago(1h)"),
])
def test_time_formatting(input, expected):
    result = format_time(input)
    assert result == expected
```

## Current State

**Note**: The repository is currently in the baseline/foundation phase. Most tests are placeholders that verify:
- Project structure is correct
- Dependencies can be imported
- Test infrastructure works

As implementation progresses (Slices 1-4), these placeholder tests will be replaced with real tests that verify actual business logic.

## Troubleshooting

### Import errors

If you see import errors:
```bash
# Make sure you're in the project root
cd /path/to/pim-auto

# Install in development mode
pip install -e .
```

### Missing dependencies

```bash
# Reinstall all dependencies
pip install -r requirements-dev.txt
```

### Tests not found

Make sure:
- Test files are named `test_*.py`
- Test functions are named `test_*`
- You're running pytest from the project root

### Coverage not working

```bash
# Make sure pytest-cov is installed
pip install pytest-cov

# Verify coverage config in pyproject.toml
cat pyproject.toml | grep -A 10 "\[tool.coverage"
```

## Next Steps

1. **Slice 1**: Add real implementation and corresponding tests
2. **Slice 2**: Add integration tests with mocked Azure services
3. **Slice 3**: Add end-to-end tests
4. **Slice 4**: Performance and validation testing

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Test Strategy Document](../docs/Test-Strategy.md)
- [Migration Plan](../docs/Migration-Plan.md)
