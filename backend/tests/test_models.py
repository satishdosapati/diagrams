"""
Tests for models.
"""
import pytest
from src.models.spec import ArchitectureSpec, Component, Connection, NodeType


def test_architecture_spec_creation():
    """Test creating a basic ArchitectureSpec."""
    spec = ArchitectureSpec(
        title="Test Diagram",
        provider="aws",
        components=[
            Component(id="api", name="API Gateway", type=NodeType.APIGATEWAY),
            Component(id="lambda", name="Function", type=NodeType.LAMBDA),
        ],
        connections=[
            Connection(from_id="api", to_id="lambda"),
        ],
    )
    
    assert spec.title == "Test Diagram"
    assert spec.provider == "aws"
    assert len(spec.components) == 2
    assert len(spec.connections) == 1


def test_provider_consistency():
    """Test provider consistency enforcement."""
    spec = ArchitectureSpec(
        title="Test",
        provider="aws",
        components=[
            Component(id="api", name="API", type=NodeType.APIGATEWAY, provider="aws"),
        ],
    )
    
    # Should not raise error
    assert spec.provider == "aws"
    assert spec.components[0].provider == "aws"

