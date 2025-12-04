"""
Node Registry - Loads and manages node type mappings from configuration file.
"""
import yaml
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class NodeRegistry:
    """Manages node type mappings loaded from configuration files."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize registry from configuration files.
        
        Args:
            config_dir: Path to config directory. If None, uses default location.
        """
        if config_dir is None:
            # Default to backend/config directory
            backend_dir = Path(__file__).parent.parent.parent
            config_dir = backend_dir / "config"
        
        self.config_dir = Path(config_dir)
        self._registry: Dict = {"providers": {}}
        self._load_registry()
    
    def _load_registry(self):
        """Load registry from YAML configuration files."""
        try:
            if not self.config_dir.exists():
                error_msg = (
                    f"Config directory not found: {self.config_dir}\n"
                    f"Please ensure the config directory exists. Expected location: backend/config"
                )
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # Try loading from separate provider files first
            provider_files = {
                "aws": self.config_dir / "aws_nodes.yaml",
                "azure": self.config_dir / "azure_nodes.yaml",
                "gcp": self.config_dir / "gcp_nodes.yaml",
            }
            
            # Check if provider-specific files exist
            has_provider_files = any(f.exists() for f in provider_files.values())
            
            if has_provider_files:
                # Load from separate provider files
                self._load_from_provider_files(provider_files)
            else:
                # Fall back to single node_registry.yaml (backward compatibility)
                legacy_file = self.config_dir / "node_registry.yaml"
                if legacy_file.exists():
                    logger.info(f"Loading from legacy single file: {legacy_file}")
                    self._load_from_legacy_file(legacy_file)
                else:
                    raise FileNotFoundError(
                        f"No config files found. Expected either:\n"
                        f"  - Separate files: {', '.join(str(f) for f in provider_files.values())}\n"
                        f"  - Legacy file: {legacy_file}"
                    )
            
            if not self._registry.get("providers"):
                raise ValueError("No providers loaded from config files")
            
            logger.info(
                f"Loaded node registry with {len(self._registry['providers'])} providers: "
                f"{', '.join(self._registry['providers'].keys())}"
            )
            self._validate_registry()
            
        except yaml.YAMLError as e:
            error_msg = f"Failed to parse YAML in config file: {e}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg) from e
        except Exception as e:
            logger.error(f"Failed to load node registry: {e}", exc_info=True)
            raise
    
    def _load_from_provider_files(self, provider_files: Dict[str, Path]):
        """Load registry from separate provider-specific files."""
        for provider, file_path in provider_files.items():
            if not file_path.exists():
                logger.warning(f"Provider file not found: {file_path}, skipping {provider}")
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    provider_config = yaml.safe_load(f)
                
                if not provider_config:
                    logger.warning(f"Provider file {file_path} is empty, skipping {provider}")
                    continue
                
                # Validate structure
                if "modules" not in provider_config:
                    raise ValueError(f"Provider file {file_path} missing 'modules' key")
                if "nodes" not in provider_config:
                    raise ValueError(f"Provider file {file_path} missing 'nodes' key")
                
                # Add to registry
                self._registry["providers"][provider] = {
                    "modules": provider_config["modules"],
                    "nodes": provider_config["nodes"]
                }
                
                node_count = len(provider_config.get("nodes", {}))
                logger.info(f"Loaded {node_count} nodes for {provider} from {file_path.name}")
                
            except Exception as e:
                logger.error(f"Failed to load {provider} config from {file_path}: {e}", exc_info=True)
                raise
    
    def _load_from_legacy_file(self, file_path: Path):
        """Load registry from legacy single file format."""
        with open(file_path, 'r', encoding='utf-8') as f:
            self._registry = yaml.safe_load(f)
        
        if not self._registry:
            raise ValueError("Legacy registry file is empty or invalid YAML")
        
        if "providers" not in self._registry:
            raise ValueError(
                "Invalid legacy registry format: missing 'providers' key. "
                "Expected structure: {providers: {aws: {...}, azure: {...}, gcp: {...}}}"
            )
    
    def _validate_registry(self):
        """Validate registry structure."""
        providers = self._registry["providers"]
        
        if not providers:
            raise ValueError("Registry has no providers defined")
        
        for provider, config in providers.items():
            if not isinstance(config, dict):
                raise ValueError(
                    f"Provider '{provider}' config must be a dictionary, got {type(config)}"
                )
            
            if "modules" not in config:
                raise ValueError(
                    f"Provider '{provider}' missing 'modules' key. "
                    "Expected: {modules: {compute: '...', storage: '...', ...}}"
                )
            
            if "nodes" not in config:
                raise ValueError(
                    f"Provider '{provider}' missing 'nodes' key. "
                    "Expected: {nodes: {node_id: {category: '...', class_name: '...'}}}"
                )
            
            if not isinstance(config["nodes"], dict):
                raise ValueError(
                    f"Provider '{provider}' 'nodes' must be a dictionary, got {type(config['nodes'])}"
                )
            
            if not config["nodes"]:
                logger.warning(f"Provider '{provider}' has no nodes defined")
            
            # Validate each node has required fields
            for node_id, node_config in config["nodes"].items():
                if not isinstance(node_config, dict):
                    raise ValueError(
                        f"Node '{node_id}' in provider '{provider}' must be a dictionary, "
                        f"got {type(node_config)}"
                    )
                
                if "category" not in node_config:
                    raise ValueError(
                        f"Node '{node_id}' in provider '{provider}' missing 'category' field. "
                        f"Expected: {{category: 'compute', class_name: 'EC2', ...}}"
                    )
                
                if "class_name" not in node_config:
                    raise ValueError(
                        f"Node '{node_id}' in provider '{provider}' missing 'class_name' field. "
                        f"Expected: {{category: 'compute', class_name: 'EC2', ...}}"
                    )
                
                # Validate category exists in modules
                category = node_config["category"]
                if category not in config["modules"]:
                    logger.warning(
                        f"Node '{node_id}' in provider '{provider}' uses category '{category}' "
                        f"which is not in modules. Available modules: {list(config['modules'].keys())}"
                    )
        
        logger.info("Registry validation passed")
    
    def get_provider_modules(self, provider: str) -> Dict[str, str]:
        """
        Get module mappings for a provider.
        
        Args:
            provider: Provider name (aws, azure, gcp)
            
        Returns:
            Dictionary mapping category names to module paths
        """
        if provider not in self._registry["providers"]:
            raise ValueError(f"Unknown provider: {provider}")
        
        return self._registry["providers"][provider]["modules"]
    
    def get_node_mapping(
        self, provider: str, node_id: str
    ) -> Optional[Tuple[str, str]]:
        """
        Get mapping for a specific node.
        
        Args:
            provider: Provider name (aws, azure, gcp)
            node_id: Node identifier (e.g., 'ec2', 'lambda')
            
        Returns:
            Tuple of (category, class_name) or None if not found
        """
        if provider not in self._registry["providers"]:
            return None
        
        nodes = self._registry["providers"][provider]["nodes"]
        if node_id not in nodes:
            return None
        
        node_config = nodes[node_id]
        return (node_config["category"], node_config["class_name"])
    
    def get_all_nodes(self, provider: str) -> Dict[str, Dict]:
        """
        Get all nodes for a provider.
        
        Args:
            provider: Provider name (aws, azure, gcp)
            
        Returns:
            Dictionary of node_id -> node_config
        """
        if provider not in self._registry["providers"]:
            return {}
        
        return self._registry["providers"][provider]["nodes"]
    
    def get_node_list(self, provider: str) -> list[str]:
        """
        Get list of all node IDs for a provider.
        
        Args:
            provider: Provider name (aws, azure, gcp)
            
        Returns:
            List of node identifiers
        """
        nodes = self.get_all_nodes(provider)
        return sorted(nodes.keys())
    
    def get_node_description(self, provider: str, node_id: str) -> Optional[str]:
        """
        Get description for a node.
        
        Args:
            provider: Provider name
            node_id: Node identifier
            
        Returns:
            Description string or None
        """
        nodes = self.get_all_nodes(provider)
        if node_id not in nodes:
            return None
        
        return nodes[node_id].get("description")
    
    def is_provider_supported(self, provider: str) -> bool:
        """Check if provider is supported."""
        return provider in self._registry.get("providers", {})


# Global registry instance (lazy-loaded)
_registry_instance: Optional[NodeRegistry] = None


def get_registry() -> NodeRegistry:
    """Get global registry instance (singleton pattern)."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = NodeRegistry()
    return _registry_instance

