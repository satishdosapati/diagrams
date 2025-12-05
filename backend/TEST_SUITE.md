# Comprehensive Test Suite

## Quick Start

### On EC2 Instance

```bash
cd /opt/diagram-generator/backend
bash run_test_suite.sh
```

This will:
1. Activate virtual environment
2. Install test dependencies
3. Run all tests
4. Generate HTML, JSON, and summary reports

### View Results

```bash
# View summary
cat tests/reports/test_summary.txt

# View HTML report (if browser available)
firefox tests/reports/test_report_*.html

# List all reports
ls -lh tests/reports/
```

## Test Coverage

### ✅ API Endpoints (test_api.py)
- Health endpoints (`/`, `/health`)
- Diagram generation (`POST /api/generate-diagram`)
  - All formats: PNG, SVG, PDF, DOT
  - All providers: AWS, Azure, GCP
  - With direction and Graphviz attributes
- Diagram modification (`POST /api/modify-diagram`)
- Format regeneration (`POST /api/regenerate-format`)
- Code execution (`POST /api/execute-code`)
- Code validation (`POST /api/validate-code`)
- Completions (`GET /api/completions/{provider}`)
- File serving (`GET /api/diagrams/{filename}`)
  - Security: Path traversal protection
- Session management
- Undo functionality

### ✅ Integration Tests (test_integration.py)
- Complete workflows (generate → modify → regenerate)
- Multi-provider workflows
- Advanced Code Mode workflow
- Error handling
- Performance tests

### ✅ Health Checks (test_health.py)
- Graphviz installation
- Python version compatibility
- Required modules availability
- Output directory permissions
- Environment variables
- Component resolution (AWS, Azure, GCP)

### ✅ Unit Tests
- Models (`test_models.py`)
- Resolvers (`test_resolvers.py`)

## Report Formats

### HTML Report
Visual report with:
- Test results summary
- Passed/failed/skipped counts
- Detailed test output
- Error messages and stack traces

**Location:** `tests/reports/test_report_YYYYMMDD_HHMMSS.html`

### JSON Report
Machine-readable format for:
- CI/CD integration
- Automated analysis
- Programmatic processing

**Location:** `tests/reports/test_report_YYYYMMDD_HHMMSS.json`

### Summary Report
Text summary with:
- Test statistics
- Failed tests list
- Environment information
- Quick overview

**Location:** `tests/reports/test_summary.txt`

## Expected Results

A successful test run should show:

```
Total Tests: ~50+
Passed: ~45+
Failed: 0-5 (depending on environment)
Skipped: 0-5
```

### Critical Tests (Must Pass)
- ✅ Health endpoints responding
- ✅ Basic diagram generation
- ✅ File serving security
- ✅ Session management

### Important Tests (Should Pass)
- ✅ All format generation
- ✅ All provider support
- ✅ Code execution
- ✅ Integration workflows

## Troubleshooting

### Graphviz Not Found
```bash
sudo yum install graphviz
```

### Missing Python Modules
```bash
pip install -r requirements.txt
pip install pytest pytest-html pytest-json-report pytest-cov httpx
```

### Permission Errors
```bash
chmod 755 output/
# Or set OUTPUT_DIR
export OUTPUT_DIR=/opt/diagram-generator/output
```

### AWS Credentials
Tests will run but diagram generation may fail without AWS credentials:
```bash
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
```

## Sharing Test Results

To share test results for bug fixes:

1. **Generate comprehensive reports:**
   ```bash
   python tests/run_tests.py --all-reports
   ```

2. **Copy report files:**
   ```bash
   cd tests/reports
   tar -czf test_reports.tar.gz *.html *.json *.txt
   ```

3. **Include in bug report:**
   - HTML report (visual overview)
   - Summary report (quick reference)
   - Any specific error messages

## Test Execution Options

```bash
# Run all tests with all reports
python tests/run_tests.py --all-reports

# Run with HTML report only
python tests/run_tests.py --html

# Run with verbose output
python tests/run_tests.py --verbose

# Run with coverage
python tests/run_tests.py --coverage

# Run specific test file
python tests/run_tests.py --test tests/test_api.py

# Run specific test
python tests/run_tests.py --test tests/test_api.py::TestHealthEndpoints::test_root_endpoint
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Run tests and exit with error code on failure
python tests/run_tests.py --json --verbose

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ All tests passed"
else
    echo "❌ Tests failed - check reports"
    exit 1
fi
```

## Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py              # Pytest configuration
├── pytest.ini              # Pytest settings
├── run_tests.py            # Test runner script
├── run_tests.sh            # Shell script for EC2
├── README.md               # Detailed documentation
├── QUICK_TEST.md           # Quick reference
├── test_api.py             # API endpoint tests
├── test_integration.py     # Integration tests
├── test_health.py          # Health checks
├── test_models.py          # Model unit tests
├── test_resolvers.py       # Resolver unit tests
└── reports/                # Generated reports
    ├── test_report_*.html
    ├── test_report_*.json
    └── test_summary.txt
```

## Adding New Tests

When adding features, add corresponding tests:

1. **New API endpoint** → Add to `test_api.py`
2. **New workflow** → Add to `test_integration.py`
3. **New system check** → Add to `test_health.py`
4. **New model/resolver** → Add to respective test files

Follow existing patterns:
- Use descriptive test names
- Include docstrings
- Test both success and failure cases
- Test edge cases and error conditions



