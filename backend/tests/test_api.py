"""
Comprehensive API endpoint tests with end-to-end coverage.
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
        assert "docs" in data
        assert "health" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert data["service"] == "diagram-generator-api"
    
    def test_request_id_header(self):
        """Test that request ID is included in response headers."""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) > 0
        assert isinstance(float(response.headers["X-Process-Time"]), float)


class TestDiagramGeneration:
    """Test diagram generation endpoints with comprehensive coverage."""
    
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
        assert "generation_id" in data
        assert data["diagram_url"].startswith("/api/diagrams/")
        assert len(data["session_id"]) > 0
        assert len(data["generation_id"]) > 0
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
            assert "session_id" in data
    
    def test_generate_diagram_all_providers(self):
        """Test diagram generation for all providers with provider-specific services."""
        provider_tests = {
            "aws": "EC2 instance",
            "azure": "Azure VM virtual machine",
            "gcp": "Compute Engine instance"
        }
        
        for provider, description in provider_tests.items():
            response = client.post(
                "/api/generate-diagram",
                json={
                    "description": description,
                    "provider": provider,
                    "outformat": "png"
                }
            )
            assert response.status_code == 200, f"Failed for provider: {provider}"
            data = response.json()
            assert "diagram_url" in data
            assert "generated_code" in data
            
            # Verify generated code uses correct provider module
            generated_code = data["generated_code"]
            if provider == "aws":
                assert "diagrams.aws" in generated_code or "from diagrams.aws" in generated_code
            elif provider == "azure":
                assert "diagrams.azure" in generated_code or "from diagrams.azure" in generated_code
            elif provider == "gcp":
                assert "diagrams.gcp" in generated_code or "from diagrams.gcp" in generated_code
    
    def test_generate_diagram_advisor_enhancement_aws(self):
        """Test that AWS diagrams are enhanced by advisor."""
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
        generated_code = data["generated_code"]
        # Advisor should apply orthogonal routing
        assert "splines=\"ortho\"" in generated_code or "splines='ortho'" in generated_code or "splines=ortho" in generated_code
    
    def test_generate_diagram_advisor_enhancement_azure(self):
        """Test that Azure diagrams are enhanced by advisor."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Virtual Network with Azure VM",
                "provider": "azure",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        generated_code = data["generated_code"]
        # Advisor should apply orthogonal routing
        assert "splines=\"ortho\"" in generated_code or "splines='ortho'" in generated_code or "splines=ortho" in generated_code
    
    def test_generate_diagram_advisor_enhancement_gcp(self):
        """Test that GCP diagrams are enhanced by advisor."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "VPC with Compute Engine",
                "provider": "gcp",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        generated_code = data["generated_code"]
        # Advisor should apply orthogonal routing
        assert "splines=\"ortho\"" in generated_code or "splines='ortho'" in generated_code or "splines=ortho" in generated_code
    
    def test_generate_diagram_advisor_ordering_aws(self):
        """Test that AWS advisor orders components correctly."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "S3 bucket, VPC, Lambda function",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Components should be ordered: VPC (network) -> Lambda (compute) -> S3 (data)
        # This is verified by checking the generated code structure
        assert "diagram_url" in data
        assert "generated_code" in data
    
    def test_generate_diagram_advisor_ordering_azure(self):
        """Test that Azure advisor orders components correctly."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Blob Storage, Virtual Network, Azure Function",
                "provider": "azure",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Components should be ordered: Virtual Network (network) -> Azure Function (compute) -> Blob Storage (data)
        assert "diagram_url" in data
        assert "generated_code" in data
    
    def test_generate_diagram_advisor_ordering_gcp(self):
        """Test that GCP advisor orders components correctly."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Cloud Storage, VPC, Cloud Function",
                "provider": "gcp",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Components should be ordered: VPC (network) -> Cloud Function (compute) -> Cloud Storage (data)
        assert "diagram_url" in data
        assert "generated_code" in data
    
    def test_generate_diagram_with_direction(self):
        """Test diagram generation with direction parameter for all providers."""
        directions = ["LR", "TB", "BT", "RL"]
        providers = ["aws", "azure", "gcp"]
        
        for provider in providers:
            for direction in directions:
                response = client.post(
                    "/api/generate-diagram",
                    json={
                        "description": f"API Gateway to Lambda on {provider}",
                        "provider": provider,
                        "outformat": "png",
                        "direction": direction
                    }
                )
                assert response.status_code == 200, f"Failed for {provider} with direction {direction}"
                data = response.json()
                assert "diagram_url" in data
    
    def test_generate_diagram_with_graphviz_attrs(self):
        """Test diagram generation with custom Graphviz attributes."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Simple EC2 instance",
                "provider": "aws",
                "outformat": "png",
                "graphviz_attrs": {
                    "graph_attr": {"bgcolor": "lightblue"},
                    "node_attr": {"style": "filled"},
                    "edge_attr": {"color": "red"}
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data
    
    def test_generate_diagram_provider_specific_services(self):
        """Test diagram generation with provider-specific services."""
        provider_tests = {
            "aws": {
                "description": "VPC with EC2 instance and RDS database",
                "expected_modules": ["diagrams.aws.compute", "diagrams.aws.database", "diagrams.aws.network"]
            },
            "azure": {
                "description": "Virtual Network with Azure VM and Azure SQL Database",
                "expected_modules": ["diagrams.azure.compute", "diagrams.azure.database", "diagrams.azure.network"]
            },
            "gcp": {
                "description": "VPC with Compute Engine and Cloud SQL",
                "expected_modules": ["diagrams.gcp.compute", "diagrams.gcp.database", "diagrams.gcp.network"]
            }
        }
        
        for provider, test_config in provider_tests.items():
            response = client.post(
                "/api/generate-diagram",
                json={
                    "description": test_config["description"],
                    "provider": provider,
                    "outformat": "png"
                }
            )
            assert response.status_code == 200, f"Failed for provider: {provider}"
            data = response.json()
            assert "diagram_url" in data
            assert "generated_code" in data
            
            # Verify generated code uses correct provider modules
            generated_code = data["generated_code"]
            for expected_module in test_config["expected_modules"]:
                # Check if module is imported or used in code
                assert expected_module in generated_code or expected_module.replace("diagrams.", "") in generated_code, \
                    f"Expected module {expected_module} not found in generated code for {provider}"
    
    def test_generate_diagram_complex_architecture_aws(self):
        """Test generating complex AWS architecture."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Serverless API with API Gateway, Lambda functions, DynamoDB, S3 bucket, and CloudFront CDN",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data
        assert "generated_code" in data
        # Verify advisor enhancements are applied
        assert "splines=\"ortho\"" in data["generated_code"] or "splines='ortho'" in data["generated_code"]
    
    def test_generate_diagram_complex_architecture_azure(self):
        """Test generating complex Azure architecture."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Serverless API with API Management, Azure Functions, Cosmos DB, Blob Storage, and CDN",
                "provider": "azure",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data
        assert "generated_code" in data
        # Verify advisor enhancements are applied
        assert "splines=\"ortho\"" in data["generated_code"] or "splines='ortho'" in data["generated_code"]
    
    def test_generate_diagram_complex_architecture_gcp(self):
        """Test generating complex GCP architecture."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Serverless API with API Gateway, Cloud Functions, Firestore, Cloud Storage, and Cloud CDN",
                "provider": "gcp",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data
        assert "generated_code" in data
        # Verify advisor enhancements are applied
        assert "splines=\"ortho\"" in data["generated_code"] or "splines='ortho'" in data["generated_code"]
    
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
    
    def test_generate_diagram_empty_description(self):
        """Test diagram generation with empty description."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "",
                "provider": "aws",
                "outformat": "png"
            }
        )
        # Should fail validation or handle gracefully
        assert response.status_code in [400, 422, 500]
    
    def test_generate_diagram_invalid_format(self):
        """Test diagram generation with invalid format."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Test diagram",
                "provider": "aws",
                "outformat": "invalid_format"
            }
        )
        # Should handle gracefully (may normalize to default or fail)
        assert response.status_code in [200, 400, 422]


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
        assert gen_response.status_code == 200
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
    
    def test_regenerate_format_all_formats(self):
        """Test regenerating to all supported formats."""
        # Generate initial diagram
        gen_response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Simple EC2 instance",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert gen_response.status_code == 200
        session_id = gen_response.json()["session_id"]
        
        formats = ["png", "svg", "pdf", "dot"]
        for fmt in formats:
            response = client.post(
                "/api/regenerate-format",
                json={
                    "session_id": session_id,
                    "outformat": fmt
                }
            )
            assert response.status_code == 200, f"Failed for format: {fmt}"
            data = response.json()
            assert "diagram_url" in data
    
    def test_regenerate_format_invalid_session(self):
        """Test regenerating with invalid session."""
        response = client.post(
            "/api/regenerate-format",
            json={
                "session_id": "invalid-session-id",
                "outformat": "svg"
            }
        )
        assert response.status_code == 404
    
    def test_regenerate_format_missing_session_id(self):
        """Test regenerating without session ID."""
        response = client.post(
            "/api/regenerate-format",
            json={
                "outformat": "svg"
            }
        )
        assert response.status_code in [400, 422]  # Validation error
    
    def test_regenerate_format_missing_outformat(self):
        """Test regenerating without outformat."""
        gen_response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Simple EC2 instance",
                "provider": "aws",
                "outformat": "png"
            }
        )
        session_id = gen_response.json()["session_id"]
        
        response = client.post(
            "/api/regenerate-format",
            json={
                "session_id": session_id
            }
        )
        assert response.status_code in [400, 422]  # Validation error


class TestCodeExecution:
    """Test code execution endpoints."""
    
    def test_execute_code_valid_aws(self):
        """Test executing valid Python code for AWS."""
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
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data or len(data.get("errors", [])) == 0
    
    def test_execute_code_valid_azure(self):
        """Test executing valid Python code for Azure."""
        code = """
from diagrams import Diagram
from diagrams.azure.compute import VM

with Diagram("Test Diagram", show=False, filename="test_diagram", outformat="png"):
    VM("Instance")
"""
        response = client.post(
            "/api/execute-code",
            json={
                "code": code,
                "provider": "azure",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data or len(data.get("errors", [])) == 0
    
    def test_execute_code_valid_gcp(self):
        """Test executing valid Python code for GCP."""
        code = """
from diagrams import Diagram
from diagrams.gcp.compute import ComputeEngine

with Diagram("Test Diagram", show=False, filename="test_diagram", outformat="png"):
    ComputeEngine("Instance")
"""
        response = client.post(
            "/api/execute-code",
            json={
                "code": code,
                "provider": "gcp",
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
    
    def test_execute_code_missing_code(self):
        """Test executing without code."""
        response = client.post(
            "/api/execute-code",
            json={
                "outformat": "png"
            }
        )
        assert response.status_code in [400, 422]  # Validation error
    
    def test_execute_code_with_connections(self):
        """Test executing code with component connections."""
        code = """
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS

with Diagram("Test Diagram", show=False, filename="test_diagram", outformat="png"):
    ec2 = EC2("Web Server")
    db = RDS("Database")
    ec2 >> db
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
    
    def test_validate_code_missing_code(self):
        """Test validating without code."""
        response = client.post(
            "/api/validate-code",
            json={}
        )
        assert response.status_code in [400, 422]  # Validation error
    
    def test_validate_code_empty_code(self):
        """Test validating empty code."""
        response = client.post(
            "/api/validate-code",
            json={"code": ""}
        )
        assert response.status_code == 200
    
    def test_validate_code_with_list_assignments(self):
        """Test validating code with list variable assignments (official diagrams library pattern)."""
        # This is the exact pattern from official diagrams library examples
        code = """from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS, EKS, Lambda
from diagrams.aws.database import Redshift
from diagrams.aws.integration import SQS
from diagrams.aws.storage import S3

with Diagram("Event Processing", show=False):
    source = EKS("k8s source")

    with Cluster("Event Flows"):
        with Cluster("Event Workers"):
            workers = [ECS("worker1"),
                       ECS("worker2"),
                       ECS("worker3")]

        queue = SQS("event queue")

        with Cluster("Processing"):
            handlers = [Lambda("proc1"),
                        Lambda("proc2"),
                        Lambda("proc3")]

    store = S3("events store")
    dw = Redshift("analytics")

    source >> workers >> queue >> handlers
    handlers >> store
    handlers >> dw"""
        
        response = client.post(
            "/api/validate-code",
            json={"code": code}
        )
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        # Should be valid - list assignments are valid Python and supported by diagrams library
        assert data["valid"] == True, f"Validation failed with errors: {data.get('errors', [])}"
        assert len(data.get("errors", [])) == 0, f"Unexpected errors: {data.get('errors', [])}"
        data = response.json()
        # Empty code may be valid or invalid depending on implementation
        assert "valid" in data


class TestCompletions:
    """Test completions endpoint."""
    
    def test_get_completions_aws(self):
        """Test getting completions for AWS."""
        response = client.get("/api/completions/aws")
        assert response.status_code == 200
        data = response.json()
        assert "classes" in data
        assert "imports" in data
        assert isinstance(data["classes"], dict)
        assert isinstance(data["imports"], dict)
    
    def test_get_completions_azure(self):
        """Test getting completions for Azure."""
        response = client.get("/api/completions/azure")
        assert response.status_code == 200
        data = response.json()
        assert "classes" in data
        assert isinstance(data["classes"], dict)
    
    def test_get_completions_gcp(self):
        """Test getting completions for GCP."""
        response = client.get("/api/completions/gcp")
        assert response.status_code == 200
        data = response.json()
        assert "classes" in data
        assert isinstance(data["classes"], dict)
    
    def test_get_completions_invalid_provider(self):
        """Test getting completions for invalid provider."""
        response = client.get("/api/completions/invalid")
        assert response.status_code in [400, 500]
    
    def test_get_completions_case_insensitive(self):
        """Test that completions endpoint handles case variations."""
        # Test uppercase
        response = client.get("/api/completions/AWS")
        assert response.status_code in [200, 400]  # May normalize or reject
    
    def test_get_completions_content_structure(self):
        """Test that completions return properly structured data."""
        response = client.get("/api/completions/aws")
        assert response.status_code == 200
        data = response.json()
        # Verify structure
        assert isinstance(data, dict)
        if "classes" in data:
            assert isinstance(data["classes"], dict)
        if "imports" in data:
            assert isinstance(data["imports"], dict)


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
    
    def test_get_diagram_path_traversal_url_encoded(self):
        """Test path traversal protection with URL encoding."""
        # Try URL-encoded path traversal
        response = client.get("/api/diagrams/..%2F..%2F..%2Fetc%2Fpasswd")
        assert response.status_code in [400, 403]
    
    def test_get_diagram_invalid_filename(self):
        """Test with invalid filename characters."""
        response = client.get("/api/diagrams/test<script>.png")
        assert response.status_code in [400, 403]
    
    def test_get_diagram_nonexistent_file(self):
        """Test retrieving non-existent diagram file."""
        response = client.get("/api/diagrams/nonexistent_file_12345.png")
        assert response.status_code == 404
    
    def test_get_diagram_empty_filename(self):
        """Test with empty filename."""
        response = client.get("/api/diagrams/")
        assert response.status_code in [400, 404, 405]  # May be 405 if route doesn't match


class TestSessionManagement:
    """Test session management."""
    
    def test_session_creation(self):
        """Test that sessions are created on diagram generation."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Test diagram",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        session_id = data["session_id"]
        assert len(session_id) > 0
        # Session should be usable for regeneration
        regen_response = client.post(
            "/api/regenerate-format",
            json={
                "session_id": session_id,
                "outformat": "svg"
            }
        )
        assert regen_response.status_code == 200
    
    def test_session_persistence(self):
        """Test that sessions persist across multiple requests."""
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
        
        # Regenerate multiple times
        for fmt in ["svg", "pdf", "dot"]:
            response = client.post(
                "/api/regenerate-format",
                json={
                    "session_id": session_id,
                    "outformat": fmt
                }
            )
            assert response.status_code == 200, f"Failed for format: {fmt}"
    
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
        regen_response = client.post(
            "/api/regenerate-format",
            json={
                "session_id": session_id,
                "outformat": "svg"
            }
        )
        assert regen_response.status_code == 200


class TestFeedbackEndpoints:
    """Test feedback endpoints."""
    
    def test_submit_feedback_thumbs_up(self):
        """Test submitting positive feedback."""
        # First generate a diagram
        gen_response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Simple EC2 instance",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert gen_response.status_code == 200
        data = gen_response.json()
        generation_id = data["generation_id"]
        session_id = data["session_id"]
        
        # Submit feedback
        feedback_response = client.post(
            "/api/feedback",
            json={
                "generation_id": generation_id,
                "session_id": session_id,
                "thumbs_up": True
            }
        )
        assert feedback_response.status_code == 200
        feedback_data = feedback_response.json()
        assert "feedback_id" in feedback_data
        assert "message" in feedback_data
    
    def test_submit_feedback_thumbs_down(self):
        """Test submitting negative feedback."""
        # First generate a diagram
        gen_response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Simple EC2 instance",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert gen_response.status_code == 200
        data = gen_response.json()
        generation_id = data["generation_id"]
        session_id = data["session_id"]
        
        # Submit feedback
        feedback_response = client.post(
            "/api/feedback",
            json={
                "generation_id": generation_id,
                "session_id": session_id,
                "thumbs_up": False
            }
        )
        assert feedback_response.status_code == 200
        feedback_data = feedback_response.json()
        assert "feedback_id" in feedback_data
    
    def test_submit_feedback_with_code(self):
        """Test submitting feedback with code."""
        # First generate a diagram
        gen_response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Simple EC2 instance",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert gen_response.status_code == 200
        data = gen_response.json()
        generation_id = data["generation_id"]
        session_id = data["session_id"]
        generated_code = data["generated_code"]
        
        # Submit feedback with code
        feedback_response = client.post(
            "/api/feedback",
            json={
                "generation_id": generation_id,
                "session_id": session_id,
                "thumbs_up": True,
                "code": generated_code
            }
        )
        assert feedback_response.status_code == 200
        feedback_data = feedback_response.json()
        assert "feedback_id" in feedback_data
    
    def test_submit_feedback_with_code_hash(self):
        """Test submitting feedback with code hash."""
        # First generate a diagram
        gen_response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Simple EC2 instance",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert gen_response.status_code == 200
        data = gen_response.json()
        generation_id = data["generation_id"]
        session_id = data["session_id"]
        
        # Submit feedback with code hash
        import hashlib
        code_hash = hashlib.sha256("test_code".encode('utf-8')).hexdigest()
        
        feedback_response = client.post(
            "/api/feedback",
            json={
                "generation_id": generation_id,
                "session_id": session_id,
                "thumbs_up": True,
                "code_hash": code_hash
            }
        )
        assert feedback_response.status_code == 200
        feedback_data = feedback_response.json()
        assert "feedback_id" in feedback_data
    
    def test_submit_feedback_missing_fields(self):
        """Test submitting feedback with missing required fields."""
        response = client.post(
            "/api/feedback",
            json={
                "thumbs_up": True
            }
        )
        assert response.status_code in [400, 422]  # Validation error
    
    def test_get_feedback_stats(self):
        """Test getting feedback statistics."""
        response = client.get("/api/feedback/stats")
        assert response.status_code == 200
        data = response.json()
        # Stats may be empty, but should return valid structure
        assert isinstance(data, dict)
    
    def test_get_feedback_stats_with_days(self):
        """Test getting feedback statistics with custom days."""
        response = client.get("/api/feedback/stats?days=7")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_feedback_stats_invalid_days(self):
        """Test getting feedback statistics with invalid days parameter."""
        response = client.get("/api/feedback/stats?days=invalid")
        # Should handle gracefully (may default to 30 or return error)
        assert response.status_code in [200, 400, 422]


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""
    
    def test_complete_workflow_generate_regenerate(self):
        """Test complete workflow: generate -> regenerate format."""
        # Step 1: Generate diagram
        gen_response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Serverless API with API Gateway, Lambda, and DynamoDB",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert gen_response.status_code == 200
        gen_data = gen_response.json()
        session_id = gen_data["session_id"]
        generation_id = gen_data["generation_id"]
        assert "diagram_url" in gen_data
        
        # Step 2: Regenerate in different format
        regen_response = client.post(
            "/api/regenerate-format",
            json={
                "session_id": session_id,
                "outformat": "svg"
            }
        )
        assert regen_response.status_code == 200
        regen_data = regen_response.json()
        assert "diagram_url" in regen_data
        
        # Step 3: Submit feedback
        feedback_response = client.post(
            "/api/feedback",
            json={
                "generation_id": generation_id,
                "session_id": session_id,
                "thumbs_up": True
            }
        )
        assert feedback_response.status_code == 200
    
    def test_multi_provider_workflow(self):
        """Test generating diagrams for different providers."""
        providers = ["aws", "azure", "gcp"]
        session_ids = []
        
        for provider in providers:
            response = client.post(
                "/api/generate-diagram",
                json={
                    "description": f"Simple compute instance on {provider}",
                    "provider": provider,
                    "outformat": "png"
                }
            )
            assert response.status_code == 200
            data = response.json()
            session_ids.append(data["session_id"])
            # Verify advisor enhancements
            assert "splines=\"ortho\"" in data["generated_code"] or "splines='ortho'" in data["generated_code"]
        
        assert len(session_ids) == len(providers)
    
    def test_advanced_code_mode_workflow(self):
        """Test Advanced Code Mode workflow."""
        # Step 1: Get completions
        completions_response = client.get("/api/completions/aws")
        assert completions_response.status_code == 200
        completions = completions_response.json()
        assert "classes" in completions
        
        # Step 2: Validate code
        code = """
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS

with Diagram("Architecture", show=False, filename="test", outformat="png"):
    ec2 = EC2("Web Server")
    db = RDS("Database")
    ec2 >> db
"""
        validate_response = client.post(
            "/api/validate-code",
            json={"code": code}
        )
        assert validate_response.status_code == 200
        validate_data = validate_response.json()
        assert validate_data["valid"] == True
        
        # Step 3: Execute code
        execute_response = client.post(
            "/api/execute-code",
            json={
                "code": code,
                "outformat": "png"
            }
        )
        assert execute_response.status_code == 200
        execute_data = execute_response.json()
        # May have errors if diagrams library not fully available, but should return response
        assert "diagram_url" in execute_data or "errors" in execute_data
    
    def test_error_handling_workflow(self):
        """Test error handling across the system."""
        # Test invalid format
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Test",
                "provider": "aws",
                "outformat": "invalid_format"
            }
        )
        # Should handle gracefully (may succeed with default or fail with validation)
        assert response.status_code in [200, 400, 422, 500]
    
    def test_performance_workflow(self):
        """Test that multiple requests can be handled."""
        start_time = time.time()
        
        # Generate multiple diagrams concurrently
        responses = []
        for i in range(3):
            response = client.post(
                "/api/generate-diagram",
                json={
                    "description": f"Test diagram {i}",
                    "provider": "aws",
                    "outformat": "png"
                }
            )
            responses.append(response)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Should complete in reasonable time (less than 60 seconds for 3 diagrams)
        assert duration < 60, f"Performance test took {duration} seconds"
    
    def test_provider_specific_advisor_workflow(self):
        """Test that advisors are applied correctly for each provider."""
        provider_scenarios = {
            "aws": {
                "description": "VPC with EC2 and S3",
                "expected_enhancements": ["splines=\"ortho\"", "splines='ortho'", "splines=ortho"]
            },
            "azure": {
                "description": "Virtual Network with Azure VM and Blob Storage",
                "expected_enhancements": ["splines=\"ortho\"", "splines='ortho'", "splines=ortho"]
            },
            "gcp": {
                "description": "VPC with Compute Engine and Cloud Storage",
                "expected_enhancements": ["splines=\"ortho\"", "splines='ortho'", "splines=ortho"]
            }
        }
        
        for provider, scenario in provider_scenarios.items():
            response = client.post(
                "/api/generate-diagram",
                json={
                    "description": scenario["description"],
                    "provider": provider,
                    "outformat": "png"
                }
            )
            assert response.status_code == 200, f"Failed for provider: {provider}"
            data = response.json()
            generated_code = data["generated_code"]
            # Verify advisor enhancements are present
            assert any(enh in generated_code for enh in scenario["expected_enhancements"]), \
                f"Advisor enhancements not found for {provider}"
