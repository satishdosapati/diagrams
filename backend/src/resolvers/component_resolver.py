"""
ComponentResolver - Maps components to provider-specific Diagrams classes.
Uses library-first discovery as source of truth.
"""
from typing import Dict, Optional, Tuple, Set
import importlib
import inspect
import logging

from ..models.spec import Component, NodeType
from ..models.node_registry import get_registry
from .intelligent_resolver import IntelligentNodeResolver
from .library_discovery import LibraryDiscovery

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
        
        # Initialize library discovery (source of truth)
        self.discovery = LibraryDiscovery(primary_provider)
        
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
        Resolve component to Diagrams class using library-first approach.
        
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
            # Get available providers from registry
            available_providers = list(self.registry._registry.get("providers", {}).keys())
            if not available_providers:
                available_providers = ["aws", "azure", "gcp"]  # Fallback
            raise ValueError(
                f"Unsupported provider: '{provider}'. "
                f"Available providers: {', '.join(available_providers)}"
            )
        
        # Get node type as string (NodeType enum value or direct string)
        node_id = component.get_node_id()
        logger.debug(f"[RESOLVER] Resolving component: id={component.id}, name={component.name}, node_id={node_id}, provider={provider}")
        
        # Provider-specific fallbacks for components that don't exist in certain providers
        # GCP doesn't have separate subnet components (subnets are part of VPC)
        if provider == "gcp" and node_id.lower() in ["subnet", "subnets", "public_subnet", "private_subnet"]:
            logger.info(f"[RESOLVER] Mapping '{node_id}' to 'vpc' for GCP (subnets are part of VPC)")
            node_id = "vpc"
        
        # STEP 1: Try library discovery first (source of truth)
        # Get category hint from registry if available
        category_hint = None
        registry_mapping = self.registry.get_node_mapping(provider, node_id)
        if registry_mapping:
            category_hint = registry_mapping[0]  # category
        
        # Search library for matching class
        logger.debug(f"[RESOLVER] Searching library for node_id={node_id}, category_hint={category_hint}, provider={provider}")
        library_match = self.discovery.find_class(node_id, category_hint)
        
        if library_match:
            module_path, class_name = library_match
            logger.info(f"[RESOLVER] Found '{class_name}' in library for '{node_id}'")
            
            # Import and return
            try:
                module = importlib.import_module(module_path)
                node_class = getattr(module, class_name)
                logger.debug(f"[RESOLVER] Successfully resolved {provider}.{node_id} -> {module_path}.{class_name}")
                return node_class
            except (ImportError, AttributeError) as e:
                logger.error(f"[RESOLVER] Failed to import {class_name} from {module_path}: {e}", exc_info=True)
                logger.error(f"[RESOLVER] Component details: id={component.id}, name={component.name}, node_id={node_id}, provider={provider}")
                # Fall through to registry fallback
        
        # STEP 2: Try intelligent resolution (for ambiguous terms)
        ambiguous_terms = {"subnet", "database", "db", "function", "compute", "storage"}
        needs_intelligent_resolution = (
            node_id.lower() in ambiguous_terms or
            component.name  # Always try intelligent resolution if component name is available
        )
        
        resolved_id = None
        if needs_intelligent_resolution or not registry_mapping:
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
                # Try library discovery again with resolved ID
                library_match = self.discovery.find_class(resolved_id)
                if library_match:
                    module_path, class_name = library_match
                    module = importlib.import_module(module_path)
                    return getattr(module, class_name)
                # Update node_id for registry lookup
                node_id = resolved_id
                registry_mapping = self.registry.get_node_mapping(provider, node_id)
        
        # STEP 3: Registry fallback with validation
        if registry_mapping:
            category, class_name = registry_mapping
            module_path = self._get_module_path(provider, category)
            
            # Validate class exists before using
            available_classes = self.discovery.discover_module_classes(module_path)
            
            if class_name in available_classes:
                # Registry class exists - use it
                logger.info(f"Using registry mapping: {class_name}")
                module = importlib.import_module(module_path)
                node_class = getattr(module, class_name)
                logger.debug(f"Resolved {provider}.{node_id} -> {module_path}.{class_name}")
                return node_class
            else:
                # Class not found in discovery - try direct import as fallback
                # This handles cases where discovery misses classes (e.g., imported from parent module)
                logger.debug(f"[RESOLVER] Class '{class_name}' not in discovered classes, trying direct import")
                try:
                    module = importlib.import_module(module_path)
                    if hasattr(module, class_name):
                        node_class = getattr(module, class_name)
                        if inspect.isclass(node_class):
                            logger.info(f"[RESOLVER] Found '{class_name}' via direct import (not in discovery cache)")
                            logger.debug(f"Resolved {provider}.{node_id} -> {module_path}.{class_name}")
                            return node_class
                except (ImportError, AttributeError) as import_error:
                    logger.debug(f"[RESOLVER] Direct import failed: {import_error}")
                
                # Registry class doesn't exist - provide helpful error
                logger.error(f"[RESOLVER] Registry class '{class_name}' not found in module '{module_path}'")
                logger.error(f"[RESOLVER] Component: id={component.id}, name={component.name}, node_id={node_id}, provider={provider}")
                logger.error(f"[RESOLVER] Available classes in module: {list(available_classes)[:10]}")
                similar_classes = self.discovery.find_similar_classes(
                    class_name, available_classes
                )
                error_msg = self._build_class_not_found_error(
                    provider, node_id, module_path, class_name,
                    available_classes, similar_classes
                )
                logger.error(f"[RESOLVER] Error message: {error_msg}")
                raise ValueError(error_msg)
        
        # STEP 4: Comprehensive error with suggestions
        logger.error(f"[RESOLVER] FAILED to resolve component: id={component.id}, name={component.name}, node_id={node_id}, provider={provider}")
        logger.error(f"[RESOLVER] Tried library discovery: {library_match is not None}")
        logger.error(f"[RESOLVER] Tried intelligent resolution: {resolved_id if 'resolved_id' in locals() else 'N/A'}")
        logger.error(f"[RESOLVER] Registry mapping exists: {registry_mapping is not None}")
        error_msg = self._build_comprehensive_error(provider, node_id, component.name)
        logger.error(f"[RESOLVER] Error message: {error_msg}")
        raise ValueError(error_msg)
    
    def _build_class_not_found_error(
        self, provider: str, node_id: str, module_path: str, expected_class: str,
        available_classes: Set[str], similar_classes: list[str]
    ) -> str:
        """Build detailed error when registry class doesn't exist."""
        error_parts = [
            f"Class '{expected_class}' not found in {module_path} for {provider}.{node_id}."
        ]
        
        if similar_classes:
            error_parts.append(
                f"\nDid you mean: {', '.join(similar_classes[:3])}?"
                )
        
        sorted_classes = sorted(available_classes)
        error_parts.append(
            f"\nAvailable classes in {module_path}: "
            f"{', '.join(sorted_classes[:10])}"
        )
        
        if len(available_classes) > 10:
            error_parts.append(f" (and {len(available_classes) - 10} more)")
        
        return "".join(error_parts)
    
    def _build_comprehensive_error(self, provider: str, node_id: str, component_name: Optional[str]) -> str:
        """Build comprehensive error with suggestions from all sources."""
        error_parts = [
            f"Could not resolve component type '{node_id}' for provider '{provider}'."
        ]
        
        if component_name:
            error_parts.append(f"\nComponent name: '{component_name}'")
        
        # Get suggestions from intelligent resolver
        registry_suggestions = self.intelligent_resolver.get_suggestions(node_id, limit=5)
        
        # Get suggestions from library discovery
        library_suggestions = self._get_library_suggestions(node_id, provider)
        
        # Combine suggestions
        all_suggestions = []
        if registry_suggestions:
            all_suggestions.extend([
                f"'{s[0]}' (registry, {s[1]:.0%})" 
                for s in registry_suggestions[:3]
            ])
        if library_suggestions:
            all_suggestions.extend([
                f"'{s}' (library)" for s in library_suggestions[:3]
            ])
        
        if all_suggestions:
            error_parts.append(f"\nSuggestions: {', '.join(all_suggestions)}")
        
        # Show available classes by category
        available_by_category = self._get_available_by_category(provider)
        if available_by_category:
            error_parts.append("\n\nAvailable classes by category:")
            for category, classes in available_by_category.items():
                if classes:
                    sorted_classes = sorted(classes)
                    error_parts.append(
                        f"  {category}: {', '.join(sorted_classes[:5])}"
                    )
                    if len(classes) > 5:
                        error_parts.append(f" (and {len(classes) - 5} more)")
        
        return "".join(error_parts)
    
    def _get_library_suggestions(self, node_id: str, provider: str) -> list[str]:
        """Get suggestions from library discovery."""
        suggestions = []
        all_classes = self.discovery.get_all_available_classes()
        
        normalized_input = self.discovery._normalize_input(node_id)
        
        for module_path, classes in all_classes.items():
            for cls in classes:
                cls_lower = cls.lower()
                if normalized_input in cls_lower or cls_lower in normalized_input:
                    suggestions.append(cls)
        
        return suggestions[:5]
    
    def _get_available_by_category(self, provider: str) -> Dict[str, Set[str]]:
        """Get available classes organized by category."""
        result = {}
        modules = self.registry.get_provider_modules(provider)
        
        for category, module_path in modules.items():
            classes = self.discovery.discover_module_classes(module_path)
            if classes:
                result[category] = classes
        
        return result

