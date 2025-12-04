"""
ComponentResolver - Maps components to provider-specific Diagrams classes.
"""
from typing import Dict, Optional
import importlib
import logging

from ..models.spec import Component, NodeType
from ..models.node_registry import get_registry
from .intelligent_resolver import IntelligentNodeResolver

logger = logging.getLogger(__name__)


class ComponentResolver:
    """Resolves component types to actual Diagrams library classes."""
    
    def __init__(self, primary_provider: str):
        """
        Initialize resolver with primary provider.
        
        Args:
            primary_provider: Primary provider (aws, azure, gcp)
        """
        self.primary_provider = primary_provider
        self.registry = get_registry()
        
        # Base module paths (fallback if registry doesn't have module info)
        self.provider_modules_base = {
            "aws": "diagrams.aws",
            "azure": "diagrams.azure",
            "gcp": "diagrams.gcp",
        }
        
        # Load provider modules from registry
        try:
            self.provider_modules = self.registry.get_provider_modules(primary_provider)
        except Exception as e:
            logger.warning(f"Failed to load modules from registry: {e}, using defaults")
            self.provider_modules = {}
        
        # Initialize intelligent resolver for fuzzy matching
        self.intelligent_resolver = IntelligentNodeResolver(primary_provider)
    
    def _get_module_path(self, provider: str, category: str) -> str:
        """
        Get full module path for a provider category.
        
        Args:
            provider: Provider name
            category: Category name (compute, storage, etc.)
            
        Returns:
            Full module path (e.g., "diagrams.aws.compute")
        """
        # Try registry first
        if provider in self.provider_modules_base:
            base = self.provider_modules_base[provider]
            if category in self.provider_modules:
                return self.provider_modules[category]
            # Fallback to base.category
            return f"{base}.{category}"
        
        raise ValueError(f"Unknown provider: {provider}")
    
    def resolve_component_class(self, component: Component):
        """
        Resolve component to Diagrams class.
        
        Args:
            component: Component to resolve
            
        Returns:
            Diagrams class for the component
        """
        provider = component.provider or self.primary_provider
        
        # Enforce provider consistency
        if not component.provider and provider != self.primary_provider:
            raise ValueError(
                f"Cannot use {provider} component in {self.primary_provider} diagram. "
                "Use is_multi_cloud=True for multi-cloud architectures."
            )
        
        # Check if provider is supported
        if not self.registry.is_provider_supported(provider):
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Get node type as string (NodeType enum value or direct string)
        node_id = component.get_node_id()
        
        # Check if this is an ambiguous term that needs intelligent resolution
        # Even if exact match exists, use context to resolve to more specific type
        ambiguous_terms = {"subnet", "database", "db", "function", "compute", "storage"}
        needs_intelligent_resolution = (
            node_id.lower() in ambiguous_terms or
            component.name  # Always try intelligent resolution if component name is available
        )
        
        # Try intelligent resolution first for ambiguous terms or when context is available
        resolved_id = None
        if needs_intelligent_resolution:
            resolved_id = self.intelligent_resolver.resolve(
                node_id=node_id,
                component_name=component.name,
                context={"provider": provider}
            )
            
            if resolved_id and resolved_id != node_id:
                logger.info(
                    f"Intelligently resolved '{node_id}' to '{resolved_id}' "
                    f"for component '{component.name}'"
                )
                node_id = resolved_id
        
        # Try exact match (or resolved_id match)
        node_mapping = self.registry.get_node_mapping(provider, node_id)
        
        # If still not found and we didn't try intelligent resolution yet, try it now
        if not node_mapping and not needs_intelligent_resolution:
            resolved_id = self.intelligent_resolver.resolve(
                node_id=node_id,
                component_name=component.name,
                context={"provider": provider}
            )
            
            if resolved_id:
                logger.info(
                    f"Intelligently resolved '{node_id}' to '{resolved_id}' "
                    f"for component '{component.name}'"
                )
                node_id = resolved_id
                node_mapping = self.registry.get_node_mapping(provider, node_id)
        
        # If still not found, provide helpful error with suggestions
        if not node_mapping:
            suggestions = self.intelligent_resolver.get_suggestions(node_id, limit=5)
            suggestion_text = ""
            if suggestions:
                suggestion_list = ", ".join(
                    f"'{s[0]}' ({s[1]:.0%})" for s in suggestions[:3]
                )
                suggestion_text = f"\nDid you mean: {suggestion_list}?"
            
            raise ValueError(
                f"Node type '{node_id}' not supported for provider '{provider}'. "
                f"Available nodes: {', '.join(self.registry.get_node_list(provider)[:10])}..."
                + suggestion_text
            )
        
        category, class_name = node_mapping
        
        # Get module path
        module_path = self._get_module_path(provider, category)
        
        # Dynamic import
        try:
            module = importlib.import_module(module_path)
            node_class = getattr(module, class_name)
            logger.debug(
                f"Resolved {provider}.{node_id} -> {module_path}.{class_name}"
            )
            return node_class
        except (ImportError, AttributeError) as e:
            raise ValueError(
                f"Failed to import {module_path}.{class_name} for {provider}.{node_id}: {e}"
            )

