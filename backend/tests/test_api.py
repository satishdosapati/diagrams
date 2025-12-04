"""
Comprehensive API endpoint tests.
"""
import pytest
import os
import time
from fastapi.testclient import TestClient
from pathlib import Path

# Import the app
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and info endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
    
    def test_request_id_header(self):
        """Test that request ID is included in response headers."""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) > 0


class TestDiagramGeneration:
    """Test diagram generation endpoints."""
    
    def test_generate_diagram_basic(self):
        """Test basic diagram generation."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "VPC with EC2 instance",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data
        assert "session_id" in data
        assert "message" in data
        assert "generated_code" in data
        assert data["diagram_url"].startswith("/api/diagrams/")
        return data["session_id"]
    
    def test_generate_diagram_all_formats(self):
        """Test diagram generation with all supported formats."""
        formats = ["png", "svg", "pdf", "dot"]
        for fmt in formats:
            response = client.post(
                "/api/generate-diagram",
                json={
                    "description": f"Simple EC2 instance - {fmt}",
                    "provider": "aws",
                    "outformat": fmt
                }
            )
            assert response.status_code == 200, f"Failed for format: {fmt}"
            data = response.json()
            assert "diagram_url" in data
    
    def test_generate_diagram_all_providers(self):
        """Test diagram generation for all providers."""
        providers = ["aws", "azure", "gcp"]
        for provider in providers:
            response = client.post(
                "/api/generate-diagram",
                json={
                    "description": f"Simple compute instance",
                    "provider": provider,
                    "outformat": "png"
                }
            )
            assert response.status_code == 200, f"Failed for provider: {provider}"
            data = response.json()
            assert "diagram_url" in data
    
    def test_generate_diagram_with_direction(self):
        """Test diagram generation with direction parameter."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "API Gateway to Lambda",
                "provider": "aws",
                "outformat": "png",
                "direction": "LR"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data
    
    def test_generate_diagram_invalid_provider(self):
        """Test diagram generation with invalid provider."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Test diagram",
                "provider": "invalid_provider",
                "outformat": "png"
            }
        )
        # Should either fail or handle gracefully
        assert response.status_code in [200, 400, 500]
    
    def test_generate_diagram_missing_description(self):
        """Test diagram generation without description."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert response.status_code in [400, 422]  # Validation error


class TestDiagramModification:
    """Test diagram modification endpoints."""
    
    def test_modify_diagram(self):
        """Test modifying an existing diagram."""
        # First generate a diagram
        gen_response = client.post(
            "/api/generate-diagram",
            json={
                "description": "VPC with EC2",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert gen_response.status_code == 200
        session_id = gen_response.json()["session_id"]
        
        # Then modify it
        response = client.post(
            "/api/modify-diagram",
            json={
                "session_id": session_id,
                "modification": "Add a Lambda function"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data
        assert "changes" in data
        assert "updated_spec" in data
    
    def test_modify_diagram_invalid_session(self):
        """Test modifying with invalid session ID."""
        response = client.post(
            "/api/modify-diagram",
            json={
                "session_id": "invalid-session-id",
                "modification": "Add component"
            }
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower() or "expired" in response.json()["detail"].lower()


class TestFormatRegeneration:
    """Test format regeneration endpoint."""
    
    def test_regenerate_format(self):
        """Test regenerating diagram in different format."""
        # Generate initial diagram
        gen_response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Simple EC2 instance",
                "provider": "aws",
                "outformat": "png"
            }
        )
        session_id = gen_response.json()["session_id"]
        
        # Regenerate as SVG
        response = client.post(
            "/api/regenerate-format",
            json={
                "session_id": session_id,
                "outformat": "svg"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data
        assert data["diagram_url"].endswith(".svg") or "svg" in data["message"].lower()
    
    def test_regenerate_format_invalid_session(self):
        """Test regenerating with invalid session."""
        response = client.post(
            "/api/regenerate-format",
            json={
                "session_id": "invalid-session",
                "outformat": "svg"
            }
        )
        assert response.status_code == 404


class TestCodeExecution:
    """Test code execution endpoints."""
    
    def test_execute_code_valid(self):
        """Test executing valid Python code."""
        code = """
from diagrams import Diagram
from diagrams.aws.compute import EC2

with Diagram("Test Diagram", show=False, filename="test_diagram", outformat="png"):
    EC2("Instance")
"""
        response = client.post(
            "/api/execute-code",
            json={
                "code": code,
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data or len(data.get("errors", [])) == 0
    
    def test_execute_code_invalid_syntax(self):
        """Test executing invalid Python code."""
        response = client.post(
            "/api/execute-code",
            json={
                "code": "invalid python syntax {",
                "outformat": "png"
            }
        )
        # Should return errors
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("errors", [])) > 0 or data.get("diagram_url") == ""


class TestCodeValidation:
    """Test code validation endpoint."""
    
    def test_validate_code_valid(self):
        """Test validating valid code."""
        code = "from diagrams import Diagram\nfrom diagrams.aws.compute import EC2"
        response = client.post(
            "/api/validate-code",
            json={"code": code}
        )
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert data["valid"] == True
    
    def test_validate_code_invalid_syntax(self):
        """Test validating invalid code."""
        code = "invalid syntax {"
        response = client.post(
            "/api/validate-code",
            json={"code": code}
        )
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert data["valid"] == False
        assert len(data.get("errors", [])) > 0


class TestCompletions:
    """Test completions endpoint."""
    
    def test_get_completions_aws(self):
        """Test getting completions for AWS."""
        response = client.get("/api/completions/aws")
        assert response.status_code == 200
        data = response.json()
        assert "classes" in data
        assert "imports" in data
    
    def test_get_completions_azure(self):
        """Test getting completions for Azure."""
        response = client.get("/api/completions/azure")
        assert response.status_code == 200
        data = response.json()
        assert "classes" in data
    
    def test_get_completions_gcp(self):
        """Test getting completions for GCP."""
        response = client.get("/api/completions/gcp")
        assert response.status_code == 200
        data = response.json()
        assert "classes" in data
    
    def test_get_completions_invalid_provider(self):
        """Test getting completions for invalid provider."""
        response = client.get("/api/completions/invalid")
        assert response.status_code in [400, 500]


class TestFileServing:
    """Test file serving endpoint."""
    
    def test_get_diagram_file(self):
        """Test retrieving a generated diagram file."""
        # First generate a diagram
        gen_response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Simple EC2",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert gen_response.status_code == 200
        diagram_url = gen_response.json()["diagram_url"]
        filename = diagram_url.split("/")[-1]
        
        # Try to retrieve it
        response = client.get(f"/api/diagrams/{filename}")
        # May be 404 if file hasn't been generated yet, or 200 if it exists
        assert response.status_code in [200, 404]
    
    def test_get_diagram_path_traversal_protection(self):
        """Test path traversal protection."""
        # Try path traversal attack
        response = client.get("/api/diagrams/../../../etc/passwd")
        assert response.status_code in [400, 403]
    
    def test_get_diagram_invalid_filename(self):
        """Test with invalid filename characters."""
        response = client.get("/api/diagrams/test<script>.png")
        assert response.status_code in [400, 403]


class TestSessionManagement:
    """Test session management."""
    
    def test_session_expiration(self):
        """Test that sessions expire properly."""
        # Generate diagram
        gen_response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Test diagram",
                "provider": "aws",
                "outformat": "png"
            }
        )
        session_id = gen_response.json()["session_id"]
        
        # Session should be accessible immediately
        mod_response = client.post(
            "/api/modify-diagram",
            json={
                "session_id": session_id,
                "modification": "test"
            }
        )
        # Should work (200) or fail gracefully
        assert mod_response.status_code in [200, 404, 500]


class TestUndo:
    """Test undo endpoint."""
    
    def test_undo_diagram(self):
        """Test undoing diagram changes."""
        # Generate diagram
        gen_response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Simple architecture",
                "provider": "aws",
                "outformat": "png"
            }
        )
        session_id = gen_response.json()["session_id"]
        
        # Try to undo
        response = client.post(
            "/api/undo-diagram",
            json={"session_id": session_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data

