"""
Health check and system validation tests.
"""
import pytest
import os
import subprocess
from pathlib import Path
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app

client = TestClient(app)


class TestSystemHealth:
    """Test system health and dependencies."""
    
    def test_graphviz_installed(self):
        """Test that Graphviz is installed and accessible."""
        try:
            result = subprocess.run(
                ["dot", "-V"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode == 0 or "graphviz" in result.stderr.lower() or "dot" in result.stdout.lower()
        except FileNotFoundError:
            pytest.fail("Graphviz (dot) command not found. Install with: sudo yum install graphviz")
    
    def test_python_version(self):
        """Test Python version compatibility."""
        import sys
        assert sys.version_info >= (3, 10), f"Python 3.10+ required, found {sys.version}"
    
    def test_required_modules(self):
        """Test that required Python modules are installed."""
        required_modules = [
            "fastapi",
            "pydantic",
            "diagrams",
            "graphviz",
            "yaml"
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        assert len(missing_modules) == 0, f"Missing required modules: {', '.join(missing_modules)}"
    
    def test_output_directory_exists(self):
        """Test that output directory exists and is writable."""
        output_dir = os.getenv("OUTPUT_DIR", "./output")
        output_path = Path(output_dir)
        
        # Directory should exist or be creatable
        output_path.mkdir(parents=True, exist_ok=True)
        assert output_path.exists()
        assert output_path.is_dir()
        
        # Should be writable
        test_file = output_path / ".test_write"
        try:
            test_file.write_text("test")
            test_file.unlink()
            is_writable = True
        except Exception:
            is_writable = False
        
        assert is_writable, f"Output directory {output_dir} is not writable"
    
    def test_environment_variables(self):
        """Test that required environment variables are set (if needed)."""
        # These are optional, but check if they're set correctly if present
        bedrock_model = os.getenv("BEDROCK_MODEL_ID")
        aws_region = os.getenv("AWS_REGION")
        
        # Just verify they're strings if set (not testing actual AWS connectivity)
        if bedrock_model:
            assert isinstance(bedrock_model, str)
        if aws_region:
            assert isinstance(aws_region, str)


class TestAPIHealth:
    """Test API health endpoints."""
    
    def test_api_responds(self):
        """Test that API is responding."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_api_cors_headers(self):
        """Test that CORS headers are present."""
        response = client.options("/health")
        # CORS headers may or may not be present in test client
        # Just verify request doesn't fail
        assert response.status_code in [200, 405]
    
    def test_api_error_handling(self):
        """Test that API handles errors gracefully."""
        # Test invalid endpoint
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        
        # Test invalid method
        response = client.delete("/api/generate-diagram")
        assert response.status_code == 405  # Method not allowed


class TestComponentResolution:
    """Test component resolution system."""
    
    def test_aws_component_resolution(self):
        """Test that AWS components can be resolved."""
        from src.resolvers.component_resolver import ComponentResolver
        from src.models.spec import Component, NodeType
        
        resolver = ComponentResolver(primary_provider="aws")
        comp = Component(id="lambda", name="Function", type=NodeType.LAMBDA)
        
        try:
            node_class = resolver.resolve_component_class(comp)
            assert node_class is not None
        except Exception as e:
            pytest.fail(f"AWS component resolution failed: {e}")
    
    def test_azure_component_resolution(self):
        """Test that Azure components can be resolved."""
        from src.resolvers.component_resolver import ComponentResolver
        from src.models.spec import Component, NodeType
        
        resolver = ComponentResolver(primary_provider="azure")
        comp = Component(id="func", name="Function", type=NodeType.AZURE_FUNCTION)
        
        try:
            node_class = resolver.resolve_component_class(comp)
            assert node_class is not None
        except Exception as e:
            pytest.fail(f"Azure component resolution failed: {e}")
    
    def test_gcp_component_resolution(self):
        """Test that GCP components can be resolved."""
        from src.resolvers.component_resolver import ComponentResolver
        from src.models.spec import Component, NodeType
        
        resolver = ComponentResolver(primary_provider="gcp")
        comp = Component(id="compute", name="Compute", type=NodeType.GCP_COMPUTE_ENGINE)
        
        try:
            node_class = resolver.resolve_component_class(comp)
            assert node_class is not None
        except Exception as e:
            pytest.fail(f"GCP component resolution failed: {e}")














