#!/usr/bin/env python3
"""
Comprehensive test suite runner with detailed reporting.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --html             # Generate HTML report
    python run_tests.py --json             # Generate JSON report
    python run_tests.py --verbose          # Verbose output
    python run_tests.py --coverage         # Run with coverage
"""
import sys
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import argparse


def run_tests(html_report=False, json_report=False, verbose=False, coverage=False, specific_test=None):
    """Run pytest with specified options."""
    test_dir = Path(__file__).parent
    reports_dir = test_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    # Add verbose flag
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add HTML report
    if html_report:
        html_file = reports_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        cmd.extend(["--html", str(html_file), "--self-contained-html"])
        print(f"HTML report will be saved to: {html_file}")
    
    # Add JSON report (using pytest's built-in JSON output)
    if json_report:
        json_file = reports_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        # Use pytest's built-in JSON output
        cmd.extend(["--json-report", "--json-report-file", str(json_file)])
        # Fallback: use pytest-json-report if available, otherwise create manual JSON
        print(f"JSON report will be saved to: {json_file}")
    
    # Add specific test if provided
    if specific_test:
        cmd.append(specific_test)
    else:
        cmd.append(str(test_dir))
    
    # Add additional options
    cmd.extend([
        # Remove -x flag to continue on failures
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker checking
        "-ra",  # Show extra test summary info
        "--maxfail=999999",  # Continue running all tests even on failures
        "--continue-on-collection-errors",  # Continue even if collection fails
        "--junit-xml", str(reports_dir / f"junit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"),  # JUnit XML report
    ])
    
    print("=" * 80)
    print("Running Comprehensive Test Suite")
    print("=" * 80)
    print(f"Command: {' '.join(cmd)}")
    print("=" * 80)
    print()
    
    # Run tests
    result = subprocess.run(cmd, cwd=test_dir.parent)
    
    return result.returncode == 0, reports_dir


def generate_summary_report(reports_dir):
    """Generate a summary report from test results."""
    summary_file = reports_dir / "test_summary.txt"
    
    # Try to parse JUnit XML first (more reliable)
    xml_files = list(reports_dir.glob("junit_*.xml"))
    json_reports = list(reports_dir.glob("test_report_*.json"))
    
    with open(summary_file, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("TEST SUITE SUMMARY REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n")
        
        # Parse JUnit XML if available
        if xml_files:
            latest_xml = max(xml_files, key=lambda p: p.stat().st_mtime)
            try:
                from test_report_generator import TestReportGenerator
                generator = TestReportGenerator(reports_dir)
                data = generator.parse_junit_xml(latest_xml)
                
                # Summary statistics
                f.write("SUMMARY STATISTICS\n")
                f.write("-" * 80 + "\n")
                f.write(f"Total Tests: {data.get('total', 0)}\n")
                f.write(f"Passed: {data.get('passed_count', 0)}\n")
                f.write(f"Failed: {data.get('failed_count', 0)}\n")
                f.write(f"Skipped: {data.get('skipped_count', 0)}\n")
                f.write("\n")
                
                # Failed tests summary
                failures = data.get("failures", [])
                errors = data.get("errors", [])
                if failures or errors:
                    f.write("FAILED TESTS SUMMARY\n")
                    f.write("-" * 80 + "\n")
                    for failure in failures + errors:
                        f.write(f"  - {failure['name']}\n")
                    f.write(f"\nSee failure_report_*.txt for detailed error messages.\n\n")
            except Exception as e:
                f.write(f"Note: Could not parse JUnit XML: {e}\n\n")
        
        # Fallback to JSON if available
        elif json_reports:
            latest_json = max(json_reports, key=lambda p: p.stat().st_mtime)
            try:
                with open(latest_json) as json_f:
                    data = json.load(json_f)
                    
                # Summary statistics
                summary = data.get("summary", {})
                f.write("SUMMARY STATISTICS\n")
                f.write("-" * 80 + "\n")
                f.write(f"Total Tests: {summary.get('total', 0)}\n")
                f.write(f"Passed: {summary.get('passed', 0)}\n")
                f.write(f"Failed: {summary.get('failed', 0)}\n")
                f.write(f"Skipped: {summary.get('skipped', 0)}\n")
                f.write(f"Errors: {summary.get('error', 0)}\n")
                f.write("\n")
                
                # Failed tests
                if summary.get('failed', 0) > 0:
                    f.write("FAILED TESTS\n")
                    f.write("-" * 80 + "\n")
                    for test in data.get("tests", []):
                        if test.get("outcome") == "failed":
                            f.write(f"  - {test.get('nodeid', 'unknown')}\n")
                            error_msg = test.get('call', {}).get('longrepr', 'No error message')
                            if isinstance(error_msg, str):
                                f.write(f"    Error: {error_msg[:300]}\n")
                            f.write("\n")
                    f.write("\n")
            except Exception as e:
                f.write(f"Note: Could not parse JSON report: {e}\n\n")
        
        # Environment info
        f.write("ENVIRONMENT INFORMATION\n")
        f.write("-" * 80 + "\n")
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Platform: {sys.platform}\n")
        f.write(f"Working Directory: {os.getcwd()}\n")
        f.write(f"Output Directory: {os.getenv('OUTPUT_DIR', './output')}\n")
        f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")
    
    print(f"\nSummary report saved to: {summary_file}")
    return summary_file


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run comprehensive test suite")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Generate JSON report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("--test", "-t", help="Run specific test file or test")
    parser.add_argument("--all-reports", action="store_true", help="Generate all report types")
    
    args = parser.parse_args()
    
    # If all-reports, enable all
    if args.all_reports:
        args.html = True
        args.json = True
    
    # At least generate JSON for summary
    if not args.json and not args.html:
        args.json = True
    
    success, reports_dir = run_tests(
        html_report=args.html,
        json_report=args.json,
        verbose=args.verbose,
        coverage=args.coverage,
        specific_test=args.test
    )
    
    # Generate summary from pytest output
    generate_summary_report(reports_dir)
    
    # Generate detailed failure reports
    try:
        from test_report_generator import generate_failure_reports
        txt_report, json_report = generate_failure_reports(reports_dir)
        print(f"\nDetailed failure report: {txt_report}")
        print(f"Failure JSON report: {json_report}")
    except ImportError:
        print("\nNote: Detailed failure report generator not available")
    except Exception as e:
        print(f"\nNote: Could not generate detailed failure report: {e}")
    
    # Print report locations
    print("\n" + "=" * 80)
    print("REPORT FILES")
    print("=" * 80)
    html_reports = list(reports_dir.glob("test_report_*.html")) + list(reports_dir.glob("report.html"))
    json_reports = list(reports_dir.glob("test_report_*.json")) + list(reports_dir.glob("failure_report_*.json"))
    summary_reports = list(reports_dir.glob("test_summary.txt"))
    failure_reports = list(reports_dir.glob("failure_report_*.txt"))
    junit_reports = list(reports_dir.glob("junit_*.xml"))
    
    if html_reports:
        print(f"HTML Report: {max(html_reports, key=lambda p: p.stat().st_mtime)}")
    if json_reports:
        print(f"JSON Report: {max(json_reports, key=lambda p: p.stat().st_mtime)}")
    if summary_reports:
        print(f"Summary Report: {max(summary_reports, key=lambda p: p.stat().st_mtime)}")
    if failure_reports:
        print(f"Failure Report: {max(failure_reports, key=lambda p: p.stat().st_mtime)}")
    if junit_reports:
        print(f"JUnit XML: {max(junit_reports, key=lambda p: p.stat().st_mtime)}")
    print("=" * 80)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

