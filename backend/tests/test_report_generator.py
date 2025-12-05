"""
Test report generator that collects failures and generates comprehensive reports.
"""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class TestReportGenerator:
    """Generates comprehensive test failure reports."""
    
    def __init__(self, reports_dir: Path):
        """Initialize with reports directory."""
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(exist_ok=True)
    
    def parse_junit_xml(self, xml_file: Path) -> Dict:
        """Parse JUnit XML report."""
        failures = []
        errors = []
        skipped = []
        passed = []
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Handle both testsuites and testsuite root elements
            if root.tag == "testsuites":
                testsuites = root.findall("testsuite")
            else:
                testsuites = [root]
            
            for testsuite in testsuites:
                for testcase in testsuite.findall("testcase"):
                    test_name = f"{testcase.get('classname')}::{testcase.get('name')}"
                    duration = float(testcase.get("time", 0))
                    
                    # Check for failures
                    failure = testcase.find("failure")
                    if failure is not None:
                        failures.append({
                            "name": test_name,
                            "message": failure.get("message", ""),
                            "type": failure.get("type", ""),
                            "traceback": failure.text or "",
                            "duration": duration
                        })
                        continue
                    
                    # Check for errors
                    error = testcase.find("error")
                    if error is not None:
                        errors.append({
                            "name": test_name,
                            "message": error.get("message", ""),
                            "type": error.get("type", ""),
                            "traceback": error.text or "",
                            "duration": duration
                        })
                        continue
                    
                    # Check for skipped
                    skipped_elem = testcase.find("skipped")
                    if skipped_elem is not None:
                        skipped.append({
                            "name": test_name,
                            "reason": skipped_elem.get("message", ""),
                            "duration": duration
                        })
                        continue
                    
                    # Passed test
                    passed.append({
                        "name": test_name,
                        "duration": duration
                    })
            
            return {
                "failures": failures,
                "errors": errors,
                "skipped": skipped,
                "passed": passed,
                "total": len(failures) + len(errors) + len(skipped) + len(passed),
                "failed_count": len(failures) + len(errors),
                "passed_count": len(passed),
                "skipped_count": len(skipped)
            }
        except Exception as e:
            return {
                "error": f"Failed to parse JUnit XML: {str(e)}",
                "failures": [],
                "errors": [],
                "skipped": [],
                "passed": [],
                "total": 0,
                "failed_count": 0,
                "passed_count": 0,
                "skipped_count": 0
            }
    
    def generate_failure_report(self, xml_file: Optional[Path] = None) -> Path:
        """Generate comprehensive failure report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f"failure_report_{timestamp}.txt"
        
        # Find latest JUnit XML if not provided
        if xml_file is None:
            xml_files = list(self.reports_dir.glob("junit_*.xml"))
            if xml_files:
                xml_file = max(xml_files, key=lambda p: p.stat().st_mtime)
            else:
                xml_file = None
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("=" * 100 + "\n")
            f.write("TEST FAILURE REPORT\n")
            f.write("=" * 100 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n")
            
            if xml_file and xml_file.exists():
                data = self.parse_junit_xml(xml_file)
                
                # Summary
                f.write("SUMMARY\n")
                f.write("-" * 100 + "\n")
                f.write(f"Total Tests: {data.get('total', 0)}\n")
                f.write(f"Passed: {data.get('passed_count', 0)}\n")
                f.write(f"Failed: {data.get('failed_count', 0)}\n")
                f.write(f"Skipped: {data.get('skipped_count', 0)}\n")
                f.write("\n")
                
                # Failures
                failures = data.get("failures", [])
                if failures:
                    f.write("FAILURES\n")
                    f.write("-" * 100 + "\n")
                    for i, failure in enumerate(failures, 1):
                        f.write(f"\n{i}. {failure['name']}\n")
                        f.write(f"   Duration: {failure.get('duration', 0):.3f}s\n")
                        if failure.get('message'):
                            f.write(f"   Message: {failure['message']}\n")
                        if failure.get('type'):
                            f.write(f"   Type: {failure['type']}\n")
                        if failure.get('traceback'):
                            # Limit traceback length
                            traceback = failure['traceback']
                            if len(traceback) > 500:
                                traceback = traceback[:500] + "\n... (truncated)"
                            f.write(f"   Traceback:\n{traceback}\n")
                        f.write("\n")
                
                # Errors
                errors = data.get("errors", [])
                if errors:
                    f.write("ERRORS\n")
                    f.write("-" * 100 + "\n")
                    for i, error in enumerate(errors, 1):
                        f.write(f"\n{i}. {error['name']}\n")
                        f.write(f"   Duration: {error.get('duration', 0):.3f}s\n")
                        if error.get('message'):
                            f.write(f"   Message: {error['message']}\n")
                        if error.get('type'):
                            f.write(f"   Type: {error['type']}\n")
                        if error.get('traceback'):
                            traceback = error['traceback']
                            if len(traceback) > 500:
                                traceback = traceback[:500] + "\n... (truncated)"
                            f.write(f"   Traceback:\n{traceback}\n")
                        f.write("\n")
                
                # Skipped tests
                skipped = data.get("skipped", [])
                if skipped:
                    f.write("SKIPPED TESTS\n")
                    f.write("-" * 100 + "\n")
                    for i, skip in enumerate(skipped, 1):
                        f.write(f"{i}. {skip['name']}\n")
                        if skip.get('reason'):
                            f.write(f"   Reason: {skip['reason']}\n")
                    f.write("\n")
                
                # Passed tests summary (if failures exist)
                if failures or errors:
                    passed = data.get("passed", [])
                    if passed:
                        f.write(f"PASSED TESTS\n")
                        f.write("-" * 100 + "\n")
                        for test in passed[:20]:  # Show first 20
                            f.write(f"  ✓ {test['name']}\n")
                        if len(passed) > 20:
                            f.write(f"  ... and {len(passed) - 20} more\n")
                        f.write("\n")
            else:
                f.write("No JUnit XML report found. Run tests with --junit-xml option.\n")
            
            f.write("=" * 100 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 100 + "\n")
        
        return report_file
    
    def generate_json_report(self, xml_file: Optional[Path] = None) -> Path:
        """Generate JSON failure report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = self.reports_dir / f"failure_report_{timestamp}.json"
        
        # Find latest JUnit XML if not provided
        if xml_file is None:
            xml_files = list(self.reports_dir.glob("junit_*.xml"))
            if xml_files:
                xml_file = max(xml_files, key=lambda p: p.stat().st_mtime)
            else:
                xml_file = None
        
        if xml_file and xml_file.exists():
            data = self.parse_junit_xml(xml_file)
            data["generated_at"] = datetime.now().isoformat()
            data["xml_source"] = str(xml_file)
        else:
            data = {
                "error": "No JUnit XML report found",
                "generated_at": datetime.now().isoformat()
            }
        
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        return json_file


def generate_failure_reports(reports_dir: Path):
    """Generate all failure reports."""
    generator = TestReportGenerator(reports_dir)
    
    txt_report = generator.generate_failure_report()
    json_report = generator.generate_json_report()
    
    return txt_report, json_report
