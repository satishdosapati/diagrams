# Quick Test Guide

## On EC2 Instance

### Step 1: Install Test Dependencies

```bash
cd /opt/diagram-generator/backend
source venv/bin/activate
pip install pytest pytest-html pytest-json-report pytest-cov httpx
```

### Step 2: Run Tests

```bash
# Option 1: Use the test runner script
bash tests/run_tests.sh

# Option 2: Use Python directly
python tests/run_tests.py --all-reports

# Option 3: Use pytest directly
pytest tests/ -v --html=tests/reports/report.html --self-contained-html
```

### Step 3: View Results

```bash
# View HTML report (if you have a browser)
firefox tests/reports/test_report_*.html

# View summary
cat tests/reports/test_summary.txt

# List all reports
ls -lh tests/reports/
```

## Test Coverage

The test suite covers:

✅ **API Endpoints** (test_api.py)
- Health checks
- Diagram generation (all formats, all providers)
- Diagram modification
- Format regeneration
- Code execution
- Code validation
- Completions
- File serving (with security tests)

✅ **Integration Tests** (test_integration.py)
- End-to-end workflows
- Multi-provider support
- Advanced Code Mode
- Error handling
- Performance

✅ **Health Checks** (test_health.py)
- System dependencies
- Graphviz installation
- Python modules
- Directory permissions
- Component resolution

✅ **Unit Tests** (test_models.py, test_resolvers.py)
- Data models
- Component resolution

## Expected Results

A successful test run should show:
- All critical tests passing
- All providers working (AWS, Azure, GCP)
- All formats working (PNG, SVG, PDF, DOT)
- No security vulnerabilities
- System health checks passing

## Troubleshooting

### Graphviz not found
```bash
sudo yum install graphviz
```

### Missing Python modules
```bash
pip install -r requirements.txt
```

### Permission errors
```bash
chmod 755 output/
# Or set OUTPUT_DIR environment variable
export OUTPUT_DIR=/opt/diagram-generator/output
```

### AWS credentials
Tests will run but diagram generation may fail without AWS credentials:
```bash
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
```

## Sharing Results

To share test results:

1. Generate reports:
   ```bash
   python tests/run_tests.py --all-reports
   ```

2. Copy reports:
   ```bash
   tar -czf test_reports.tar.gz tests/reports/
   ```

3. Include in bug report:
   - HTML report (visual)
   - Summary report (text)
   - Any error messages

