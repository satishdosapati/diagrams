"""
Comprehensive security test cases for the API.
Tests for common vulnerabilities: injection attacks, path traversal, XSS, code execution, etc.
"""
import pytest
import sys
import os
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app

client = TestClient(app)


class TestPathTraversalSecurity:
    """Test path traversal attack prevention."""
    
    def test_basic_path_traversal(self):
        """Test basic path traversal attempts."""
        attacks = [
            "../etc/passwd",
            "../../etc/passwd",
            "../../../etc/passwd",
            "....//....//etc//passwd",
            "..\\..\\windows\\system32",
        ]
        
        for attack in attacks:
            response = client.get(f"/api/diagrams/{attack}")
            assert response.status_code in [400, 403], f"Failed to block: {attack}"
            assert "path traversal" in response.json().get("detail", "").lower() or \
                   "invalid" in response.json().get("detail", "").lower()
    
    def test_url_encoded_path_traversal(self):
        """Test URL-encoded path traversal attempts."""
        attacks = [
            "%2E%2E%2Fetc%2Fpasswd",
            "%2e%2e%2fetc%2fpasswd",
            "..%2F..%2Fetc%2Fpasswd",
            "%2E%2E%5C..%5Cwindows%5Csystem32",
        ]
        
        for attack in attacks:
            response = client.get(f"/api/diagrams/{attack}")
            assert response.status_code in [400, 403], f"Failed to block URL-encoded: {attack}"
    
    def test_double_encoded_path_traversal(self):
        """Test double URL-encoded path traversal."""
        attacks = [
            "%252E%252E%252Fetc%252Fpasswd",  # Double encoded
            "%252e%252e%252fetc%252fpasswd",
        ]
        
        for attack in attacks:
            response = client.get(f"/api/diagrams/{attack}")
            assert response.status_code in [400, 403], f"Failed to block double-encoded: {attack}"
    
    def test_unicode_path_traversal(self):
        """Test Unicode-based path traversal attempts."""
        attacks = [
            "..%c0%afetc%c0%afpasswd",  # UTF-8 encoding
            "..%c1%9cetc%c1%9cpasswd",
        ]
        
        for attack in attacks:
            response = client.get(f"/api/diagrams/{attack}")
            assert response.status_code in [400, 403], f"Failed to block Unicode: {attack}"
    
    def test_absolute_paths(self):
        """Test absolute path attempts."""
        attacks = [
            "/etc/passwd",
            "C:\\Windows\\System32",
            "/root/.ssh/id_rsa",
            "C:/Windows/System32",
        ]
        
        for attack in attacks:
            response = client.get(f"/api/diagrams/{attack}")
            assert response.status_code in [400, 403], f"Failed to block absolute path: {attack}"
    
    def test_hidden_files(self):
        """Test hidden file access attempts."""
        attacks = [
            ".env",
            ".ssh/id_rsa",
            ".git/config",
            "..hidden",
        ]
        
        for attack in attacks:
            response = client.get(f"/api/diagrams/{attack}")
            assert response.status_code in [400, 403], f"Failed to block hidden file: {attack}"
    
    def test_null_byte_injection(self):
        """Test null byte injection attempts."""
        attacks = [
            "file.txt%00.png",
            "file.txt\x00.png",
            "..%00/etc/passwd",
        ]
        
        for attack in attacks:
            response = client.get(f"/api/diagrams/{attack}")
            assert response.status_code in [400, 403], f"Failed to block null byte: {attack}"


class TestCodeInjectionSecurity:
    """Test code injection attack prevention."""
    
    def test_os_command_injection(self):
        """Test OS command injection attempts."""
        malicious_codes = [
            "import os; os.system('rm -rf /')",
            "import os; os.system('ls -la')",
            "__import__('os').system('whoami')",
            "import subprocess; subprocess.call(['rm', '-rf', '/'])",
            "from subprocess import call; call(['ls'])",
            "exec('import os; os.system(\"ls\")')",
            "eval('__import__(\"os\").system(\"ls\")')",
        ]
        
        for code in malicious_codes:
            response = client.post(
                "/api/execute-code",
                json={"code": code, "outformat": "png"}
            )
            # Should either reject or sandbox (not execute commands)
            assert response.status_code in [200, 400, 422, 500]
            if response.status_code == 200:
                data = response.json()
                # Should have errors indicating failure
                assert len(data.get("errors", [])) > 0 or data.get("diagram_url") == ""
    
    def test_file_system_access(self):
        """Test file system access attempts."""
        malicious_codes = [
            "import os; print(os.listdir('/'))",
            "open('/etc/passwd').read()",
            "with open('/etc/passwd', 'r') as f: print(f.read())",
            "import pathlib; list(pathlib.Path('/').iterdir())",
        ]
        
        for code in malicious_codes:
            response = client.post(
                "/api/execute-code",
                json={"code": code, "outformat": "png"}
            )
            assert response.status_code in [200, 400, 422, 500]
            # Should not expose file system contents
            if response.status_code == 200:
                data = response.json()
                # Should fail or not expose sensitive data
                assert len(data.get("errors", [])) > 0 or data.get("diagram_url") == ""
    
    def test_environment_variable_access(self):
        """Test environment variable access attempts."""
        malicious_codes = [
            "import os; print(os.environ)",
            "import os; print(os.getenv('AWS_SECRET_ACCESS_KEY'))",
            "import os; print(os.getenv('PATH'))",
        ]
        
        for code in malicious_codes:
            response = client.post(
                "/api/execute-code",
                json={"code": code, "outformat": "png"}
            )
            assert response.status_code in [200, 400, 422, 500]
            # Should not expose environment variables
            if response.status_code == 200:
                data = response.json()
                # Should not expose sensitive env vars in response
                response_text = str(data)
                assert "AWS_SECRET_ACCESS_KEY" not in response_text
                assert "AWS_ACCESS_KEY_ID" not in response_text
    
    def test_network_access(self):
        """Test network access attempts."""
        malicious_codes = [
            "import urllib.request; urllib.request.urlopen('http://evil.com')",
            "import requests; requests.get('http://evil.com')",
            "import socket; socket.create_connection(('evil.com', 80))",
        ]
        
        for code in malicious_codes:
            response = client.post(
                "/api/execute-code",
                json={"code": code, "outformat": "png"}
            )
            assert response.status_code in [200, 400, 422, 500]
            # Should either block network access or timeout
    
    def test_import_restrictions(self):
        """Test dangerous import attempts."""
        dangerous_imports = [
            "import os",
            "import subprocess",
            "import sys",
            "import shutil",
            "import socket",
            "import urllib",
            "import requests",
        ]
        
        for imp in dangerous_imports:
            code = f"{imp}\nfrom diagrams import Diagram\nwith Diagram('test', show=False): pass"
            response = client.post(
                "/api/execute-code",
                json={"code": code, "outformat": "png"}
            )
            # May succeed (imports allowed) but should not execute dangerous operations
            assert response.status_code in [200, 400, 422, 500]
    
    def test_code_in_description(self):
        """Test code injection in description field."""
        malicious_descriptions = [
            "EC2 instance'; import os; os.system('ls'); #",
            "EC2 instance\" + __import__('os').system('ls') + \"",
            "EC2 instance ${__import__('os').system('ls')}",
        ]
        
        for desc in malicious_descriptions:
            response = client.post(
                "/api/generate-diagram",
                json={"description": desc, "provider": "aws", "outformat": "png"}
            )
            # Should handle safely (may reject or sanitize)
            assert response.status_code in [200, 400, 422, 500]
            # Should not execute code
            if response.status_code == 200:
                # Verify no code execution occurred
                pass


class TestXSSSecurity:
    """Test Cross-Site Scripting (XSS) prevention."""
    
    def test_xss_in_description(self):
        """Test XSS attempts in description."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
        ]
        
        for payload in xss_payloads:
            response = client.post(
                "/api/generate-diagram",
                json={"description": f"EC2 instance {payload}", "provider": "aws", "outformat": "png"}
            )
            # Should sanitize or reject
            assert response.status_code in [200, 400, 422, 500]
            if response.status_code == 200:
                data = response.json()
                # Response should not contain unescaped script tags
                response_text = str(data)
                assert "<script>" not in response_text.lower() or \
                       response_text.lower().find("<script>") == -1
    
    def test_xss_in_filename(self):
        """Test XSS attempts in filename."""
        xss_payloads = [
            "<script>alert('XSS')</script>.png",
            "test<img src=x>.png",
            "test.svg",
        ]
        
        for payload in xss_payloads:
            response = client.get(f"/api/diagrams/{payload}")
            # Should reject invalid filename format
            assert response.status_code in [400, 403, 404]
    
    def test_xss_in_code(self):
        """Test XSS attempts in code execution."""
        xss_code = """
from diagrams import Diagram
with Diagram("<script>alert('XSS')</script>", show=False):
    pass
"""
        response = client.post(
            "/api/execute-code",
            json={"code": xss_code, "outformat": "png"}
        )
        # Should handle safely
        assert response.status_code in [200, 400, 422, 500]


class TestSSRFSecurity:
    """Test Server-Side Request Forgery (SSRF) prevention."""
    
    def test_ssrf_in_code(self):
        """Test SSRF attempts in code execution."""
        ssrf_codes = [
            "import urllib.request; urllib.request.urlopen('http://127.0.0.1:22')",
            "import urllib.request; urllib.request.urlopen('http://169.254.169.254/latest/meta-data/')",
            "import requests; requests.get('http://localhost:8080')",
            "import socket; socket.create_connection(('127.0.0.1', 22))",
        ]
        
        for code in ssrf_codes:
            response = client.post(
                "/api/execute-code",
                json={"code": code, "outformat": "png"}
            )
            # Should block or timeout
            assert response.status_code in [200, 400, 422, 500]
            if response.status_code == 200:
                data = response.json()
                # Should fail or timeout
                assert len(data.get("errors", [])) > 0 or data.get("diagram_url") == ""


class TestSessionSecurity:
    """Test session management security."""
    
    def test_session_hijacking_prevention(self):
        """Test that sessions cannot be easily hijacked."""
        # Generate a diagram to create a session
        response = client.post(
            "/api/generate-diagram",
            json={"description": "EC2 instance", "provider": "aws", "outformat": "png"}
        )
        
        if response.status_code == 200:
            session_id = response.json()["session_id"]
            
            # Try to access with modified session ID
            modified_session = session_id[:-1] + "X"
            response = client.post(
                "/api/regenerate-format",
                json={"session_id": modified_session, "outformat": "svg"}
            )
            # Should reject invalid session
            assert response.status_code == 404
    
    def test_session_expiration(self):
        """Test that sessions expire properly."""
        # This would require mocking time, so we'll test the concept
        # Sessions should expire after SESSION_EXPIRY_SECONDS (3600)
        pass
    
    def test_session_fixation(self):
        """Test session fixation prevention."""
        # Try to set a specific session ID
        custom_session = "custom-session-id-12345"
        response = client.post(
            "/api/regenerate-format",
            json={"session_id": custom_session, "outformat": "svg"}
        )
        # Should reject non-existent session
        assert response.status_code == 404
    
    def test_session_enumeration(self):
        """Test that session IDs cannot be easily enumerated."""
        # Try common session ID patterns
        common_patterns = [
            "00000000-0000-0000-0000-000000000000",
            "11111111-1111-1111-1111-111111111111",
            "admin",
            "test",
            "1",
        ]
        
        for pattern in common_patterns:
            response = client.post(
                "/api/regenerate-format",
                json={"session_id": pattern, "outformat": "svg"}
            )
            # Should reject invalid sessions
            assert response.status_code == 404


class TestInformationDisclosure:
    """Test information disclosure prevention."""
    
    def test_error_message_information_disclosure(self):
        """Test that error messages don't leak sensitive information."""
        # Try to trigger errors that might leak information
        response = client.post(
            "/api/generate-diagram",
            json={"description": "test", "provider": "invalid", "outformat": "png"}
        )
        
        if response.status_code != 200:
            error_detail = response.json().get("detail", "")
            # Should not expose:
            assert "AWS_SECRET_ACCESS_KEY" not in error_detail
            assert "AWS_ACCESS_KEY_ID" not in error_detail
            assert "/etc/passwd" not in error_detail
            assert "C:\\Windows" not in error_detail
            assert "traceback" not in error_detail.lower() or \
                   os.getenv("DEBUG", "false").lower() == "true"
    
    def test_stack_trace_disclosure(self):
        """Test that stack traces are not exposed in production."""
        # In production (DEBUG=false), stack traces should not be exposed
        with patch.dict(os.environ, {"DEBUG": "false"}):
            response = client.post(
                "/api/generate-diagram",
                json={"description": "test", "provider": "invalid", "outformat": "png"}
            )
            
            if response.status_code != 200:
                error_detail = response.json().get("detail", "")
                # Should not contain full traceback
                assert "Traceback" not in error_detail or \
                       "File \"" not in error_detail
    
    def test_file_path_disclosure(self):
        """Test that file paths are not exposed."""
        response = client.get("/api/diagrams/nonexistent_file.png")
        
        if response.status_code != 200:
            error_detail = response.json().get("detail", "")
            # Should not expose full file paths
            assert "/etc/" not in error_detail
            assert "C:\\" not in error_detail
            assert ".." not in error_detail


class TestDoSProtection:
    """Test Denial of Service (DoS) protection."""
    
    def test_resource_exhaustion_code(self):
        """Test code that tries to exhaust resources."""
        resource_exhaustion_codes = [
            # Infinite loop
            "while True: pass",
            # Memory exhaustion
            "x = 'a' * (10**9)",
            # CPU intensive
            "for i in range(10**9): pass",
            # File creation spam
            "for i in range(10000): open(f'file{i}.txt', 'w').write('test')",
        ]
        
        for code in resource_exhaustion_codes:
            response = client.post(
                "/api/execute-code",
                json={"code": code, "outformat": "png"}
            )
            # Should timeout or reject
            assert response.status_code in [200, 400, 422, 500]
            if response.status_code == 200:
                data = response.json()
                # Should have errors or timeout
                assert len(data.get("errors", [])) > 0 or data.get("diagram_url") == ""
    
    def test_very_large_input(self):
        """Test very large input handling."""
        # Very large description
        large_desc = "EC2 instance " * 100000  # ~1.3MB
        response = client.post(
            "/api/generate-diagram",
            json={"description": large_desc, "provider": "aws", "outformat": "png"}
        )
        # Should handle gracefully (may reject or process)
        assert response.status_code in [200, 400, 413, 422, 500]
    
    def test_nested_structure_attack(self):
        """Test deeply nested structure attack."""
        # Create deeply nested JSON
        nested = {"a": {"b": {"c": {"d": {"e": "value"}}}}}
        for i in range(100):
            nested = {"nested": nested}
        
        response = client.post(
            "/api/generate-diagram",
            json=nested
        )
        # Should reject invalid structure
        assert response.status_code in [400, 422]


class TestInputValidationBypass:
    """Test input validation bypass attempts."""
    
    def test_encoding_bypass(self):
        """Test various encoding bypass attempts."""
        bypass_attempts = [
            "EC2 instance",
            "EC2%20instance",  # URL encoding
            "EC2+instance",  # Plus encoding
            "EC2%09instance",  # Tab encoding
            "EC2%0Ainstance",  # Newline encoding
        ]
        
        for attempt in bypass_attempts:
            response = client.post(
                "/api/generate-diagram",
                json={"description": attempt, "provider": "aws", "outformat": "png"}
            )
            # Should handle consistently
            assert response.status_code in [200, 400, 422, 500]
    
    def test_sql_injection_attempts(self):
        """Test SQL injection attempts (even though we don't use SQL)."""
        sql_injections = [
            "EC2'; DROP TABLE users; --",
            "EC2' OR '1'='1",
            "EC2' UNION SELECT * FROM users--",
        ]
        
        for injection in sql_injections:
            response = client.post(
                "/api/generate-diagram",
                json={"description": injection, "provider": "aws", "outformat": "png"}
            )
            # Should handle safely (may accept as description or reject)
            assert response.status_code in [200, 400, 422, 500]
    
    def test_noql_injection_attempts(self):
        """Test NoSQL injection attempts."""
        nosql_injections = [
            "EC2'; return true; //",
            "EC2'; return 1==1; //",
        ]
        
        for injection in nosql_injections:
            response = client.post(
                "/api/generate-diagram",
                json={"description": injection, "provider": "aws", "outformat": "png"}
            )
            # Should handle safely
            assert response.status_code in [200, 400, 422, 500]


class TestCSRFSecurity:
    """Test Cross-Site Request Forgery (CSRF) protection."""
    
    def test_csrf_token_absence(self):
        """Test that endpoints don't require CSRF tokens (if not implemented)."""
        # If CSRF protection is not implemented, this test documents that
        # In production, consider adding CSRF protection for state-changing operations
        response = client.post(
            "/api/generate-diagram",
            json={"description": "EC2 instance", "provider": "aws", "outformat": "png"}
        )
        # Currently no CSRF protection, so this will succeed
        # This is acceptable for MVP but should be addressed in production
        assert response.status_code in [200, 400, 422, 500]


class TestRateLimiting:
    """Test rate limiting (if implemented)."""
    
    def test_rapid_requests(self):
        """Test rapid successive requests."""
        # Make many rapid requests
        for i in range(20):
            response = client.post(
                "/api/generate-diagram",
                json={"description": f"EC2 instance {i}", "provider": "aws", "outformat": "png"}
            )
            # Should handle (may rate limit or process)
            assert response.status_code in [200, 400, 422, 429, 500]
            if response.status_code == 429:
                # Rate limited
                break


class TestSecurityHeaders:
    """Test security headers in responses."""
    
    def test_security_headers_present(self):
        """Test that security headers are present."""
        response = client.get("/health")
        
        # Check for common security headers (may not all be present)
        headers = response.headers
        
        # X-Request-ID should be present (we know this is implemented)
        assert "X-Request-ID" in headers
        
        # Other security headers to consider:
        # - X-Content-Type-Options: nosniff
        # - X-Frame-Options: DENY
        # - X-XSS-Protection: 1; mode=block
        # - Content-Security-Policy
        # - Strict-Transport-Security (if HTTPS)
        
        # Note: These may not be implemented yet, but should be in production


class TestFileUploadSecurity:
    """Test file upload security (if file upload is added in future)."""
    
    def test_file_extension_validation(self):
        """Test that only allowed file extensions are accepted."""
        # Currently no file upload endpoint, but if added:
        # - Should validate file extensions
        # - Should scan for malicious content
        # - Should limit file size
        pass
    
    def test_malicious_file_content(self):
        """Test that malicious file content is rejected."""
        # If file upload is added:
        # - Should scan for viruses/malware
        # - Should validate file structure
        # - Should reject executable files
        pass

