"""
Prompt rewriting agent that enhances user prompts with clustering guidance and icon availability checks.
"""
import os
import logging
import re
from typing import Dict, List, Optional, Set
from strands import Agent
from strands.models import BedrockModel
from pydantic import BaseModel, Field

from ..models.node_registry import get_registry
from ..resolvers.library_discovery import LibraryDiscovery

logger = logging.getLogger(__name__)


class SuggestedCluster(BaseModel):
    """Suggested cluster grouping."""
    name: str = Field(..., description="Cluster display name")
    components: List[str] = Field(..., description="List of component IDs in this cluster")
    pattern: Optional[str] = Field(None, description="Architectural pattern (event-driven, data-pipeline, etc.)")
    parent_id: Optional[str] = Field(None, description="Parent cluster ID for nested clusters (e.g., VPC → Subnets)")


class PromptRewriteResponse(BaseModel):
    """Response model for prompt rewriting."""
    rewritten_description: str = Field(..., description="Enhanced prompt with clustering hints")
    improvements: List[str] = Field(default_factory=list, description="List of improvements made")
    components_identified: List[str] = Field(default_factory=list, description="List of component node_ids identified")
    suggested_clusters: List[SuggestedCluster] = Field(default_factory=list, description="Suggested cluster groupings")


class PromptRewriterAgent:
    """Agent that rewrites prompts with clustering guidance and icon availability checks."""
    
    def __init__(self):
        """Initialize prompt rewriter agent."""
        model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
        
        # Create Bedrock model (region configured via AWS_REGION env var or boto3 default)
        model = BedrockModel(model_id=model_id)
        
        # Initialize registry for fallback/helper (YAML-based)
        try:
            self.registry = get_registry()
            logger.info("[PROMPT_REWRITER] NodeRegistry initialized successfully")
        except Exception as e:
            logger.warning(f"[PROMPT_REWRITER] Failed to load NodeRegistry: {e}, continuing without registry")
            self.registry = None
        
        # Initialize LibraryDiscovery instances for each provider (source of truth)
        # These will be created lazily per provider when needed
        self._discovery_cache: Dict[str, LibraryDiscovery] = {}
        
        # Generate system prompt with icon availability info
        system_prompt = self._generate_system_prompt()
        
        self.agent = Agent(
            model=model,
            structured_output_model=PromptRewriteResponse,
            system_prompt=system_prompt
        )
    
    def _get_discovery(self, provider: str) -> LibraryDiscovery:
        """Get or create LibraryDiscovery instance for a provider."""
        if provider not in self._discovery_cache:
            try:
                self._discovery_cache[provider] = LibraryDiscovery(provider)
                logger.info(f"[PROMPT_REWRITER] LibraryDiscovery initialized for {provider}")
            except Exception as e:
                logger.warning(f"[PROMPT_REWRITER] Failed to initialize LibraryDiscovery for {provider}: {e}")
                return None
        return self._discovery_cache.get(provider)
    
    def _class_name_to_node_id(self, class_name: str) -> str:
        """
        Convert class name to node_id format (lowercase, snake_case).
        
        Examples:
        - "EC2" -> "ec2"
        - "EC2Instance" -> "ec2_instance"
        - "ApplicationLoadBalancer" -> "application_load_balancer"
        - "APIGateway" -> "api_gateway"
        - "S3" -> "s3"
        """
        # Remove common prefixes
        normalized = re.sub(r'^(AWS|Amazon|Azure|GCP|Google|Microsoft)\s*', '', class_name, flags=re.IGNORECASE)
        
        # Handle acronyms at the start (e.g., "EC2", "S3", "API")
        # Insert underscore before first lowercase letter after acronyms
        normalized = re.sub(r'^([A-Z]{2,})([a-z])', r'\1_\2', normalized)
        
        # Convert CamelCase to snake_case
        # Insert underscore before uppercase letters that follow lowercase letters or numbers
        normalized = re.sub(r'(?<!^)(?<!_)([a-z0-9])([A-Z])', r'\1_\2', normalized)
        # Insert underscore before uppercase sequences followed by lowercase
        normalized = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', normalized)
        
        # Convert to lowercase
        normalized = normalized.lower()
        
        # Clean up multiple underscores
        normalized = re.sub(r'_+', '_', normalized)
        
        # Remove leading/trailing underscores
        normalized = normalized.strip('_')
        
        return normalized
    
    def _get_available_node_ids(self, provider: str) -> List[str]:
        """
        Get available node IDs for a provider using LibraryDiscovery (source of truth).
        Falls back to registry if discovery fails.
        
        Returns:
            List of node_id strings (normalized from class names)
        """
        discovery = self._get_discovery(provider)
        if discovery:
            try:
                # Get all available classes from discovery
                all_classes_dict = discovery.get_all_available_classes()
                # Flatten all classes from all modules
                all_classes: Set[str] = set()
                for classes_set in all_classes_dict.values():
                    all_classes.update(classes_set)
                
                # Convert class names to node_ids
                node_ids = [self._class_name_to_node_id(cls) for cls in all_classes]
                # Remove duplicates and sort
                node_ids = sorted(set(node_ids))
                logger.info(f"[PROMPT_REWRITER] Discovered {len(node_ids)} available node_ids for {provider} via LibraryDiscovery")
                return node_ids
            except Exception as e:
                logger.warning(f"[PROMPT_REWRITER] Failed to get classes from LibraryDiscovery for {provider}: {e}")
        
        # Fallback to registry if discovery fails
        if self.registry:
            try:
                node_ids = self.registry.get_node_list(provider)
                logger.info(f"[PROMPT_REWRITER] Using registry fallback: {len(node_ids)} node_ids for {provider}")
                return node_ids
            except Exception as e:
                logger.warning(f"[PROMPT_REWRITER] Failed to get node_ids from registry for {provider}: {e}")
        
        return []
    
    def _generate_system_prompt(self) -> str:
        """Generate system prompt with icon availability information."""
        base_prompt = """You are an expert at rewriting architecture prompts to improve diagram generation quality.

Your task:
1. Analyze the user's architecture description
2. Check component availability against the provided icon registry (discovered from actual library)
3. Identify architectural patterns (event-driven, data pipeline, microservices, serverless, network/VPC)
4. Suggest component groupings/clusters based on architectural layers
5. Rewrite the prompt with clustering hints that help DiagramAgent generate better organized diagrams

CLUSTERING GUIDELINES:
- Always suggest clusters when you have 3+ components of similar types or layers
- Use pattern-specific cluster names:
  * Event-Driven: "Event Sources", "Event Processing", "Event Storage"
  * Data Pipeline: "Data Sources", "Processing Layer", "Storage Layer", "Analytics Layer"
  * Microservices: "API Layer", "Service Layer", "Data Layer"
  * Serverless: "API Layer", "Compute Layer", "Data Layer"
  * Network/VPC: "Public Layer", "Private Layer", "Data Layer" (with nested VPC → Subnets → Resources)
- Group components by architectural layers:
  * Frontend/Edge: Route53, CloudFront, WAF, API Gateway
  * Network: VPC, Subnets, Internet Gateway, NAT Gateway
  * Compute: EC2, Lambda, ECS, EKS
  * Data: RDS, DynamoDB, S3, ElastiCache
  * Integration: SQS, SNS, EventBridge
- For VPC architectures, suggest nested clusters using parent_id:
  * VPC cluster contains Subnet clusters (subnets have parent_id pointing to VPC)
  * Subnet clusters contain EC2 instances (EC2 components have parent_id pointing to Subnet)

ICON AVAILABILITY CHECK:
- Prefer components that exist in the available icons list
- Use full service names with descriptive subtitles (e.g., "Amazon API Gateway (API Management)" not "API Gateway")
- Examples of proper naming:
  * "Amazon EventBridge (Event Bus)"
  * "Amazon DynamoDB (Event Storage)"
  * "Amazon Kinesis (Data Stream)"
  * "Amazon S3 (Data Lake)"
  * "Amazon Redshift (Data Warehouse)"
  * "AWS Lambda Function"
- Ensure rewritten prompt uses components that will successfully resolve

OUTPUT FORMAT:
The rewritten_description must follow this structured format:

1. Layer-by-layer flow sections showing data/request flow (use layer names as headers)
2. CLUSTERING section with explicit cluster groupings
3. CONNECTIONS section showing component relationships

IMPORTANT: Keep descriptions concise.

Format structure:
[Layer Name] (optional description):
- Component 1 description and role
- Component 2 description and role
...

CLUSTERING:
- Group [component] in the "[Cluster Name]" cluster
- Group [components] in the "[Cluster Name]" cluster
...

CONNECTIONS:
- [Component A] connects to [Component B] (connection purpose/label)
- [Component B] connects to [Component C] (connection purpose/label)
- Use descriptive labels for connections:
  * Event-Driven: "Event Stream", "Event Routing"
  * Serverless: "HTTP Request", "Query/Write"
  * Data Pipeline: "Data Stream", "Storage"
  * Microservices: "API Request"
  * Network: "Traffic"
- Follow canonical patterns (see PATTERN ENFORCEMENT below)
...

EXAMPLE 1 - Serverless Architecture:
Input: "serverless app with api gateway lambda dynamodb"
Output:
{
  "rewritten_description": "Create a serverless architecture with the following structured flow:\n\nAPI Layer (Frontend):\n- Amazon API Gateway receives HTTP requests from clients\n\nCompute Layer (Processing):\n- AWS Lambda functions process requests from API Gateway\n- Lambda functions execute business logic\n\nData Layer (Storage):\n- Amazon DynamoDB stores application data\n- Lambda functions read and write data to DynamoDB\n\nCLUSTERING:\n- Group API Gateway in the \"API Layer\" cluster\n- Group Lambda functions in the \"Compute Layer\" cluster\n- Group DynamoDB in the \"Data Layer\" cluster\n\nCONNECTIONS:\n- API Gateway connects to Lambda functions (HTTP requests)\n- Lambda functions connect to DynamoDB (read/write operations)",
  "improvements": [
    "Added full AWS service names",
    "Identified serverless architectural pattern",
    "Structured flow by architectural layers",
    "Added explicit clustering and connection information"
  ],
  "components_identified": ["api_gateway", "lambda", "dynamodb"],
  "suggested_clusters": [
    {"name": "API Layer", "components": ["api_gateway"], "pattern": "serverless", "parent_id": null},
    {"name": "Compute Layer", "components": ["lambda"], "pattern": "serverless", "parent_id": null},
    {"name": "Data Layer", "components": ["dynamodb"], "pattern": "serverless", "parent_id": null}
  ]
}

EXAMPLE 2 - Event-Driven Architecture:
Input: "event driven system: s3 uploads trigger eventbridge which invokes 2 lambdas that write to dynamodb"
Output:
{
  "rewritten_description": "Build an event-driven architecture with the following structured flow:\n\nEvent Sources Layer:\n- Amazon S3 (Data Lake) receives file uploads from users\n- S3 generates upload events\n\nEvent Routing Layer:\n- Amazon EventBridge (Event Bus) receives events from S3\n- EventBridge routes events to subscribers\n\nEvent Processing Layer:\n- AWS Lambda Function 1 processes events from EventBridge\n- AWS Lambda Function 2 processes events from EventBridge\n- Both Lambda functions execute business logic based on events\n\nEvent Storage Layer:\n- Amazon DynamoDB (Event Storage) stores processed event data\n- Lambda Function 1 writes results to DynamoDB\n- Lambda Function 2 writes results to DynamoDB\n\nCLUSTERING:\n- Group S3 in the \"Event Sources\" cluster\n- Group EventBridge in the \"Integration\" layer\n- Group Lambda Function 1 and Lambda Function 2 in the \"Event Processing\" cluster\n- Group DynamoDB in the \"Event Storage\" cluster\n\nCONNECTIONS:\n- S3 connects to EventBridge (Event Stream)\n- EventBridge connects to Lambda Function 1 (Event Routing)\n- EventBridge connects to Lambda Function 2 (Event Routing)\n- Lambda Function 1 connects to DynamoDB (Query/Write)\n- Lambda Function 2 connects to DynamoDB (Query/Write)\n\nIMPORTANT: In event-driven architectures, all event sources MUST connect TO EventBridge, and all processors connect FROM EventBridge. Do NOT create direct source-to-processor connections when EventBridge exists.",
  "improvements": [
    "Clarified event flow and relationships",
    "Identified event-driven architectural pattern",
    "Structured flow by event processing stages",
    "Added explicit clustering and connection information",
    "Added descriptive service name subtitles",
    "Emphasized canonical pattern enforcement"
  ],
  "components_identified": ["s3", "eventbridge", "lambda", "dynamodb"],
  "suggested_clusters": [
    {"name": "Event Sources", "components": ["s3"], "pattern": "event-driven", "parent_id": null},
    {"name": "Event Processing", "components": ["lambda"], "pattern": "event-driven", "parent_id": null},
    {"name": "Event Storage", "components": ["dynamodb"], "pattern": "event-driven", "parent_id": null}
  ]
}

PATTERN ENFORCEMENT (CRITICAL):
- Event-Driven Architecture: All event sources MUST connect TO EventBridge, all processors connect FROM EventBridge
  * Do NOT create direct source-to-processor connections when EventBridge exists
  * Pattern: Sources → EventBridge → Processors → Storage
- Serverless Pattern: API Gateway → Lambda → DynamoDB (enforce this order)
- Microservices Pattern: API Gateway → Services → Database (enforce service boundaries)
- Data Pipeline Pattern: Source → Queue/Stream → Processor → Storage (enforce flow direction)
- VPC Pattern: Internet Gateway → VPC → Subnet → EC2 (enforce network hierarchy)
  * VPC should contain Subnets (use nested clusters with parent_id)
  * Subnets should contain EC2 instances (use nested clusters with parent_id)
"""
        
        # Add available icons information using LibraryDiscovery (source of truth)
        try:
            # Get available nodes for all providers using discovery
            aws_nodes = self._get_available_node_ids("aws")
            azure_nodes = self._get_available_node_ids("azure")
            gcp_nodes = self._get_available_node_ids("gcp")
            
            # Format node lists (limit to first 100 for readability)
            def format_node_list(nodes, limit=100):
                if len(nodes) <= limit:
                    return ", ".join(nodes)
                return ", ".join(nodes[:limit]) + f", ... (and {len(nodes) - limit} more)"
            
            icon_info = f"""

AVAILABLE ICONS BY PROVIDER (discovered from actual diagrams library):
AWS: {format_node_list(aws_nodes)}
Azure: {format_node_list(azure_nodes)}
GCP: {format_node_list(gcp_nodes)}

When rewriting prompts, prefer components from the appropriate provider's available icons list.
These are discovered directly from the installed diagrams library, ensuring accuracy.
"""
            return base_prompt + icon_info
        except Exception as e:
            logger.warning(f"[PROMPT_REWRITER] Failed to load icon lists: {e}, continuing without icon info")
        
        return base_prompt
    
    def rewrite(self, description: str, provider: str) -> Dict:
        """
        Rewrite prompt with clustering guidance and icon availability checks.
        
        Args:
            description: Original user prompt
            provider: Cloud provider (aws, azure, gcp)
            
        Returns:
            Dictionary with rewritten_description, improvements, components_identified, suggested_clusters
        """
        # Get available icons for the provider using LibraryDiscovery (source of truth)
        available_icons_info = ""
        try:
            available_nodes = self._get_available_node_ids(provider)
            if available_nodes:
                # Format for prompt (limit to 100)
                if len(available_nodes) <= 100:
                    nodes_str = ", ".join(available_nodes)
                else:
                    nodes_str = ", ".join(available_nodes[:100]) + f", ... (and {len(available_nodes) - 100} more)"
                available_icons_info = f"\n\nAvailable icons for {provider.upper()} (discovered from actual library): {nodes_str}\nPrefer these components when rewriting the prompt."
        except Exception as e:
            logger.warning(f"[PROMPT_REWRITER] Failed to get available icons for {provider}: {e}")
        
        prompt = f"""Rewrite this architecture description to improve diagram generation quality:

{description}

Provider: {provider.upper()}
{available_icons_info}

Analyze the description, check icon availability, identify architectural patterns, and suggest clustering.

IMPORTANT: The rewritten_description must follow this exact structure:
1. Start with a brief introduction
2. Include layer-by-layer flow sections (use layer names as headers, e.g., "API Layer (Frontend):")
3. Each layer section should list components with their roles
4. Use full service names with descriptive subtitles (e.g., "Amazon API Gateway (API Management)")
5. Include a "CLUSTERING:" section with explicit cluster groupings
   - Suggest clusters only when there are 3+ components of similar types
   - For VPC architectures, suggest nested clusters (VPC → Subnets → Resources)
6. Include a "CONNECTIONS:" section showing component relationships with descriptive labels
   - Follow canonical pattern enforcement rules (see PATTERN ENFORCEMENT in system prompt)
   - Use clear connection labels (e.g., "Event Stream", "HTTP Request", "Query/Write")

Keep descriptions concise.
Format the output with clear sections, bullet points, and explicit clustering/connection information.
"""
        
        try:
            response = self.agent(prompt)
            result = response.structured_output
            
            # Convert Pydantic model to dict
            return {
                "rewritten_description": result.rewritten_description or description,
                "improvements": result.improvements,
                "components_identified": result.components_identified,
                "suggested_clusters": [
                    {
                        "name": cluster.name,
                        "components": cluster.components,
                        "pattern": cluster.pattern,
                        "parent_id": cluster.parent_id
                    }
                    for cluster in result.suggested_clusters
                ]
            }
        except Exception as e:
            logger.error(f"[PROMPT_REWRITER] Error rewriting prompt: {e}", exc_info=True)
            # Fallback to original prompt with error message
            return {
                "rewritten_description": description,
                "improvements": [f"Rewrite failed: {str(e)}"],
                "components_identified": [],
                "suggested_clusters": []
            }

