# Comprehensive Test Suite

## Overview

This test suite provides comprehensive coverage for all architectural advisors (AWS, Azure, GCP) and ensures tests continue running even when failures occur, with detailed failure reporting.

## Test Structure

### Test Files

- `test_advisors.py` - Comprehensive tests for AWS, Azure, and GCP architectural advisors
- `test_api.py` - API endpoint tests including advisor enhancement verification
- `test_health.py` - Health check endpoint tests
- `test_integration.py` - Integration tests
- `test_models.py` - Model validation tests
- `test_resolvers.py` - Component resolver tests

### Test Configuration

- `pytest.ini` - Pytest configuration with failure tolerance settings
- `conftest.py` - Pytest fixtures and hooks
- `run_tests.py` - Test runner with comprehensive reporting
- `test_report_generator.py` - Failure report generator

## Running Tests

### Basic Usage

```bash
# Run all tests
python -m pytest

# Run with test runner (recommended)
python run_tests.py

# Run specific test file
python -m pytest tests/test_advisors.py

# Run specific test class
python -m pytest tests/test_advisors.py::TestAWSArchitecturalAdvisor

# Run specific test
python -m pytest tests/test_advisors.py::TestAWSArchitecturalAdvisor::test_initialization
```

### Advanced Options

```bash
# Generate HTML report
python run_tests.py --html

# Generate JSON report
python run_tests.py --json

# Generate all reports
python run_tests.py --all-reports

# Run with coverage
python run_tests.py --coverage

# Verbose output
python run_tests.py --verbose

# Run specific test
python run_tests.py --test tests/test_advisors.py::TestAWSArchitecturalAdvisor
```

## Test Behavior

### Failure Tolerance

The test suite is configured to **continue running all tests** even when failures occur:

- `--maxfail=999999` - Continue running all tests regardless of failures
- `--continue-on-collection-errors` - Continue even if test collection fails
- Removed `-x` flag - No longer stops on first failure

### Reports Generated

1. **HTML Report** (`reports/report.html`)
   - Visual test results with pass/fail status
   - Clickable test names for details
   - Self-contained HTML file

2. **JUnit XML** (`reports/junit_*.xml`)
   - Standard JUnit format for CI/CD integration
   - Contains detailed failure information

3. **Failure Report** (`reports/failure_report_*.txt`)
   - Detailed text report of all failures
   - Includes error messages and tracebacks
   - Organized by failure type

4. **Failure JSON** (`reports/failure_report_*.json`)
   - Machine-readable failure data
   - Structured format for programmatic analysis

5. **Summary Report** (`reports/test_summary.txt`)
   - Quick overview of test results
   - Summary statistics
   - Environment information

## Test Coverage

### Architectural Advisors

- ✅ AWS Architectural Advisor
  - Initialization
  - Layer ordering
  - Component sorting
  - Missing component suggestions
  - Connection validation (VPC patterns, serverless patterns)
  - Spec enhancement (orthogonal routing, clustering)
  - Best practices guidance

- ✅ Azure Architectural Advisor
  - Initialization
  - Layer ordering
  - Component sorting
  - Missing component suggestions
  - Connection validation (Virtual Network patterns, serverless patterns)
  - Spec enhancement (orthogonal routing, clustering)
  - Best practices guidance

- ✅ GCP Architectural Advisor
  - Initialization
  - Layer ordering
  - Component sorting
  - Missing component suggestions
  - Connection validation (VPC patterns, serverless patterns)
  - Spec enhancement (orthogonal routing, clustering)
  - Best practices guidance

- ✅ Integration Tests
  - All advisors apply consistent layout (orthogonal routing)
  - All advisors use same spacing and direction
  - Cross-provider consistency verification

### API Tests

- ✅ Provider-specific diagram generation (AWS, Azure, GCP)
- ✅ Advisor enhancement verification (orthogonal routing applied)
- ✅ Component ordering verification
- ✅ Format regeneration
- ✅ Code execution and validation

## Viewing Reports

### HTML Report

Open `reports/report.html` in a web browser for visual test results.

### Failure Report

```bash
# View latest failure report
cat reports/failure_report_*.txt | tail -1

# Or open in editor
code reports/failure_report_*.txt
```

### Summary Report

```bash
cat reports/test_summary.txt
```

## Continuous Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    cd backend
    python tests/run_tests.py --all-reports
    
- name: Upload test reports
  uses: actions/upload-artifact@v3
  with:
    name: test-reports
    path: backend/tests/reports/
```

## Troubleshooting

### Tests Fail But Suite Continues

This is expected behavior. Check the failure reports:
- `reports/failure_report_*.txt` - Detailed failure information
- `reports/test_summary.txt` - Quick overview

### No Reports Generated

Ensure the `reports` directory exists:
```bash
mkdir -p backend/tests/reports
```

### Import Errors

Make sure you're running tests from the backend directory:
```bash
cd backend
python -m pytest tests/
```

## Best Practices

1. **Always run full test suite** before committing
2. **Review failure reports** to understand issues
3. **Fix failures incrementally** - don't ignore test failures
4. **Add new tests** when adding new features
5. **Keep tests independent** - each test should be able to run alone

## Test Markers

- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.advisor` - Advisor tests
- `@pytest.mark.critical` - Critical tests (must pass)

Run specific marker groups:
```bash
# Run only advisor tests
pytest -m advisor

# Skip slow tests
pytest -m "not slow"

# Run only critical tests
pytest -m critical
```
