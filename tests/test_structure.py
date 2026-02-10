"""Test project structure and basic imports."""

import importlib.util
from pathlib import Path

import pytest


def test_project_structure_exists():
    """Verify the expected project structure exists."""
    base_dir = Path(__file__).parent.parent

    # Check main directories
    assert (base_dir / "src").exists(), "src directory should exist"
    assert (base_dir / "src" / "pim_auto").exists(), "src/pim_auto directory should exist"
    assert (base_dir / "tests").exists(), "tests directory should exist"
    assert (base_dir / "tests" / "unit").exists(), "tests/unit directory should exist"
    assert (base_dir / "tests" / "integration").exists(), "tests/integration directory should exist"
    assert (base_dir / "tests" / "e2e").exists(), "tests/e2e directory should exist"
    assert (base_dir / "tests" / "fixtures").exists(), "tests/fixtures directory should exist"

    # Check configuration files
    assert (base_dir / "pyproject.toml").exists(), "pyproject.toml should exist"
    assert (base_dir / "requirements.txt").exists(), "requirements.txt should exist"
    assert (base_dir / "requirements-dev.txt").exists(), "requirements-dev.txt should exist"


def test_pim_auto_package_exists():
    """Verify the pim_auto package can be imported."""
    spec = importlib.util.find_spec("pim_auto")
    assert spec is not None, "pim_auto package should be importable"


def test_pim_auto_has_version():
    """Verify the pim_auto package has a version attribute."""
    import pim_auto

    assert hasattr(pim_auto, "__version__"), "pim_auto should have __version__"
    assert isinstance(pim_auto.__version__, str), "__version__ should be a string"
    assert len(pim_auto.__version__) > 0, "__version__ should not be empty"


def test_documentation_exists():
    """Verify required documentation files exist."""
    base_dir = Path(__file__).parent.parent
    docs_dir = base_dir / "docs"

    assert (base_dir / "README.md").exists(), "README.md should exist"
    assert docs_dir.exists(), "docs directory should exist"
    assert (docs_dir / "Test-Strategy.md").exists(), "Test-Strategy.md should exist"
    assert (docs_dir / "HLD.md").exists(), "HLD.md should exist"
    assert (docs_dir / "LLD.md").exists(), "LLD.md should exist"


@pytest.mark.unit
def test_placeholder_passes():
    """Placeholder test to ensure test infrastructure works."""
    assert True, "Test infrastructure is working"


@pytest.mark.unit
def test_basic_python_features():
    """Test basic Python features work as expected."""
    # Test list comprehension
    result = [x * 2 for x in range(5)]
    assert result == [0, 2, 4, 6, 8]

    # Test dictionary
    data = {"key": "value"}
    assert data["key"] == "value"

    # Test string formatting
    name = "PIM Auto"
    assert f"Hello {name}" == "Hello PIM Auto"
