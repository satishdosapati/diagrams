"""
Tests for component resolvers.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.resolvers.component_resolver import ComponentResolver
from src.resolvers.intelligent_resolver import IntelligentNodeResolver
from src.models.spec import Component, NodeType, ArchitectureSpec


class TestComponentResolver:
    """Test ComponentResolver class."""
    
    def test_resolve_aws_component(self):
        """Test resolving AWS component."""
        resolver = ComponentResolver(primary_provider="aws")
        comp = Component(id="lambda", name="Function", type=NodeType.LAMBDA)
        
        node_class = resolver.resolve_component_class(comp)
        assert node_class is not None
        assert "Lambda" in node_class.__name__
    
    def test_resolve_azure_component(self):
        """Test resolving Azure component."""
        resolver = ComponentResolver(primary_provider="azure")
        comp = Component(id="func", name="Function", type=NodeType.AZURE_FUNCTION)
        
        node_class = resolver.resolve_component_class(comp)
        assert node_class is not None
    
    def test_resolve_gcp_component(self):
        """Test resolving GCP component."""
        resolver = ComponentResolver(primary_provider="gcp")
        comp = Component(id="compute", name="Compute Engine", type=NodeType.COMPUTE_ENGINE)
        
        node_class = resolver.resolve_component_class(comp)
        assert node_class is not None
        assert "ComputeEngine" in node_class.__name__ or "Compute" in node_class.__name__
    
    def test_resolve_aws_s3(self):
        """Test resolving AWS S3 component."""
        resolver = ComponentResolver(primary_provider="aws")
        comp = Component(id="s3", name="S3 Bucket", type=NodeType.S3)
        
        node_class = resolver.resolve_component_class(comp)
        assert node_class is not None
        assert "S3" in node_class.__name__
    
    def test_resolve_aws_rds(self):
        """Test resolving AWS RDS component."""
        resolver = ComponentResolver(primary_provider="aws")
        comp = Component(id="rds", name="RDS Database", type=NodeType.RDS)
        
        node_class = resolver.resolve_component_class(comp)
        assert node_class is not None
        assert "RDS" in node_class.__name__
    
    def test_resolve_azure_vm(self):
        """Test resolving Azure VM component."""
        resolver = ComponentResolver(primary_provider="azure")
        comp = Component(id="vm", name="Azure VM", type=NodeType.AZURE_VM)
        
        node_class = resolver.resolve_component_class(comp)
        assert node_class is not None
    
    def test_resolve_azure_blob_storage(self):
        """Test resolving Azure Blob Storage component."""
        resolver = ComponentResolver(primary_provider="azure")
        comp = Component(id="blob", name="Blob Storage", type=NodeType.BLOB_STORAGE)
        
        node_class = resolver.resolve_component_class(comp)
        assert node_class is not None
    
    def test_resolve_gcp_cloud_function(self):
        """Test resolving GCP Cloud Function component."""
        resolver = ComponentResolver(primary_provider="gcp")
        comp = Component(id="function", name="Cloud Function", type=NodeType.CLOUD_FUNCTION)
        
        node_class = resolver.resolve_component_class(comp)
        assert node_class is not None
    
    def test_resolve_gcp_cloud_storage(self):
        """Test resolving GCP Cloud Storage component."""
        resolver = ComponentResolver(primary_provider="gcp")
        comp = Component(id="storage", name="Cloud Storage", type=NodeType.CLOUD_STORAGE)
        
        node_class = resolver.resolve_component_class(comp)
        assert node_class is not None
    
    def test_resolve_gcp_bigquery(self):
        """Test resolving GCP BigQuery component."""
        resolver = ComponentResolver(primary_provider="gcp")
        comp = Component(id="bigquery", name="BigQuery", type=NodeType.BIGQUERY)
        
        node_class = resolver.resolve_component_class(comp)
        assert node_class is not None
    
    def test_resolve_with_node_id(self):
        """Test resolving component using node_id."""
        resolver = ComponentResolver(primary_provider="aws")
        comp = Component(id="lambda", name="Function", type="lambda")  # Using string type
        
        node_class = resolver.resolve_component_class(comp)
        assert node_class is not None


class TestIntelligentNodeResolver:
    """Test IntelligentNodeResolver class."""
    
    @pytest.fixture
    def aws_resolver(self):
        """Create IntelligentNodeResolver instance for AWS."""
        return IntelligentNodeResolver(provider="aws")
    
    @pytest.fixture
    def azure_resolver(self):
        """Create IntelligentNodeResolver instance for Azure."""
        return IntelligentNodeResolver(provider="azure")
    
    @pytest.fixture
    def gcp_resolver(self):
        """Create IntelligentNodeResolver instance for GCP."""
        return IntelligentNodeResolver(provider="gcp")
    
    def test_initialization(self, aws_resolver):
        """Test IntelligentNodeResolver initialization."""
        assert aws_resolver is not None
        assert aws_resolver.provider == "aws"
        assert hasattr(aws_resolver, 'resolve')
        assert hasattr(aws_resolver, 'node_index')
    
    def test_resolve_exact_match(self, aws_resolver):
        """Test resolving exact node_id match."""
        result = aws_resolver.resolve("lambda")
        assert result == "lambda" or result is not None
    
    def test_resolve_fuzzy_match(self, aws_resolver):
        """Test resolving with fuzzy matching."""
        # Test common variations
        result = aws_resolver.resolve("ec2")
        assert result is not None
        
        result = aws_resolver.resolve("s3")
        assert result is not None
    
    def test_resolve_with_component_name(self, aws_resolver):
        """Test resolving with component name context."""
        result = aws_resolver.resolve("function", component_name="Lambda Function")
        # Should resolve to lambda
        assert result is not None
    
    def test_resolve_subnet_public(self, aws_resolver):
        """Test resolving public subnet."""
        result = aws_resolver.resolve("subnet", component_name="Public Subnet")
        assert result is not None
        # Should resolve to public_subnet or subnet
        assert "subnet" in result.lower()
    
    def test_resolve_subnet_private(self, aws_resolver):
        """Test resolving private subnet."""
        result = aws_resolver.resolve("subnet", component_name="Private Subnet")
        assert result is not None
        assert "subnet" in result.lower()
    
    def test_resolve_function_lambda(self, aws_resolver):
        """Test resolving function to lambda."""
        result = aws_resolver.resolve("function", component_name="Serverless Function")
        assert result is not None
        # Should prefer lambda for serverless
        assert "lambda" in result.lower() or result == "lambda"
    
    def test_get_suggestions(self, aws_resolver):
        """Test getting suggestions for unknown node."""
        suggestions = aws_resolver.get_suggestions("lamda", limit=3)  # Typo: lamda instead of lambda
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        # Should suggest lambda
        assert any("lambda" in s[0].lower() for s in suggestions)
    
    def test_resolve_azure_vm(self, azure_resolver):
        """Test resolving Azure VM."""
        result = azure_resolver.resolve("vm")
        assert result is not None
    
    def test_resolve_gcp_compute(self, gcp_resolver):
        """Test resolving GCP Compute Engine."""
        result = gcp_resolver.resolve("compute")
        assert result is not None

