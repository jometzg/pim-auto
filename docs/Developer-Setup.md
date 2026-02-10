# Developer Setup Guide

## Prerequisites

- Python 3.11 or higher
- Docker Desktop
- Azure CLI (for Azure authentication)
- Git

## Initial Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jometzg/pim-auto.git
   cd pim-auto
   ```

2. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Verify installation:
   ```bash
   pytest
   black --check src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src/pim_auto

# Specific test file
pytest tests/unit/test_config.py

# Verbose output
pytest -v
```

## Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check formatting (CI mode)
black --check src/ tests/
isort --check-only src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/
```

## Building Container

```bash
# Build image
docker build -t pim-auto:local .

# Run container
docker run --rm pim-auto:local

# Interactive shell
docker run --rm -it pim-auto:local /bin/bash
```

## Azure Authentication (Local Development)

```bash
# Login to Azure
az login

# Set default subscription (if you have multiple)
az account set --subscription "Your Subscription Name"

# Verify authentication
az account show
```

## Troubleshooting

### Virtual Environment Issues

If you see "command not found" errors, ensure your virtual environment is activated:
```bash
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Dependency Conflicts

Clear and reinstall dependencies:
```bash
pip install --upgrade pip
pip install --force-reinstall -r requirements.txt
pip install --force-reinstall -r requirements-dev.txt
```

### Docker Build Failures

Clear Docker cache and rebuild:
```bash
docker builder prune -a
docker build --no-cache -t pim-auto:local .
```
