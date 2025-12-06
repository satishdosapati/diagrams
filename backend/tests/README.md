# Test Suite

## Quick Start

```bash
cd backend
python -m pytest tests/ -v
```

Or use the test runner:
```bash
python tests/run_tests.py
bash tests/run_tests.sh  # On EC2
```

## Test Coverage

- **API Endpoints**: Health checks, diagram generation, modifications, code execution
- **Integration**: End-to-end workflows, multi-provider support
- **Unit Tests**: Models, resolvers, advisors
- **Health Checks**: System dependencies, Graphviz, permissions

## View Results

```bash
# HTML report
firefox tests/reports/test_report_*.html

# Summary
cat tests/reports/test_summary.txt
```
```

### Generate HTML Report

```bash
python tests/run_tests.py --html
```

### Generate All Reports

```bash
python tests/run_tests.py --all-reports
```

### Run with Coverage

```bash
python tests/run_tests.py --coverage
```

### Run Specific Test File

```bash
python tests/run_tests.py --test tests/test_api.py
```

## Test Structure

### test_api.py
Comprehensive API endpoint tests covering:
- Health endpoints (root, /health)
- Diagram generation (all formats, all providers)
- Diagram modification
- Format regeneration
- Code execution
- Code validation
- Completions endpoint
- File serving (with security tests)
- Session management
- Undo functionality

### test_integration.py
End-to-end workflow tests:
- Complete diagram workflow (generate -> modify -> regenerate)
- Multi-provider workflows
- Advanced Code Mode workflow
- Error handling workflows
- Performance tests

### test_health.py
System health and validation tests:
- Graphviz installation check
- Python version check
- Required modules check
- Output directory permissions
- Environment variables
- API health endpoints
- Component resolution for all providers

### test_models.py
Unit tests for data models:
- ArchitectureSpec creation
- Provider consistency
- Component and Connection models

### test_resolvers.py
Unit tests for component resolution:
- AWS component resolution
- Azure component resolution
- GCP component resolution

## Test Reports

Reports are generated in `backend/tests/reports/` directory:

- **HTML Report**: `test_report_YYYYMMDD_HHMMSS.html` - Visual HTML report with detailed results
- **JSON Report**: `test_report_YYYYMMDD_HHMMSS.json` - Machine-readable JSON format
- **Summary Report**: `test_summary.txt` - Text summary for quick review

## Test Categories

### Critical Tests (Must Pass)
- Health endpoints
- Basic diagram generation
- File serving security
- Session management

### Important Tests (Should Pass)
- All format generation
- All provider support
- Code execution
- Integration workflows

### Optional Tests (Nice to Have)
- Performance benchmarks
- Edge cases
- Error handling

## Running on EC2 Instance

### Prerequisites

```bash
# Install test dependencies
cd /opt/diagram-generator/backend
source venv/bin/activate
pip install pytest pytest-html pytest-json-report pytest-cov httpx
```

### Run Full Test Suite

```bash
cd /opt/diagram-generator/backend
source venv/bin/activate
python tests/run_tests.py --all-reports --verbose
```

### Check Results

```bash
# View HTML report
cd tests/reports
ls -lt test_report_*.html | head -1 | xargs -I {} firefox {} &

# View summary
cat tests/reports/test_summary.txt
```

## Interpreting Results

### Success Criteria
- ✅ All critical tests pass
- ✅ No security vulnerabilities detected
- ✅ All providers supported
- ✅ All formats working

### Common Issues

1. **Graphviz not installed**
   - Fix: `sudo yum install graphviz`

2. **Missing Python modules**
   - Fix: `pip install -r requirements.txt`

3. **Output directory not writable**
   - Fix: `chmod 755 output/` or set OUTPUT_DIR environment variable

4. **AWS credentials not configured**
   - Tests will still run but diagram generation may fail
   - Set AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

## Sharing Test Reports

To share test results for bug fixes:

1. **Generate comprehensive report:**
   ```bash
   python tests/run_tests.py --all-reports
   ```

2. **Copy report files:**
   ```bash
   tar -czf test_reports.tar.gz tests/reports/
   ```

3. **Include in bug report:**
   - HTML report (visual)
   - Summary report (quick overview)
   - Any error logs

## Continuous Integration

For CI/CD pipelines:

```bash
# Run tests and fail on any error
python tests/run_tests.py --json --verbose

# Check exit code
if [ $? -eq 0 ]; then
    echo "All tests passed"
else
    echo "Tests failed - check reports"
    exit 1
fi
```

## Adding New Tests

When adding new features, add corresponding tests:

1. **API endpoint** → Add to `test_api.py`
2. **Workflow** → Add to `test_integration.py`
3. **System check** → Add to `test_health.py`
4. **Model/Resolver** → Add to respective test files

Follow existing test patterns and naming conventions.



