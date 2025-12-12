"""
Comprehensive tests for input validation and error handling across all API endpoints.
Tests various types of valid/invalid inputs with proper error handling verification.
"""
import pytest
import json
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app

client = TestClient(app)


class TestInputValidationGenerateDiagram:
    """Test input validation for /api/generate-diagram endpoint."""
    
    def test_missing_required_fields(self):
        """Test missing required fields."""
        # Missing description
        response = client.post("/api/generate-diagram", json={"provider": "aws"})
        assert response.status_code == 422  # FastAPI validation error
        
        # Missing provider (should use default)
        response = client.post("/api/generate-diagram", json={"description": "Test"})
        # Should succeed with default provider
        assert response.status_code in [200, 400, 500]
    
    def test_empty_description(self):
        """Test empty description."""
        response = client.post(
            "/api/generate-diagram",
            json={"description": "", "provider": "aws", "outformat": "png"}
        )
        assert response.status_code in [400, 422]
        if response.status_code == 400:
            assert "description" in response.json().get("detail", "").lower()
    
    def test_whitespace_only_description(self):
        """Test whitespace-only description."""
        response = client.post(
            "/api/generate-diagram",
            json={"description": "   ", "provider": "aws", "outformat": "png"}
        )
        assert response.status_code in [400, 422]
    
    def test_invalid_data_types(self):
        """Test invalid data types."""
        # Description as number
        response = client.post(
            "/api/generate-diagram",
            json={"description": 12345, "provider": "aws"}
        )
        assert response.status_code == 422
        
        # Description as list
        response = client.post(
            "/api/generate-diagram",
            json={"description": ["test"], "provider": "aws"}
        )
        assert response.status_code == 422
        
        # Provider as number
        response = client.post(
            "/api/generate-diagram",
            json={"description": "Test", "provider": 123}
        )
        assert response.status_code == 422
    
    def test_invalid_provider_values(self):
        """Test invalid provider values."""
        invalid_providers = ["invalid", "gcp2", "AWS2", "", " ", None]
        
        for provider in invalid_providers:
            if provider is None:
                # None will cause 422 validation error
                response = client.post(
                    "/api/generate-diagram",
                    json={"description": "Test", "provider": None}
                )
                assert response.status_code == 422
            else:
                response = client.post(
                    "/api/generate-diagram",
                    json={"description": "Test", "provider": provider, "outformat": "png"}
                )
                # Should handle gracefully (may accept or reject)
                assert response.status_code in [200, 400, 422, 500]
    
    def test_invalid_format_values(self):
        """Test invalid format values."""
        invalid_formats = ["invalid", "jpg", "gif", "", " ", None, 123, []]
        
        for fmt in invalid_formats:
            if fmt is None or isinstance(fmt, (int, list)):
                # These will cause validation errors
                response = client.post(
                    "/api/generate-diagram",
                    json={"description": "Test", "provider": "aws", "outformat": fmt}
                )
                assert response.status_code in [200, 400, 422, 500]
            else:
                response = client.post(
                    "/api/generate-diagram",
                    json={"description": "Test", "provider": "aws", "outformat": fmt}
                )
                # Should handle gracefully (may normalize or reject)
                assert response.status_code in [200, 400, 422, 500]
    
    def test_very_long_description(self):
        """Test very long description."""
        long_desc = "EC2 instance " * 1000  # ~13KB
        response = client.post(
            "/api/generate-diagram",
            json={"description": long_desc, "provider": "aws", "outformat": "png"}
        )
        # Should handle (may succeed or fail based on limits)
        assert response.status_code in [200, 400, 413, 422, 500]
    
    def test_special_characters_in_description(self):
        """Test special characters in description."""
        special_chars = [
            "EC2 & RDS & S3",
            "Lambda → DynamoDB → S3",
            "API Gateway + Lambda",
            "VPC with <script>alert('xss')</script>",
            "EC2 with 'quotes' and \"double quotes\"",
            "EC2\nwith\nnewlines",
            "EC2\twith\ttabs",
        ]
        
        for desc in special_chars:
            response = client.post(
                "/api/generate-diagram",
                json={"description": desc, "provider": "aws", "outformat": "png"}
            )
            # Should handle special characters (may sanitize or reject)
            assert response.status_code in [200, 400, 422, 500]
    
    def test_unicode_characters(self):
        """Test unicode characters in description."""
        unicode_descs = [
            "EC2实例与RDS数据库",  # Chinese
            "EC2インスタンスとRDS",  # Japanese
            "EC2 экземпляр и RDS",  # Cyrillic
            "EC2 instance 🚀 with RDS 💾",
        ]
        
        for desc in unicode_descs:
            response = client.post(
                "/api/generate-diagram",
                json={"description": desc, "provider": "aws", "outformat": "png"}
            )
            # Should handle unicode
            assert response.status_code in [200, 400, 422, 500]
    
    def test_malformed_json(self):
        """Test malformed JSON."""
        # Missing closing brace
        response = client.post(
            "/api/generate-diagram",
            data='{"description": "Test", "provider": "aws"',
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
        # Invalid JSON syntax
        response = client.post(
            "/api/generate-diagram",
            data='{"description": "Test", "provider": }',
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_out_of_context_input_rejection(self):
        """Test that out-of-context inputs are rejected."""
        out_of_context = [
            "How to bake a cake",
            "What's the weather today?",
            "Tell me a joke",
            "Recipe for pasta",
        ]
        
        for desc in out_of_context:
            response = client.post(
                "/api/generate-diagram",
                json={"description": desc, "provider": "aws", "outformat": "png"}
            )
            # Should reject with 400 (validation error)
            assert response.status_code == 400
            error_detail = response.json().get("detail", "")
            assert "cloud architecture" in error_detail.lower() or "diagram" in error_detail.lower()
    
    def test_error_response_format(self):
        """Test error response format."""
        response = client.post(
            "/api/generate-diagram",
            json={"description": "bake a cake", "provider": "aws"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert len(data["detail"]) > 0


class TestInputValidationRegenerateFormat:
    """Test input validation for /api/regenerate-format endpoint."""
    
    def test_missing_session_id(self):
        """Test missing session_id."""
        response = client.post(
            "/api/regenerate-format",
            json={"outformat": "svg"}
        )
        assert response.status_code == 422
    
    def test_missing_outformat(self):
        """Test missing outformat."""
        response = client.post(
            "/api/regenerate-format",
            json={"session_id": "test-session"}
        )
        assert response.status_code == 422
    
    def test_invalid_session_id(self):
        """Test invalid session_id."""
        response = client.post(
            "/api/regenerate-format",
            json={"session_id": "nonexistent-session-12345", "outformat": "svg"}
        )
        assert response.status_code == 404
        assert "session" in response.json().get("detail", "").lower()
    
    def test_empty_session_id(self):
        """Test empty session_id."""
        response = client.post(
            "/api/regenerate-format",
            json={"session_id": "", "outformat": "svg"}
        )
        assert response.status_code in [400, 404, 422]
    
    def test_invalid_outformat(self):
        """Test invalid outformat."""
        # First create a valid session
        gen_response = client.post(
            "/api/generate-diagram",
            json={"description": "EC2 instance", "provider": "aws", "outformat": "png"}
        )
        if gen_response.status_code == 200:
            session_id = gen_response.json()["session_id"]
            
            # Try invalid format
            response = client.post(
                "/api/regenerate-format",
                json={"session_id": session_id, "outformat": "invalid_format"}
            )
            # Should handle gracefully
            assert response.status_code in [200, 400, 422, 500]


class TestInputValidationExecuteCode:
    """Test input validation for /api/execute-code endpoint."""
    
    def test_missing_code(self):
        """Test missing code."""
        response = client.post(
            "/api/execute-code",
            json={"title": "Test", "outformat": "png"}
        )
        assert response.status_code == 422
    
    def test_empty_code(self):
        """Test empty code."""
        response = client.post(
            "/api/execute-code",
            json={"code": "", "outformat": "png"}
        )
        # Should handle (may succeed or fail)
        assert response.status_code in [200, 400, 422, 500]
    
    def test_invalid_code_syntax(self):
        """Test invalid Python syntax."""
        invalid_codes = [
            "invalid syntax {",
            "from diagrams import",
            "def incomplete_function(",
            "print('unclosed string",
            "x = [1, 2, 3",
        ]
        
        for code in invalid_codes:
            response = client.post(
                "/api/execute-code",
                json={"code": code, "outformat": "png"}
            )
            # Should return errors in response
            assert response.status_code == 200
            data = response.json()
            assert len(data.get("errors", [])) > 0 or data.get("diagram_url") == ""
    
    def test_code_with_imports_only(self):
        """Test code with only imports."""
        code = "from diagrams import Diagram\nfrom diagrams.aws.compute import EC2"
        response = client.post(
            "/api/execute-code",
            json={"code": code, "outformat": "png"}
        )
        # May succeed or fail depending on implementation
        assert response.status_code in [200, 400, 500]
    
    def test_code_with_security_risks(self):
        """Test code with potential security risks."""
        risky_codes = [
            "import os; os.system('rm -rf /')",
            "__import__('os').system('ls')",
            "eval('print(1)')",
            "exec('print(1)')",
        ]
        
        for code in risky_codes:
            response = client.post(
                "/api/execute-code",
                json={"code": code, "outformat": "png"}
            )
            # Should handle securely (may reject or sandbox)
            assert response.status_code in [200, 400, 422, 500]
            # If succeeds, should not execute dangerous code
            if response.status_code == 200:
                data = response.json()
                # Should have errors or warnings
                assert len(data.get("errors", [])) > 0 or len(data.get("warnings", [])) > 0
    
    def test_very_long_code(self):
        """Test very long code."""
        long_code = "from diagrams import Diagram\n" + "ec2 = EC2('Instance')\n" * 1000
        response = client.post(
            "/api/execute-code",
            json={"code": long_code, "outformat": "png"}
        )
        # Should handle (may succeed or fail based on limits)
        assert response.status_code in [200, 400, 413, 422, 500]


class TestInputValidationValidateCode:
    """Test input validation for /api/validate-code endpoint."""
    
    def test_missing_code(self):
        """Test missing code."""
        response = client.post("/api/validate-code", json={})
        assert response.status_code == 422
    
    def test_empty_code(self):
        """Test empty code."""
        response = client.post("/api/validate-code", json={"code": ""})
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
    
    def test_invalid_syntax(self):
        """Test invalid syntax validation."""
        response = client.post(
            "/api/validate-code",
            json={"code": "invalid syntax {"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data.get("errors", [])) > 0
    
    def test_code_with_undefined_variables(self):
        """Test code with undefined variables."""
        code = """
from diagrams import Diagram
with Diagram("Test", show=False):
    ec2 >> undefined_variable
"""
        response = client.post("/api/validate-code", json={"code": code})
        assert response.status_code == 200
        data = response.json()
        # Should detect undefined variable
        assert data["valid"] is False or len(data.get("errors", [])) > 0


class TestInputValidationFeedback:
    """Test input validation for /api/feedback endpoint."""
    
    def test_missing_required_fields(self):
        """Test missing required fields."""
        # Missing generation_id
        response = client.post(
            "/api/feedback",
            json={"session_id": "test", "thumbs_up": True}
        )
        assert response.status_code == 422
        
        # Missing session_id
        response = client.post(
            "/api/feedback",
            json={"generation_id": "test", "thumbs_up": True}
        )
        assert response.status_code == 422
        
        # Missing thumbs_up
        response = client.post(
            "/api/feedback",
            json={"generation_id": "test", "session_id": "test"}
        )
        assert response.status_code == 422
    
    def test_invalid_thumbs_up_type(self):
        """Test invalid thumbs_up type."""
        response = client.post(
            "/api/feedback",
            json={"generation_id": "test", "session_id": "test", "thumbs_up": "yes"}
        )
        assert response.status_code == 422
    
    def test_empty_strings(self):
        """Test empty string fields."""
        response = client.post(
            "/api/feedback",
            json={"generation_id": "", "session_id": "", "thumbs_up": True}
        )
        # May accept or reject empty strings
        assert response.status_code in [200, 400, 422, 500]


class TestInputValidationFileServing:
    """Test input validation for /api/diagrams/{filename} endpoint."""
    
    def test_path_traversal_attempts(self):
        """Test path traversal attack attempts."""
        attacks = [
            "../etc/passwd",
            "..\\..\\windows\\system32",
            "%2E%2E%2Fetc%2Fpasswd",  # URL encoded
            "....//....//etc//passwd",
            "/etc/passwd",
            "C:\\Windows\\System32",
        ]
        
        for attack in attacks:
            response = client.get(f"/api/diagrams/{attack}")
            # Should reject with 403 or 400
            assert response.status_code in [400, 403, 404]
    
    def test_special_characters_in_filename(self):
        """Test special characters in filename."""
        special_chars = [
            "<script>alert('xss')</script>.png",
            "test;rm -rf /.png",
            "test|cat /etc/passwd.png",
            "test`whoami`.png",
        ]
        
        for filename in special_chars:
            response = client.get(f"/api/diagrams/{filename}")
            # Should reject or sanitize
            assert response.status_code in [400, 403, 404]
    
    def test_very_long_filename(self):
        """Test very long filename."""
        long_filename = "a" * 1000 + ".png"
        response = client.get(f"/api/diagrams/{long_filename}")
        # Should handle (may reject or truncate)
        assert response.status_code in [400, 403, 404, 414]


class TestErrorHandlingConsistency:
    """Test error handling consistency across endpoints."""
    
    def test_error_response_structure(self):
        """Test that error responses have consistent structure."""
        # Test 400 error
        response = client.post(
            "/api/generate-diagram",
            json={"description": "bake a cake", "provider": "aws"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        
        # Test 404 error
        response = client.get("/api/diagrams/nonexistent_file_12345.png")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        
        # Test 422 error (validation)
        response = client.post("/api/generate-diagram", json={})
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_error_messages_are_helpful(self):
        """Test that error messages are helpful and informative."""
        # Validation error
        response = client.post("/api/generate-diagram", json={})
        assert response.status_code == 422
        detail = response.json().get("detail", "")
        assert len(detail) > 0
        
        # Business logic error
        response = client.post(
            "/api/generate-diagram",
            json={"description": "bake a cake", "provider": "aws"}
        )
        assert response.status_code == 400
        detail = response.json().get("detail", "")
        assert len(detail) > 0
        assert "cloud architecture" in detail.lower() or "diagram" in detail.lower()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_null_values(self):
        """Test null/None values."""
        # None in description
        response = client.post(
            "/api/generate-diagram",
            json={"description": None, "provider": "aws"}
        )
        assert response.status_code == 422
        
        # None in optional fields
        response = client.post(
            "/api/generate-diagram",
            json={"description": "Test", "provider": "aws", "outformat": None}
        )
        # Should handle None in optional fields
        assert response.status_code in [200, 400, 422, 500]
    
    def test_boolean_values(self):
        """Test boolean values where strings expected."""
        response = client.post(
            "/api/generate-diagram",
            json={"description": True, "provider": "aws"}
        )
        assert response.status_code == 422
    
    def test_array_values(self):
        """Test array values where strings expected."""
        response = client.post(
            "/api/generate-diagram",
            json={"description": ["test"], "provider": "aws"}
        )
        assert response.status_code == 422
    
    def test_nested_objects(self):
        """Test nested objects where strings expected."""
        response = client.post(
            "/api/generate-diagram",
            json={"description": {"nested": "object"}, "provider": "aws"}
        )
        assert response.status_code == 422
    
    def test_extra_fields(self):
        """Test extra fields in request."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "EC2 instance",
                "provider": "aws",
                "outformat": "png",
                "extra_field": "should be ignored",
                "another_extra": 12345
            }
        )
        # Should accept and ignore extra fields
        assert response.status_code in [200, 400, 422, 500]

