# Test Suite Instructions

## Test Suite Status

✅ **Comprehensive and Up-to-Date**

The test suite covers:
- ✅ All API endpoints (9/9 endpoints tested, including error-logs)
- ✅ Health checks and system validation
- ✅ Integration workflows
- ✅ Unit tests for models, resolvers, and advisors
- ✅ Multiple output formats (PNG, SVG, PDF, DOT)
- ✅ Format normalization (invalid formats like GIF normalized to PNG)
- ✅ All cloud providers (AWS, Azure, GCP)
- ✅ Code execution and validation
- ✅ Session management with generation_id persistence
- ✅ Feedback endpoints with generation_id tracking
- ✅ File serving with security tests
- ✅ Regenerate-format with generation_id preservation
- ✅ Format normalization in regenerate-format

**Recent Updates:**
- ✅ Added tests for generation_id persistence across regenerations
- ✅ Added tests for format normalization in regenerate-format
- ✅ Fixed normalize_format test (removed invalid None test)
- ✅ Removed orphaned code from routes.py

## Quick Start

### Prerequisites

1. **Activate virtual environment:**
   ```bash
   cd backend
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   # Windows CMD
   venv\Scripts\activate.bat
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

### Running Tests

#### Option 1: Simple pytest (Recommended for Quick Runs)

```bash
cd backend
pytest tests/ -v
```

#### Option 2: Using Test Runner Script (Recommended for Full Reports)

**Windows PowerShell:**
```powershell
cd backend
python tests\run_tests.py --all-reports --verbose
```

**Windows CMD:**
```cmd
cd backend
python tests\run_tests.py --all-reports --verbose
```

**Linux/Mac:**
```bash
cd backend
python tests/run_tests.py --all-reports --verbose
```

#### Option 3: Using Shell Scripts (Linux/Mac/EC2)

```bash
cd backend
bash tests/run_tests.sh
# OR
bash run_test_suite.sh
```

### Test Runner Options

```bash
# Generate HTML report
python tests/run_tests.py --html

# Generate JSON report
python tests/run_tests.py --json

# Run with code coverage
python tests/run_tests.py --coverage

# Run specific test file
python tests/run_tests.py --test tests/test_api.py

# Run all reports (HTML + JSON + Summary)
python tests/run_tests.py --all-reports

# Verbose output
python tests/run_tests.py --verbose
```

## Test Reports

After running tests, reports are generated in `backend/tests/reports/`:

- **HTML Report**: `test_report_YYYYMMDD_HHMMSS.html` - Visual HTML report
- **JSON Report**: `test_report_YYYYMMDD_HHMMSS.json` - Machine-readable format
- **Summary Report**: `test_summary.txt` - Quick text summary
- **JUnit XML**: `junit_YYYYMMDD_HHMMSS.xml` - CI/CD integration format

### Viewing Reports

**Windows:**
```powershell
# View HTML report (opens in default browser)
Start-Process tests\reports\test_report_*.html

# View summary
Get-Content tests\reports\test_summary.txt
```

**Linux/Mac:**
```bash
# View HTML report
firefox tests/reports/test_report_*.html

# View summary
cat tests/reports/test_summary.txt
```

## Running Specific Tests

### Run Single Test File

```bash
pytest tests/test_api.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_api.py::TestHealthEndpoints -v
```

### Run Specific Test Function

```bash
pytest tests/test_api.py::TestHealthEndpoints::test_root_endpoint -v
```

### Run Tests by Marker

```bash
# Run only critical tests
pytest -m critical -v

# Run only API tests
pytest -m api -v

# Run all except slow tests
pytest -m "not slow" -v

# Run integration tests
pytest -m integration -v
```

## Test Structure

### Test Files

- **test_api.py** - API endpoint tests (comprehensive)
- **test_integration.py** - End-to-end workflow tests
- **test_health.py** - System health and validation tests
- **test_models.py** - Data model unit tests
- **test_resolvers.py** - Component resolver tests
- **test_advisors.py** - Architectural advisor tests
- **test_report_generator.py** - Test report generation tests

### Test Categories

- **Critical** (`@pytest.mark.critical`) - Must pass tests
- **API** (`@pytest.mark.api`) - API endpoint tests
- **Integration** (`@pytest.mark.integration`) - End-to-end tests
- **Health** (`@pytest.mark.health`) - Health check tests
- **Advisor** (`@pytest.mark.advisor`) - Advisor tests
- **Slow** (`@pytest.mark.slow`) - Long-running tests

## Environment Setup

### Test Environment Variables

Tests use these default environment variables (set in `conftest.py`):

```python
OUTPUT_DIR = "./test_output"  # Test output directory
DEBUG = "false"                # Debug mode
```

### Override Environment Variables

```bash
# Windows PowerShell
$env:OUTPUT_DIR="custom_test_output"; pytest tests/ -v

# Windows CMD
set OUTPUT_DIR=custom_test_output && pytest tests/ -v

# Linux/Mac
OUTPUT_DIR=custom_test_output pytest tests/ -v
```

## Common Issues

### Issue: ModuleNotFoundError

**Solution:**
```bash
cd backend
source venv/bin/activate  # or activate on Windows
pip install -r requirements.txt
```

### Issue: Graphviz not found

**Solution:**
- **Windows**: Install Graphviz from https://graphviz.org/download/
- **Linux**: `sudo yum install graphviz` or `sudo apt-get install graphviz`
- **Mac**: `brew install graphviz`

### Issue: Tests fail due to AWS credentials

**Note:** Tests should work without AWS credentials for most endpoints. Diagram generation tests may fail if AWS credentials are not configured, but other tests should pass.

**Solution:** Set AWS credentials (optional):
```bash
# Windows PowerShell
$env:AWS_REGION="us-east-1"
$env:AWS_ACCESS_KEY_ID="your-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret"

# Linux/Mac
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

### Issue: Permission errors on test output directory

**Solution:**
```bash
# Windows PowerShell (run as Administrator if needed)
New-Item -ItemType Directory -Force -Path backend\test_output

# Linux/Mac
mkdir -p backend/test_output
chmod 755 backend/test_output
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run tests
  run: |
    cd backend
    source venv/bin/activate
    python tests/run_tests.py --json --verbose
```

### Exit Codes

- `0` - All tests passed
- `1` - Tests failed or errors occurred

## Adding New Tests

When adding new features:

1. **API endpoint** → Add to `test_api.py`
2. **Workflow** → Add to `test_integration.py`
3. **System check** → Add to `test_health.py`
4. **Model/Resolver** → Add to respective test files

Follow existing test patterns and naming conventions.

## Test Coverage

To generate coverage report:

```bash
python tests/run_tests.py --coverage
```

Coverage report will be in:
- Terminal output (summary)
- HTML report: `htmlcov/index.html`

## Performance Testing

Some tests include performance benchmarks. Run with:

```bash
pytest tests/test_integration.py::TestEndToEndWorkflows -v
```

## Troubleshooting

### View Test Output

```bash
# Very verbose output
pytest tests/ -vv -s

# Show print statements
pytest tests/ -s
```

### Debug Failed Tests

```bash
# Run with pdb debugger
pytest tests/ --pdb

# Run specific failed test with pdb
pytest tests/test_api.py::TestHealthEndpoints::test_root_endpoint --pdb
```

### Check Test Collection

```bash
# List all tests without running
pytest tests/ --collect-only
```

