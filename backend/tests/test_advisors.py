"""
Comprehensive tests for architectural advisors (AWS, Azure, GCP).
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.advisors.aws_architectural_advisor import AWSArchitecturalAdvisor
from src.advisors.azure_architectural_advisor import AzureArchitecturalAdvisor
from src.advisors.gcp_architectural_advisor import GCPArchitecturalAdvisor
from src.models.spec import ArchitectureSpec, Component, Connection, Cluster, GraphvizAttributes


class TestAWSArchitecturalAdvisor:
    """Test AWS Architectural Advisor."""
    
    @pytest.fixture
    def advisor(self):
        """Create AWS advisor instance."""
        return AWSArchitecturalAdvisor()
    
    def test_initialization(self, advisor):
        """Test advisor initialization."""
        assert advisor is not None
        assert hasattr(advisor, 'LAYER_ORDER')
        assert hasattr(advisor, 'DEPENDENCIES')
        assert hasattr(advisor, 'PATTERNS')
    
    def test_get_layer_order(self, advisor):
        """Test layer ordering for AWS components."""
        assert advisor.get_layer_order("route53") == 0
        assert advisor.get_layer_order("vpc") == 2
        assert advisor.get_layer_order("lambda") == 5
        assert advisor.get_layer_order("s3") == 7
        assert advisor.get_layer_order("unknown") == 5  # Default to compute layer
    
    def test_sort_components_by_layer(self, advisor):
        """Test component sorting by layer."""
        components = [
            Component(id="s3", name="S3", type="s3", provider="aws"),
            Component(id="vpc", name="VPC", type="vpc", provider="aws"),
            Component(id="lambda", name="Lambda", type="lambda", provider="aws"),
        ]
        sorted_components = advisor.sort_components_by_layer(components)
        assert sorted_components[0].get_node_id() == "vpc"
        assert sorted_components[1].get_node_id() == "lambda"
        assert sorted_components[2].get_node_id() == "s3"
    
    def test_suggest_missing_components(self, advisor):
        """Test missing component suggestions."""
        components = [
            Component(id="ec2", name="EC2", type="ec2", provider="aws"),
        ]
        suggestions = advisor.suggest_missing_components(components)
        assert len(suggestions) > 0
        assert any(s["type"] == "vpc" for s in suggestions)
        assert any(s["type"] == "subnet" for s in suggestions)
    
    def test_validate_connections_vpc_pattern(self, advisor):
        """Test VPC containment pattern."""
        components = [
            Component(id="vpc", name="VPC", type="vpc", provider="aws"),
            Component(id="subnet", name="Subnet", type="subnet", provider="aws"),
        ]
        connections = []
        suggested_conns, warnings = advisor.validate_connections(components, connections)
        assert len(suggested_conns) > 0
        assert any(c.from_id == "vpc" and c.to_id == "subnet" for c in suggested_conns)
    
    def test_validate_connections_serverless_pattern(self, advisor):
        """Test serverless pattern validation."""
        components = [
            Component(id="api_gateway", name="API Gateway", type="api_gateway", provider="aws"),
            Component(id="lambda", name="Lambda", type="lambda", provider="aws"),
            Component(id="dynamodb", name="DynamoDB", type="dynamodb", provider="aws"),
        ]
        connections = []
        suggested_conns, warnings = advisor.validate_connections(components, connections)
        assert len(suggested_conns) >= 2
        assert any(c.from_id == "api_gateway" and c.to_id == "lambda" for c in suggested_conns)
        assert any(c.from_id == "lambda" and c.to_id == "dynamodb" for c in suggested_conns)
    
    def test_enhance_spec(self, advisor):
        """Test spec enhancement."""
        spec = ArchitectureSpec(
            title="Test AWS Architecture",
            provider="aws",
            components=[
                Component(id="s3", name="S3", type="s3", provider="aws"),
                Component(id="vpc", name="VPC", type="vpc", provider="aws"),
            ],
            connections=[],
        )
        enhanced = advisor.enhance_spec(spec)
        assert enhanced.metadata.get("enhanced") == True
        assert enhanced.metadata.get("advisor_consulted") == True
        assert "splines" in enhanced.graphviz_attrs.graph_attr
        assert enhanced.graphviz_attrs.graph_attr["splines"] == "ortho"
        assert enhanced.direction == "LR"
    
    def test_get_static_guidance(self, advisor):
        """Test architectural guidance retrieval."""
        guidance = advisor._get_static_guidance()
        assert "AWS Architectural Best Practices" in guidance
        assert "Component Ordering" in guidance
        assert "VPC Network Best Practices" in guidance


class TestAzureArchitecturalAdvisor:
    """Test Azure Architectural Advisor."""
    
    @pytest.fixture
    def advisor(self):
        """Create Azure advisor instance."""
        return AzureArchitecturalAdvisor()
    
    def test_initialization(self, advisor):
        """Test advisor initialization."""
        assert advisor is not None
        assert hasattr(advisor, 'LAYER_ORDER')
        assert hasattr(advisor, 'DEPENDENCIES')
        assert hasattr(advisor, 'PATTERNS')
    
    def test_get_layer_order(self, advisor):
        """Test layer ordering for Azure components."""
        assert advisor.get_layer_order("dns") == 0
        assert advisor.get_layer_order("virtual_network") == 2
        assert advisor.get_layer_order("azure_function") == 5
        assert advisor.get_layer_order("blob_storage") == 7
        assert advisor.get_layer_order("unknown") == 5  # Default to compute layer
    
    def test_sort_components_by_layer(self, advisor):
        """Test component sorting by layer."""
        components = [
            Component(id="blob_storage", name="Blob Storage", type="blob_storage", provider="azure"),
            Component(id="virtual_network", name="Virtual Network", type="virtual_network", provider="azure"),
            Component(id="azure_function", name="Azure Function", type="azure_function", provider="azure"),
        ]
        sorted_components = advisor.sort_components_by_layer(components)
        assert sorted_components[0].get_node_id() == "virtual_network"
        assert sorted_components[1].get_node_id() == "azure_function"
        assert sorted_components[2].get_node_id() == "blob_storage"
    
    def test_suggest_missing_components(self, advisor):
        """Test missing component suggestions."""
        components = [
            Component(id="azure_vm", name="VM", type="azure_vm", provider="azure"),
        ]
        suggestions = advisor.suggest_missing_components(components)
        assert len(suggestions) > 0
        assert any(s["type"] == "virtual_network" for s in suggestions)
    
    def test_validate_connections_vnet_pattern(self, advisor):
        """Test Virtual Network containment pattern."""
        components = [
            Component(id="virtual_network", name="Virtual Network", type="virtual_network", provider="azure"),
            Component(id="azure_vm", name="VM", type="azure_vm", provider="azure"),
        ]
        connections = []
        suggested_conns, warnings = advisor.validate_connections(components, connections)
        assert len(suggested_conns) > 0
        assert any(c.from_id == "virtual_network" and c.to_id == "azure_vm" for c in suggested_conns)
    
    def test_validate_connections_serverless_pattern(self, advisor):
        """Test Azure serverless pattern validation."""
        components = [
            Component(id="api_management", name="API Management", type="api_management", provider="azure"),
            Component(id="azure_function", name="Azure Function", type="azure_function", provider="azure"),
            Component(id="cosmos_db", name="Cosmos DB", type="cosmos_db", provider="azure"),
        ]
        connections = []
        suggested_conns, warnings = advisor.validate_connections(components, connections)
        assert len(suggested_conns) >= 2
        assert any(c.from_id == "api_management" and c.to_id == "azure_function" for c in suggested_conns)
        assert any(c.from_id == "azure_function" and c.to_id == "cosmos_db" for c in suggested_conns)
    
    def test_enhance_spec(self, advisor):
        """Test spec enhancement."""
        spec = ArchitectureSpec(
            title="Test Azure Architecture",
            provider="azure",
            components=[
                Component(id="blob_storage", name="Blob Storage", type="blob_storage", provider="azure"),
                Component(id="virtual_network", name="Virtual Network", type="virtual_network", provider="azure"),
            ],
            connections=[],
        )
        enhanced = advisor.enhance_spec(spec)
        assert enhanced.metadata.get("enhanced") == True
        assert enhanced.metadata.get("advisor_consulted") == True
        assert "splines" in enhanced.graphviz_attrs.graph_attr
        assert enhanced.graphviz_attrs.graph_attr["splines"] == "ortho"
        assert enhanced.direction == "LR"
    
    def test_get_static_guidance(self, advisor):
        """Test architectural guidance retrieval."""
        guidance = advisor._get_static_guidance()
        assert "Azure Architectural Best Practices" in guidance
        assert "Component Ordering" in guidance
        assert "Virtual Network Best Practices" in guidance


class TestGCPArchitecturalAdvisor:
    """Test GCP Architectural Advisor."""
    
    @pytest.fixture
    def advisor(self):
        """Create GCP advisor instance."""
        return GCPArchitecturalAdvisor()
    
    def test_initialization(self, advisor):
        """Test advisor initialization."""
        assert advisor is not None
        assert hasattr(advisor, 'LAYER_ORDER')
        assert hasattr(advisor, 'DEPENDENCIES')
        assert hasattr(advisor, 'PATTERNS')
    
    def test_get_layer_order(self, advisor):
        """Test layer ordering for GCP components."""
        assert advisor.get_layer_order("cloud_dns") == 0
        assert advisor.get_layer_order("vpc") == 2
        assert advisor.get_layer_order("cloud_function") == 5
        assert advisor.get_layer_order("cloud_storage") == 7
        assert advisor.get_layer_order("unknown") == 5  # Default to compute layer
    
    def test_sort_components_by_layer(self, advisor):
        """Test component sorting by layer."""
        components = [
            Component(id="cloud_storage", name="Cloud Storage", type="cloud_storage", provider="gcp"),
            Component(id="vpc", name="VPC", type="vpc", provider="gcp"),
            Component(id="cloud_function", name="Cloud Function", type="cloud_function", provider="gcp"),
        ]
        sorted_components = advisor.sort_components_by_layer(components)
        assert sorted_components[0].get_node_id() == "vpc"
        assert sorted_components[1].get_node_id() == "cloud_function"
        assert sorted_components[2].get_node_id() == "cloud_storage"
    
    def test_suggest_missing_components(self, advisor):
        """Test missing component suggestions."""
        components = [
            Component(id="compute_engine", name="Compute Engine", type="compute_engine", provider="gcp"),
        ]
        suggestions = advisor.suggest_missing_components(components)
        assert len(suggestions) > 0
        assert any(s["type"] == "vpc" for s in suggestions)
    
    def test_validate_connections_vpc_pattern(self, advisor):
        """Test VPC containment pattern."""
        components = [
            Component(id="vpc", name="VPC", type="vpc", provider="gcp"),
            Component(id="compute_engine", name="Compute Engine", type="compute_engine", provider="gcp"),
        ]
        connections = []
        suggested_conns, warnings = advisor.validate_connections(components, connections)
        assert len(suggested_conns) > 0
        assert any(c.from_id == "vpc" and c.to_id == "compute_engine" for c in suggested_conns)
    
    def test_validate_connections_serverless_pattern(self, advisor):
        """Test GCP serverless pattern validation."""
        components = [
            Component(id="api_gateway", name="API Gateway", type="api_gateway", provider="gcp"),
            Component(id="cloud_function", name="Cloud Function", type="cloud_function", provider="gcp"),
            Component(id="firestore", name="Firestore", type="firestore", provider="gcp"),
        ]
        connections = []
        suggested_conns, warnings = advisor.validate_connections(components, connections)
        assert len(suggested_conns) >= 2
        assert any(c.from_id == "api_gateway" and c.to_id == "cloud_function" for c in suggested_conns)
        assert any(c.from_id == "cloud_function" and c.to_id == "firestore" for c in suggested_conns)
    
    def test_enhance_spec(self, advisor):
        """Test spec enhancement."""
        spec = ArchitectureSpec(
            title="Test GCP Architecture",
            provider="gcp",
            components=[
                Component(id="cloud_storage", name="Cloud Storage", type="cloud_storage", provider="gcp"),
                Component(id="vpc", name="VPC", type="vpc", provider="gcp"),
            ],
            connections=[],
        )
        enhanced = advisor.enhance_spec(spec)
        assert enhanced.metadata.get("enhanced") == True
        assert enhanced.metadata.get("advisor_consulted") == True
        assert "splines" in enhanced.graphviz_attrs.graph_attr
        assert enhanced.graphviz_attrs.graph_attr["splines"] == "ortho"
        assert enhanced.direction == "LR"
    
    def test_get_static_guidance(self, advisor):
        """Test architectural guidance retrieval."""
        guidance = advisor._get_static_guidance()
        assert "GCP Architectural Best Practices" in guidance
        assert "Component Ordering" in guidance
        assert "VPC Network Best Practices" in guidance


class TestAdvisorIntegration:
    """Integration tests for advisors with actual diagram generation."""
    
    def test_aws_advisor_orthogonal_routing(self):
        """Test that AWS advisor applies orthogonal routing."""
        advisor = AWSArchitecturalAdvisor()
        spec = ArchitectureSpec(
            title="Test",
            provider="aws",
            components=[
                Component(id="vpc", name="VPC", type="vpc", provider="aws"),
                Component(id="ec2", name="EC2", type="ec2", provider="aws"),
            ],
            connections=[],
        )
        enhanced = advisor.enhance_spec(spec)
        assert enhanced.graphviz_attrs.graph_attr.get("splines") == "ortho"
        assert enhanced.graphviz_attrs.graph_attr.get("overlap") == "false"
    
    def test_azure_advisor_orthogonal_routing(self):
        """Test that Azure advisor applies orthogonal routing."""
        advisor = AzureArchitecturalAdvisor()
        spec = ArchitectureSpec(
            title="Test",
            provider="azure",
            components=[
                Component(id="virtual_network", name="Virtual Network", type="virtual_network", provider="azure"),
                Component(id="azure_vm", name="VM", type="azure_vm", provider="azure"),
            ],
            connections=[],
        )
        enhanced = advisor.enhance_spec(spec)
        assert enhanced.graphviz_attrs.graph_attr.get("splines") == "ortho"
        assert enhanced.graphviz_attrs.graph_attr.get("overlap") == "false"
    
    def test_gcp_advisor_orthogonal_routing(self):
        """Test that GCP advisor applies orthogonal routing."""
        advisor = GCPArchitecturalAdvisor()
        spec = ArchitectureSpec(
            title="Test",
            provider="gcp",
            components=[
                Component(id="vpc", name="VPC", type="vpc", provider="gcp"),
                Component(id="compute_engine", name="Compute Engine", type="compute_engine", provider="gcp"),
            ],
            connections=[],
        )
        enhanced = advisor.enhance_spec(spec)
        assert enhanced.graphviz_attrs.graph_attr.get("splines") == "ortho"
        assert enhanced.graphviz_attrs.graph_attr.get("overlap") == "false"
    
    def test_all_advisors_apply_same_layout(self):
        """Test that all advisors apply consistent layout settings."""
        aws_advisor = AWSArchitecturalAdvisor()
        azure_advisor = AzureArchitecturalAdvisor()
        gcp_advisor = GCPArchitecturalAdvisor()
        
        aws_spec = ArchitectureSpec(
            title="AWS Test",
            provider="aws",
            components=[Component(id="lambda", name="Lambda", type="lambda", provider="aws")],
            connections=[],
        )
        azure_spec = ArchitectureSpec(
            title="Azure Test",
            provider="azure",
            components=[Component(id="azure_function", name="Function", type="azure_function", provider="azure")],
            connections=[],
        )
        gcp_spec = ArchitectureSpec(
            title="GCP Test",
            provider="gcp",
            components=[Component(id="cloud_function", name="Function", type="cloud_function", provider="gcp")],
            connections=[],
        )
        
        aws_enhanced = aws_advisor.enhance_spec(aws_spec)
        azure_enhanced = azure_advisor.enhance_spec(azure_spec)
        gcp_enhanced = gcp_advisor.enhance_spec(gcp_spec)
        
        # All should have orthogonal routing
        assert aws_enhanced.graphviz_attrs.graph_attr.get("splines") == "ortho"
        assert azure_enhanced.graphviz_attrs.graph_attr.get("splines") == "ortho"
        assert gcp_enhanced.graphviz_attrs.graph_attr.get("splines") == "ortho"
        
        # All should have LR direction
        assert aws_enhanced.direction == "LR"
        assert azure_enhanced.direction == "LR"
        assert gcp_enhanced.direction == "LR"
        
        # All should have same spacing
        assert aws_enhanced.graphviz_attrs.graph_attr.get("nodesep") == "1.0"
        assert azure_enhanced.graphviz_attrs.graph_attr.get("nodesep") == "1.0"
        assert gcp_enhanced.graphviz_attrs.graph_attr.get("nodesep") == "1.0"
