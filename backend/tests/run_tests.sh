#!/bin/bash
# Comprehensive test suite runner for Linux/EC2

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

echo "=================================================================================="
echo "Architecture Diagram Generator - Comprehensive Test Suite"
echo "=================================================================================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: Virtual environment not activated"
    echo "Activating virtual environment..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "Error: Virtual environment not found. Please create it first:"
        echo "  python3 -m venv venv"
        echo "  source venv/bin/activate"
        echo "  pip install -r requirements.txt"
        exit 1
    fi
fi

# Install test dependencies if needed
echo "Checking test dependencies..."
pip install -q pytest pytest-html pytest-json-report pytest-cov httpx || {
    echo "Error: Failed to install test dependencies"
    exit 1
}

# Create reports directory
mkdir -p tests/reports

# Run tests with all reports
echo ""
echo "Running test suite..."
echo ""

python tests/run_tests.py --all-reports --verbose

# Check exit code
TEST_EXIT_CODE=$?

echo ""
echo "=================================================================================="
echo "Test Suite Completed"
echo "=================================================================================="
echo ""

# Display report locations
if [ -d "tests/reports" ]; then
    echo "Report files generated:"
    ls -lh tests/reports/*.html tests/reports/*.json tests/reports/*.txt 2>/dev/null | tail -5
    echo ""
    echo "View HTML report:"
    echo "  firefox tests/reports/test_report_*.html"
    echo ""
    echo "View summary:"
    echo "  cat tests/reports/test_summary.txt"
fi

exit $TEST_EXIT_CODE




















