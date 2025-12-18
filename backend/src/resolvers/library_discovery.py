"""
Library Discovery - Discovers available classes from diagrams library at runtime.
Uses the actual installed library as source of truth.
"""
import importlib
import inspect
import re
import logging
from typing import Dict, Set, Optional, Tuple
from functools import lru_cache
from difflib import get_close_matches

logger = logging.getLogger(__name__)


class LibraryDiscovery:
    """
    Discovers and caches available classes from diagrams library.
    Uses introspection to find what's actually available.
    """
    
    def __init__(self, provider: str):
        """
        Initialize discovery for a provider.
        
        Args:
            provider: Provider name (aws, azure, gcp)
        """
        self.provider = provider
        self._class_cache: Dict[str, Set[str]] = {}  # module_path -> set of class names
        
        # Known module categories (from registry or docs)
        self.module_categories = self._get_module_categories()
        
        # Build discovery cache on init
        self._discover_all_modules()
    
    def _get_module_categories(self) -> Dict[str, str]:
        """Get module categories for the provider."""
        base_modules = {
            "aws": {
                "compute": "diagrams.aws.compute",
                "storage": "diagrams.aws.storage",
                "database": "diagrams.aws.database",
                "network": "diagrams.aws.network",
                "integration": "diagrams.aws.integration",
                "analytics": "diagrams.aws.analytics",
                "security": "diagrams.aws.security",
                "management": "diagrams.aws.management",
                "iot": "diagrams.aws.iot",
                "ml": "diagrams.aws.ml",
                "ar": "diagrams.aws.ar",
                "blockchain": "diagrams.aws.blockchain",
                "business": "diagrams.aws.business",
                "cost": "diagrams.aws.cost",
                "devtools": "diagrams.aws.devtools",
                "enablement": "diagrams.aws.enablement",
                "enduser": "diagrams.aws.enduser",
                "engagement": "diagrams.aws.engagement",
                "game": "diagrams.aws.game",
                "general": "diagrams.aws.general",
                "media": "diagrams.aws.media",
                "migration": "diagrams.aws.migration",
                "mobile": "diagrams.aws.mobile",
                "quantum": "diagrams.aws.quantum",
                "robotics": "diagrams.aws.robotics",
                "satellite": "diagrams.aws.satellite",
            },
            "azure": {
                "compute": "diagrams.azure.compute",
                "storage": "diagrams.azure.storage",
                "database": "diagrams.azure.database",
                "network": "diagrams.azure.network",
                "integration": "diagrams.azure.integration",
                "security": "diagrams.azure.security",
                "management": "diagrams.azure.management",
                "analytics": "diagrams.azure.analytics",
                "iot": "diagrams.azure.iot",
                "ml": "diagrams.azure.ml",
            },
            "gcp": {
                "compute": "diagrams.gcp.compute",
                "storage": "diagrams.gcp.storage",
                "database": "diagrams.gcp.database",
                "network": "diagrams.gcp.network",
                "integration": "diagrams.gcp.integration",
                "security": "diagrams.gcp.security",
                "management": "diagrams.gcp.management",
                "analytics": "diagrams.gcp.analytics",
                "iot": "diagrams.gcp.iot",
                "ml": "diagrams.gcp.ml",
            },
        }
        return base_modules.get(self.provider, {})
    
    def _discover_all_modules(self):
        """Discover all available classes across all modules."""
        for category, module_path in self.module_categories.items():
            try:
                classes = self.discover_module_classes(module_path)
                self._class_cache[module_path] = classes
                logger.debug(f"Discovered {len(classes)} classes in {module_path}")
            except ImportError as e:
                logger.warning(f"Module {module_path} not available: {e}")
            except Exception as e:
                logger.warning(f"Error discovering {module_path}: {e}")
    
    @lru_cache(maxsize=128)
    def discover_module_classes(self, module_path: str) -> Set[str]:
        """
        Discover all available classes in a module.
        
        Args:
            module_path: Full module path (e.g., "diagrams.aws.network")
            
        Returns:
            Set of available class names
        """
        try:
            module = importlib.import_module(module_path)
            
            # Find all classes (not starting with _)
            classes = set()
            for name in dir(module):
                if name.startswith("_"):
                    continue
                
                try:
                    obj = getattr(module, name)
                    # Check if it's a class and is defined in this module
                    if inspect.isclass(obj):
                        # Check if it's from this module (not imported)
                        if hasattr(obj, '__module__') and obj.__module__ == module_path:
                            classes.add(name)
                        # Also include if it's a re-exported class (common pattern)
                        elif hasattr(obj, '__module__') and module_path in obj.__module__:
                            classes.add(name)
                except Exception as e:
                    logger.debug(f"Error checking {name} in {module_path}: {e}")
                    continue
            
            return classes
            
        except ImportError as e:
            logger.error(f"Failed to import module {module_path}: {e}")
            return set()
        except Exception as e:
            logger.error(f"Error discovering classes in {module_path}: {e}")
            return set()
    
    def find_class(self, user_input: str, category_hint: Optional[str] = None) -> Optional[Tuple[str, str]]:
        """
        Find a class matching user input from available classes.
        
        Args:
            user_input: User-provided input (e.g., "ALB", "Application Load Balancer")
            category_hint: Optional category hint (e.g., "network")
            
        Returns:
            Tuple of (module_path, class_name) or None if not found
        """
        # Normalize user input
        normalized_input = self._normalize_input(user_input)
        
        # If category hint provided, search in that module first
        if category_hint and category_hint in self.module_categories:
            module_path = self.module_categories[category_hint]
            match = self._search_in_module(module_path, normalized_input, user_input)
            if match:
                return (module_path, match)
        
        # Search all modules
        for module_path, classes in self._class_cache.items():
            match = self._search_in_module(module_path, normalized_input, user_input, classes)
            if match:
                return (module_path, match)
        
        return None
    
    def _search_in_module(self, module_path: str, normalized_input: str, 
                         original_input: str, classes: Optional[Set[str]] = None) -> Optional[str]:
        """
        Search for matching class in a module.
        
        Args:
            module_path: Module to search
            normalized_input: Normalized user input
            original_input: Original user input
            classes: Optional pre-discovered classes (if None, will discover)
            
        Returns:
            Matching class name or None
        """
        if classes is None:
            classes = self.discover_module_classes(module_path)
        
        # 1. Exact match (case-insensitive)
        for cls_name in classes:
            if cls_name.lower() == normalized_input:
                return cls_name
        
        # 2. Normalized match (remove underscores, hyphens)
        normalized_classes = {self._normalize_input(c): c for c in classes}
        if normalized_input in normalized_classes:
            return normalized_classes[normalized_input]
        
        # 3. Partial match (contains)
        for cls_name in classes:
            cls_lower = cls_name.lower()
            if normalized_input in cls_lower or cls_lower in normalized_input:
                return cls_name
        
        # 4. Fuzzy match (similarity)
        matches = get_close_matches(normalized_input, [c.lower() for c in classes], n=1, cutoff=0.6)
        if matches:
            # Find original case
            for cls_name in classes:
                if cls_name.lower() == matches[0]:
                    return cls_name
        
        return None
    
    def _normalize_input(self, text: str) -> str:
        """Normalize input for matching."""
        # Remove special chars, convert to lowercase
        normalized = re.sub(r'[_\-\s]+', '', text.lower())
        # Remove common prefixes
        normalized = re.sub(r'^(aws|amazon|azure|gcp|google|microsoft)\s*', '', normalized)
        return normalized
    
    def get_all_available_classes(self) -> Dict[str, Set[str]]:
        """Get all discovered classes organized by module."""
        return self._class_cache.copy()
    
    def get_classes_for_category(self, category: str) -> Set[str]:
        """Get all classes for a specific category."""
        if category not in self.module_categories:
            return set()
        module_path = self.module_categories[category]
        return self._class_cache.get(module_path, set())
    
    def find_similar_classes(self, target_class: str, available_classes: Set[str], limit: int = 3) -> list[str]:
        """Find similar class names using fuzzy matching."""
        matches = get_close_matches(
            target_class.lower(),
            [c.lower() for c in available_classes],
            n=limit,
            cutoff=0.6
        )
        # Return original case
        result = []
        for match in matches:
            for cls in available_classes:
                if cls.lower() == match:
                    result.append(cls)
                    break
        return result

