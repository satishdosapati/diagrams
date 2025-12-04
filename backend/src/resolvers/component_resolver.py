"""
ComponentResolver - Maps components to provider-specific Diagrams classes.
"""
from typing import Dict, Optional
import importlib

from ..models.spec import Component, NodeType


class ComponentResolver:
    """Resolves component types to actual Diagrams library classes."""
    
    def __init__(self, primary_provider: str):
        """
        Initialize resolver with primary provider.
        
        Args:
            primary_provider: Primary provider (aws, azure, gcp)
        """
        self.primary_provider = primary_provider
        self.provider_modules = {
            "aws": "diagrams.aws",
            "azure": "diagrams.azure",
            "gcp": "diagrams.gcp",
        }
        
        # Map node types to (category, class_name) for each provider
        self.node_mappings = {
            "aws": {
                NodeType.EC2: ("compute", "EC2"),
                NodeType.LAMBDA: ("compute", "Lambda"),
                NodeType.ECS: ("compute", "ECS"),
                NodeType.S3: ("storage", "S3"),
                NodeType.DYNAMODB: ("database", "DynamoDB"),
                NodeType.RDS: ("database", "RDS"),
                NodeType.APIGATEWAY: ("network", "APIGateway"),
                NodeType.ELB: ("network", "ELB"),
                NodeType.CLOUDFRONT: ("network", "CloudFront"),
                NodeType.SQS: ("integration", "SQS"),
                NodeType.SNS: ("integration", "SNS"),
            },
            "azure": {
                NodeType.AZURE_FUNCTION: ("compute", "Function"),
                NodeType.AZURE_VM: ("compute", "VM"),
                NodeType.BLOB_STORAGE: ("storage", "BlobStorage"),
                NodeType.COSMOS_DB: ("database", "CosmosDb"),
            },
            "gcp": {
                NodeType.CLOUD_FUNCTION: ("compute", "CloudFunctions"),
                NodeType.COMPUTE_ENGINE: ("compute", "ComputeEngine"),
                NodeType.CLOUD_STORAGE: ("storage", "GCS"),
                NodeType.FIRESTORE: ("database", "Firestore"),
            },
        }
    
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
        
        # Get mapping for provider
        provider_mapping = self.node_mappings.get(provider)
        if not provider_mapping:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Get node mapping
        node_mapping = provider_mapping.get(component.type)
        if not node_mapping:
            raise ValueError(
                f"Node type {component.type} not supported for provider {provider}"
            )
        
        category, class_name = node_mapping
        module_path = self.provider_modules[provider]
        
        # Dynamic import
        try:
            module = importlib.import_module(f"{module_path}.{category}")
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(
                f"Failed to import {module_path}.{category}.{class_name}: {e}"
            )

