"""
Tests for component resolver.
"""
import pytest
from src.resolvers.component_resolver import ComponentResolver
from src.models.spec import Component, NodeType


def test_resolve_aws_component():
    """Test resolving AWS component."""
    resolver = ComponentResolver(primary_provider="aws")
    comp = Component(id="lambda", name="Function", type=NodeType.LAMBDA)
    
    node_class = resolver.resolve_component_class(comp)
    assert node_class is not None
    assert "Lambda" in node_class.__name__


def test_resolve_azure_component():
    """Test resolving Azure component."""
    resolver = ComponentResolver(primary_provider="azure")
    comp = Component(id="func", name="Function", type=NodeType.AZURE_FUNCTION)
    
    node_class = resolver.resolve_component_class(comp)
    assert node_class is not None

