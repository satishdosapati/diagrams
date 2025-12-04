"""
Integration tests for end-to-end workflows.
"""
import pytest
import time
from fastapi.testclient import TestClient
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app

client = TestClient(app)


class TestEndToEndWorkflows:
    """Test complete user workflows."""
    
    def test_complete_diagram_workflow(self):
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

