#!/bin/bash
# Quick test suite runner for EC2 instances

cd "$(dirname "$0")"

echo "=================================================================================="
echo "Architecture Diagram Generator - Test Suite"
echo "=================================================================================="
echo ""

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install test dependencies
echo "Installing test dependencies..."
pip install -q pytest pytest-html pytest-json-report pytest-cov httpx 2>/dev/null || {
    echo "Installing test dependencies..."
    pip install pytest pytest-html pytest-json-report pytest-cov httpx
}

# Run tests
echo ""
echo "Running comprehensive test suite..."
echo ""

python tests/run_tests.py --all-reports --verbose

echo ""
echo "=================================================================================="
echo "Test Suite Complete"
echo "=================================================================================="
echo ""
echo "Reports generated in: tests/reports/"
echo ""
echo "To view summary:"
echo "  cat tests/reports/test_summary.txt"
echo ""
echo "To view HTML report (if browser available):"
echo "  firefox tests/reports/test_report_*.html"
echo ""














