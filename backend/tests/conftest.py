"""
Pytest configuration and fixtures.
"""
import pytest
import os
import shutil
from pathlib import Path

# Set test environment variables
os.environ.setdefault("OUTPUT_DIR", "./test_output")
os.environ.setdefault("DEBUG", "false")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment before all tests."""
    # Create test output directory
    test_output_dir = Path(os.getenv("OUTPUT_DIR", "./test_output"))
    test_output_dir.mkdir(exist_ok=True)
    
    yield
    
    # Cleanup after all tests
    # Optionally remove test output directory
    # if test_output_dir.exists():
    #     shutil.rmtree(test_output_dir)


@pytest.fixture(autouse=True)
def cleanup_between_tests():
    """Cleanup between tests if needed."""
    yield
    # Add any per-test cleanup here



