"""
ArchitectureSpec model with multi-provider support (AWS, Azure, GCP).
"""
from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional, List, Literal, Union
from enum import Enum


class NodeType(str, Enum):
    """
    Multi-provider node types.
    
    Note: This enum contains commonly used nodes. The full list of supported
    nodes is defined in backend/config/node_registry.yaml. The ComponentResolver
    can resolve any node_id from the registry, even if not listed here.
    """
    # AWS - Compute
    EC2 = "ec2"
    LAMBDA = "lambda"
    ECS = "ecs"
    EKS = "eks"
    FARGATE = "fargate"
    BATCH = "batch"
    LIGHTSAIL = "lightsail"
    ELASTIC_BEANSTALK = "elastic_beanstalk"
    
    # AWS - Storage
    S3 = "s3"
    EBS = "ebs"
    EFS = "efs"
    GLACIER = "glacier"
    FSX = "fsx"
    BACKUP = "backup"
    
    # AWS - Database
    DYNAMODB = "dynamodb"
    RDS = "rds"
    AURORA = "aurora"
    REDSHIFT = "redshift"
    ELASTICACHE = "elasticache"
    DOCUMENTDB = "documentdb"
    NEPTUNE = "neptune"
    
    # AWS - Network
    VPC = "vpc"
    APIGATEWAY = "api_gateway"
    CLOUDFRONT = "cloudfront"
    ELB = "elb"
    ALB = "alb"
    NLB = "nlb"
    ROUTE53 = "route53"
    NAT_GATEWAY = "nat_gateway"
    INTERNET_GATEWAY = "internet_gateway"
    VPN_GATEWAY = "vpn_gateway"
    TRANSIT_GATEWAY = "transit_gateway"
    DIRECT_CONNECT = "direct_connect"
    
    # AWS - Integration
    SQS = "sqs"
    SNS = "sns"
    EVENTBRIDGE = "eventbridge"
    STEP_FUNCTIONS = "step_functions"
    APP_SYNC = "app_sync"
    
    # AWS - Analytics
    KINESIS = "kinesis"
    KINESIS_DATA_STREAMS = "kinesis_data_streams"
    KINESIS_DATA_FIREHOSE = "kinesis_data_firehose"
    ATHENA = "athena"
    EMR = "emr"
    GLUE = "glue"
    QUICKSIGHT = "quicksight"
    
    # AWS - Security
    IAM = "iam"
    KMS = "kms"
    SECRETS_MANAGER = "secrets_manager"
    COGNITO = "cognito"
    WAF = "waf"
    SHIELD = "shield"
    GUARDDUTY = "guardduty"
    SECURITY_HUB = "security_hub"
    CERTIFICATE_MANAGER = "certificate_manager"
    
    # AWS - Management
    CLOUDWATCH = "cloudwatch"
    CLOUDFORMATION = "cloudformation"
    SYSTEMS_MANAGER = "systems_manager"
    CONFIG = "config"
    TRUSTED_ADVISOR = "trusted_advisor"
    
    # AWS - IoT
    IOT_CORE = "iot_core"
    IOT_GREENGRASS = "iot_greengrass"
    
    # AWS - ML
    SAGEMAKER = "sagemaker"
    REKOGNITION = "rekognition"
    COMPREHEND = "comprehend"
    POLLY = "polly"
    TRANSLATE = "translate"
    TRANSCRIBE = "transcribe"
    
    # Azure - Compute
    AZURE_FUNCTION = "azure_function"
    AZURE_VM = "azure_vm"
    CONTAINER_INSTANCES = "container_instances"
    KUBERNETES_SERVICES = "kubernetes_services"
    APP_SERVICE = "app_service"
    # Note: batch and backup are AWS enum values, Azure uses strings "batch" and "backup"
    CLOUD_SERVICES = "cloud_services"
    SERVICE_FABRIC = "service_fabric"
    
    # Azure - Storage
    BLOB_STORAGE = "blob_storage"
    FILE_STORAGE = "file_storage"
    DATA_LAKE = "data_lake"
    DISK_STORAGE = "disk_storage"
    # Note: backup is AWS enum value, Azure uses string "backup"
    ARCHIVE_STORAGE = "archive_storage"
    
    # Azure - Database
    COSMOS_DB = "cosmos_db"
    SQL_DATABASE = "sql_database"
    DATABASE_FOR_MYSQL = "database_for_mysql"
    DATABASE_FOR_POSTGRESQL = "database_for_postgresql"
    DATABASE_FOR_MARIADB = "database_for_mariadb"
    REDIS_CACHE = "redis_cache"
    DATA_FACTORY = "data_factory"
    SQL_DATAWAREHOUSE = "sql_datawarehouse"
    
    # Azure - Network
    VIRTUAL_NETWORK = "virtual_network"
    LOAD_BALANCER = "load_balancer"
    APPLICATION_GATEWAY = "application_gateway"
    # Note: vpn_gateway is AWS enum value, Azure uses string "vpn_gateway"
    EXPRESSROUTE = "expressroute"
    # Note: dns, cdn, firewall are GCP enum values, Azure uses strings
    TRAFFIC_MANAGER = "traffic_manager"
    
    # Azure - Integration
    SERVICE_BUS = "service_bus"
    EVENT_GRID = "event_grid"
    EVENT_HUBS = "event_hubs"
    LOGIC_APPS = "logic_apps"
    API_MANAGEMENT = "api_management"
    
    # Azure - Security
    KEY_VAULTS = "key_vaults"
    ACTIVE_DIRECTORY = "active_directory"
    SECURITY_CENTER = "security_center"
    SENTINEL = "sentinel"
    APPLICATION_SECURITY_GROUPS = "application_security_groups"
    
    # Azure - Management
    # Note: monitor and policy are GCP enum values, Azure uses strings
    RESOURCE_MANAGER = "resource_manager"
    AUTOMATION = "automation"
    
    # Azure - Analytics
    DATA_LAKE_ANALYTICS = "data_lake_analytics"
    STREAM_ANALYTICS = "stream_analytics"
    HDINSIGHT = "hdinsight"
    DATABRICKS = "databricks"
    SYNAPSE_ANALYTICS = "synapse_analytics"
    
    # Azure - IoT
    AZURE_IOT_HUB = "iot_hub"  # Different from AWS iot_core
    AZURE_IOT_CENTRAL = "iot_central"
    
    # Azure - ML
    MACHINE_LEARNING = "machine_learning"
    COGNITIVE_SERVICES = "cognitive_services"
    
    # GCP - Compute
    CLOUD_FUNCTION = "cloud_function"
    COMPUTE_ENGINE = "compute_engine"
    APP_ENGINE = "app_engine"
    CLOUD_RUN = "cloud_run"
    GKE = "gke"
    CLOUD_SQL = "cloud_sql"
    # Note: batch is AWS enum value, GCP uses string "batch"
    
    # GCP - Storage
    CLOUD_STORAGE = "cloud_storage"
    FILESTORE = "filestore"
    PERSISTENT_DISK = "persistent_disk"
    STORAGE_TRANSFER = "storage_transfer"
    
    # GCP - Database
    FIRESTORE = "firestore"
    BIGTABLE = "bigtable"
    SPANNER = "spanner"
    MEMORYSTORE = "memorystore"
    DATASTORE = "datastore"
    
    # GCP - Network
    # Note: vpc is AWS enum value, GCP uses string "vpc"
    LOAD_BALANCING = "load_balancing"
    CLOUD_DNS = "dns"  # Note: registry uses "dns" not "cloud_dns"
    CLOUD_CDN = "cdn"
    CLOUD_INTERCONNECT = "cloud_interconnect"
    CLOUD_VPN = "cloud_vpn"
    CLOUD_ARMOR = "cloud_armor"
    CLOUD_NAT = "cloud_nat"
    
    # GCP - Integration
    PUBSUB = "pubsub"
    CLOUD_SCHEDULER = "cloud_scheduler"
    CLOUD_TASKS = "cloud_tasks"
    CLOUD_ENDPOINTS = "cloud_endpoints"
    # Note: api_gateway is AWS enum value, GCP uses string "api_gateway"
    WORKFLOW = "workflow"
    
    # GCP - Security
    # Note: iam is AWS enum value, GCP uses string "iam"
    CLOUD_KMS = "cloud_kms"
    SECRET_MANAGER = "secret_manager"
    SECURITY_COMMAND_CENTER = "security_command_center"
    CLOUD_ARMOR_SECURITY = "cloud_armor_security"
    
    # GCP - Management
    CLOUD_MONITORING = "cloud_monitoring"
    CLOUD_LOGGING = "cloud_logging"
    CLOUD_TRACE = "cloud_trace"
    CLOUD_DEBUGGER = "cloud_debugger"
    CLOUD_PROFILER = "cloud_profiler"
    DEPLOYMENT_MANAGER = "deployment_manager"
    
    # GCP - Analytics
    BIGQUERY = "bigquery"
    DATAFLOW = "dataflow"
    DATAPROC = "dataproc"
    DATAPREP = "dataprep"
    DATA_FUSION = "data_fusion"
    DATA_CATALOG = "data_catalog"
    
    # GCP - IoT
    # Note: iot_core is AWS enum value, GCP uses string "iot_core"
    
    # GCP - ML
    AI_PLATFORM = "ai_platform"
    AUTOML = "automl"
    NATURAL_LANGUAGE_API = "natural_language_api"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    TRANSLATION_API = "translation_api"
    VIDEO_INTELLIGENCE = "video_intelligence"
    VISION_API = "vision_api"


class GraphvizAttributes(BaseModel):
    """Graphviz attribute configuration for diagram styling."""
    graph_attr: dict = Field(default_factory=dict, description="Graph-level attributes (e.g., rankdir, bgcolor)")
    node_attr: dict = Field(default_factory=dict, description="Default node attributes (e.g., shape, style, fillcolor)")
    edge_attr: dict = Field(default_factory=dict, description="Default edge attributes (e.g., color, style, arrowsize)")


class Component(BaseModel):
    """
    Represents a component in the architecture.
    
    The type field accepts either a NodeType enum value or a string node_id.
    String values are validated against the node registry at runtime.
    """
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Display name")
    type: Union[NodeType, str] = Field(..., description="Component type (enum or node_id string)")
    provider: Optional[str] = Field(None, description="Cloud provider (inherits from spec if not set)")
    metadata: dict = Field(default_factory=dict, description="Additional properties")
    graphviz_attrs: Optional[dict] = Field(None, description="Component-specific Graphviz node attributes")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Validate type is either a NodeType enum or a valid string."""
        if isinstance(v, NodeType):
            return v
        if isinstance(v, str):
            # String values will be validated against registry at resolution time
            return v
        raise ValueError(f"Type must be NodeType enum or string, got {type(v)}")
    
    def get_node_id(self) -> str:
        """Get node_id as string (from enum value or direct string)."""
        if isinstance(self.type, NodeType):
            return self.type.value
        return str(self.type)


class Connection(BaseModel):
    """Represents a connection between components."""
    from_id: str = Field(..., description="Source component ID")
    to_id: str = Field(..., description="Target component ID")
    label: Optional[str] = Field(None, description="Connection label")
    graphviz_attrs: Optional[dict] = Field(None, description="Connection-specific Graphviz edge attributes")
    direction: Optional[Literal["forward", "backward", "bidirectional"]] = Field(
        None, 
        description="Connection direction: forward (>>), backward (<<), or bidirectional (-)"
    )


class Cluster(BaseModel):
    """Represents a cluster/group of components."""
    id: str = Field(..., description="Unique cluster identifier")
    name: str = Field(..., description="Cluster display name")
    component_ids: List[str] = Field(..., description="List of component IDs in this cluster")
    graphviz_attrs: Optional[dict] = Field(None, description="Cluster-specific Graphviz attributes")
    # Note: Nested clusters removed to avoid recursion issues with Strands structured output
    # For nesting, use parent_id to reference parent cluster
    parent_id: Optional[str] = Field(None, description="Parent cluster ID for nested clusters")
    
    model_config = {"arbitrary_types_allowed": True}


class ArchitectureSpec(BaseModel):
    """Architecture specification with provider support."""
    title: str = Field(..., description="Diagram title")
    provider: Literal["aws", "azure", "gcp"] = Field(default="aws", description="Cloud provider")
    is_multi_cloud: bool = Field(default=False, description="Allow multiple providers")
    components: List[Component] = Field(default_factory=list, description="Architecture components")
    connections: List[Connection] = Field(default_factory=list, description="Component connections")
    clusters: List[Cluster] = Field(default_factory=list, description="Component clusters/groups")
    metadata: dict = Field(default_factory=dict, description="Additional metadata (diagram_type, etc.)")
    graphviz_attrs: Optional[GraphvizAttributes] = Field(None, description="Custom Graphviz attributes for diagram styling")
    direction: Optional[Literal["TB", "BT", "LR", "RL"]] = Field(
        None,
        description="Layout direction: TB (top-bottom), BT (bottom-top), LR (left-right), RL (right-left)"
    )
    outformat: Optional[Union[str, List[str]]] = Field(
        None,
        description="Output format(s): png, svg, pdf, jpg, dot. Can be single format or list."
    )
    
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


# Resolve forward references (no longer needed but kept for safety)
Cluster.model_rebuild()
ArchitectureSpec.model_rebuild()

