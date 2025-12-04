"""
ArchitectureSpec model with multi-provider support (AWS, Azure, GCP).
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Literal
from enum import Enum


class NodeType(str, Enum):
    """Multi-provider node types."""
    # AWS
    EC2 = "ec2"
    LAMBDA = "lambda"
    S3 = "s3"
    DYNAMODB = "dynamodb"
    RDS = "rds"
    APIGATEWAY = "api_gateway"
    ELB = "elb"
    ECS = "ecs"
    CLOUDFRONT = "cloudfront"
    SQS = "sqs"
    SNS = "sns"
    # Azure
    AZURE_FUNCTION = "azure_function"
    AZURE_VM = "azure_vm"
    BLOB_STORAGE = "blob_storage"
    COSMOS_DB = "cosmos_db"
    # GCP
    CLOUD_FUNCTION = "cloud_function"
    COMPUTE_ENGINE = "compute_engine"
    CLOUD_STORAGE = "cloud_storage"
    FIRESTORE = "firestore"


class Component(BaseModel):
    """Represents a component in the architecture."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Display name")
    type: NodeType = Field(..., description="Component type")
    provider: Optional[str] = Field(None, description="Cloud provider (inherits from spec if not set)")
    metadata: dict = Field(default_factory=dict, description="Additional properties")


class Connection(BaseModel):
    """Represents a connection between components."""
    from_id: str = Field(..., description="Source component ID")
    to_id: str = Field(..., description="Target component ID")
    label: Optional[str] = Field(None, description="Connection label")


class ArchitectureSpec(BaseModel):
    """Architecture specification with provider support."""
    title: str = Field(..., description="Diagram title")
    provider: Literal["aws", "azure", "gcp"] = Field(default="aws", description="Cloud provider")
    is_multi_cloud: bool = Field(default=False, description="Allow multiple providers")
    components: List[Component] = Field(default_factory=list, description="Architecture components")
    connections: List[Connection] = Field(default_factory=list, description="Component connections")
    metadata: dict = Field(default_factory=dict, description="Additional metadata (diagram_type, etc.)")
    
    @model_validator(mode='after')
    def enforce_provider_consistency(self):
        """Ensure all components use the same provider unless multi-cloud."""
        if self.is_multi_cloud:
            return self
        
        # Set provider on all components
        for comp in self.components:
            if comp.provider and comp.provider != self.provider:
                raise ValueError(
                    f"Component '{comp.name}' uses provider '{comp.provider}' "
                    f"but diagram provider is '{self.provider}'. "
                    "Set is_multi_cloud=True for multi-cloud diagrams."
                )
            comp.provider = self.provider
        
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Serverless API",
                "provider": "aws",
                "components": [
                    {"id": "api", "name": "API Gateway", "type": "api_gateway"},
                    {"id": "lambda", "name": "Function", "type": "lambda"},
                    {"id": "db", "name": "Database", "type": "dynamodb"}
                ],
                "connections": [
                    {"from_id": "api", "to_id": "lambda"},
                    {"from_id": "lambda", "to_id": "db"}
                ]
            }
        }

