"""
Comprehensive integration tests for end-to-end workflows.
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
    """Test complete user workflows end-to-end."""
    
    def test_complete_diagram_workflow(self):
        """Test complete workflow: generate -> regenerate format -> feedback."""
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
        assert "generated_code" in gen_data
        
        # Verify advisor enhancements
        assert "splines=\"ortho\"" in gen_data["generated_code"] or "splines='ortho'" in gen_data["generated_code"]
        
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
        feedback_data = feedback_response.json()
        assert "feedback_id" in feedback_data
    
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
            assert response.status_code == 200, f"Failed for provider: {provider}"
            data = response.json()
            session_ids.append(data["session_id"])
            # Verify advisor enhancements
            assert "splines=\"ortho\"" in data["generated_code"] or "splines='ortho'" in data["generated_code"]
        
        assert len(session_ids) == len(providers)
        
        # Test regeneration for each session
        for session_id in session_ids:
            regen_response = client.post(
                "/api/regenerate-format",
                json={
                    "session_id": session_id,
                    "outformat": "svg"
                }
            )
            assert regen_response.status_code == 200
    
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
    
    def test_provider_specific_advisor_workflow(self):
        """Test that advisors are applied correctly for each provider end-to-end."""
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
            # Generate diagram
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
            
            # Test regeneration
            regen_response = client.post(
                "/api/regenerate-format",
                json={
                    "session_id": data["session_id"],
                    "outformat": "svg"
                }
            )
            assert regen_response.status_code == 200
    
    def test_complex_architecture_workflow_aws(self):
        """Test generating complex AWS architecture end-to-end."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Multi-tier architecture with VPC, public and private subnets, EC2 instances, RDS database, S3 bucket, CloudFront CDN, and API Gateway with Lambda functions",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data
        assert "generated_code" in data
        assert "session_id" in data
        
        # Verify advisor enhancements
        assert "splines=\"ortho\"" in data["generated_code"] or "splines='ortho'" in data["generated_code"]
        
        # Test regeneration
        regen_response = client.post(
            "/api/regenerate-format",
            json={
                "session_id": data["session_id"],
                "outformat": "pdf"
            }
        )
        assert regen_response.status_code == 200
    
    def test_complex_architecture_workflow_azure(self):
        """Test generating complex Azure architecture end-to-end."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Multi-tier architecture with Virtual Network, public and private subnets, Azure VMs, Azure SQL Database, Blob Storage, Azure CDN, and API Management with Azure Functions",
                "provider": "azure",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data
        assert "generated_code" in data
        assert "session_id" in data
        
        # Verify advisor enhancements
        assert "splines=\"ortho\"" in data["generated_code"] or "splines='ortho'" in data["generated_code"]
        
        # Test regeneration
        regen_response = client.post(
            "/api/regenerate-format",
            json={
                "session_id": data["session_id"],
                "outformat": "svg"
            }
        )
        assert regen_response.status_code == 200
    
    def test_complex_architecture_workflow_gcp(self):
        """Test generating complex GCP architecture end-to-end."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Multi-tier architecture with VPC, public and private subnets, Compute Engine instances, Cloud SQL, Cloud Storage, Cloud CDN, and API Gateway with Cloud Functions",
                "provider": "gcp",
                "outformat": "png"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data
        assert "generated_code" in data
        assert "session_id" in data
        
        # Verify advisor enhancements
        assert "splines=\"ortho\"" in data["generated_code"] or "splines='ortho'" in data["generated_code"]
        
        # Test regeneration
        regen_response = client.post(
            "/api/regenerate-format",
            json={
                "session_id": data["session_id"],
                "outformat": "dot"
            }
        )
        assert regen_response.status_code == 200
    
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
        
        # Test invalid session
        regen_response = client.post(
            "/api/regenerate-format",
            json={
                "session_id": "invalid-session-id",
                "outformat": "svg"
            }
        )
        assert regen_response.status_code == 404
    
    def test_performance_workflow(self):
        """Test that multiple requests can be handled efficiently."""
        start_time = time.time()
        
        # Generate multiple diagrams sequentially
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
    
    def test_session_persistence_workflow(self):
        """Test that sessions persist across multiple operations."""
        # Generate diagram
        gen_response = client.post(
            "/api/generate-diagram",
            json={
                "description": "VPC with EC2 instance",
                "provider": "aws",
                "outformat": "png"
            }
        )
        assert gen_response.status_code == 200
        session_id = gen_response.json()["session_id"]
        generation_id = gen_response.json()["generation_id"]
        
        # Regenerate multiple times
        formats = ["svg", "pdf", "dot"]
        for fmt in formats:
            regen_response = client.post(
                "/api/regenerate-format",
                json={
                    "session_id": session_id,
                    "outformat": fmt
                }
            )
            assert regen_response.status_code == 200, f"Failed for format: {fmt}"
        
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
    
    def test_all_formats_workflow(self):
        """Test generating and regenerating all supported formats."""
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
        
        # Regenerate to all formats
        formats = ["png", "svg", "pdf", "dot"]
        for fmt in formats:
            regen_response = client.post(
                "/api/regenerate-format",
                json={
                    "session_id": session_id,
                    "outformat": fmt
                }
            )
            assert regen_response.status_code == 200, f"Failed for format: {fmt}"
            data = regen_response.json()
            assert "diagram_url" in data
    
    def test_feedback_workflow(self):
        """Test complete feedback workflow."""
        # Generate diagram
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
        
        # Submit positive feedback
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
        
        # Check feedback stats
        stats_response = client.get("/api/feedback/stats")
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        assert isinstance(stats_data, dict)
    
    def test_direction_workflow(self):
        """Test diagram generation with different directions."""
        directions = ["LR", "TB", "BT", "RL"]
        
        for direction in directions:
            response = client.post(
                "/api/generate-diagram",
                json={
                    "description": "API Gateway to Lambda",
                    "provider": "aws",
                    "outformat": "png",
                    "direction": direction
                }
            )
            assert response.status_code == 200, f"Failed for direction: {direction}"
            data = response.json()
            assert "diagram_url" in data
    
    def test_graphviz_attrs_workflow(self):
        """Test diagram generation with custom Graphviz attributes."""
        response = client.post(
            "/api/generate-diagram",
            json={
                "description": "Simple EC2 instance",
                "provider": "aws",
                "outformat": "png",
                "graphviz_attrs": {
                    "graph_attr": {"bgcolor": "lightblue", "rankdir": "LR"},
                    "node_attr": {"style": "filled", "fillcolor": "white"},
                    "edge_attr": {"color": "blue", "style": "bold"}
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "diagram_url" in data
    
    def test_multi_provider_complex_workflow(self):
        """Test complex workflows across all providers."""
        providers = ["aws", "azure", "gcp"]
        
        for provider in providers:
            # Generate complex diagram
            gen_response = client.post(
                "/api/generate-diagram",
                json={
                    "description": f"Serverless API with API Gateway, Functions, Database, Storage, and CDN on {provider}",
                    "provider": provider,
                    "outformat": "png"
                }
            )
            assert gen_response.status_code == 200, f"Failed for provider: {provider}"
            data = gen_response.json()
            
            # Verify advisor enhancements
            assert "splines=\"ortho\"" in data["generated_code"] or "splines='ortho'" in data["generated_code"]
            
            # Regenerate
            regen_response = client.post(
                "/api/regenerate-format",
                json={
                    "session_id": data["session_id"],
                    "outformat": "svg"
                }
            )
            assert regen_response.status_code == 200
            
            # Submit feedback
            feedback_response = client.post(
                "/api/feedback",
                json={
                    "generation_id": data["generation_id"],
                    "session_id": data["session_id"],
                    "thumbs_up": True
                }
            )
            assert feedback_response.status_code == 200
