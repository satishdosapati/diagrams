"""
Prompt rewriting agent that enhances user prompts with clustering guidance and icon availability checks.
"""
import os
import logging
from typing import Dict, List, Optional
from strands import Agent
from strands.models import BedrockModel
from pydantic import BaseModel, Field

from ..models.node_registry import get_registry

logger = logging.getLogger(__name__)


class SuggestedCluster(BaseModel):
    """Suggested cluster grouping."""
    name: str = Field(..., description="Cluster display name")
    components: List[str] = Field(..., description="List of component IDs in this cluster")
    pattern: Optional[str] = Field(None, description="Architectural pattern (event-driven, data-pipeline, etc.)")


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
        
        # Initialize registry for icon availability checking
        try:
            self.registry = get_registry()
            logger.info("[PROMPT_REWRITER] NodeRegistry initialized successfully")
        except Exception as e:
            logger.warning(f"[PROMPT_REWRITER] Failed to load NodeRegistry: {e}, continuing without icon check")
            self.registry = None
        
        # Generate system prompt with icon availability info
        system_prompt = self._generate_system_prompt()
        
        self.agent = Agent(
            model=model,
            structured_output_model=PromptRewriteResponse,
            system_prompt=system_prompt
        )
    
    def _generate_system_prompt(self) -> str:
        """Generate system prompt with icon availability information."""
        base_prompt = """You are an expert at rewriting architecture prompts to improve diagram generation quality.

Your task:
1. Analyze the user's architecture description
2. Check component availability against the provided icon registry
3. Identify architectural patterns (event-driven, data pipeline, microservices, serverless, network/VPC)
4. Suggest component groupings/clusters based on architectural layers
5. Rewrite the prompt with clustering hints that help DiagramAgent generate better organized diagrams

CLUSTERING GUIDELINES:
- Always suggest clusters when you have components of similar types or layers
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

ICON AVAILABILITY CHECK:
- Prefer components that exist in the available icons list
- Use full service names (e.g., "Amazon API Gateway" not "API Gateway")
- Ensure rewritten prompt uses components that will successfully resolve

OUTPUT FORMAT:
The rewritten_description must follow this structured format and MUST NOT exceed 2000 characters:

1. Layer-by-layer flow sections showing data/request flow (use layer names as headers)
2. CLUSTERING section with explicit cluster groupings
3. CONNECTIONS section showing component relationships

IMPORTANT: Keep descriptions concise. The rewritten_description field is limited to 2000 characters maximum.

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
- [Component A] connects to [Component B] (connection purpose)
- [Component B] connects to [Component C] (connection purpose)
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
    {"name": "API Layer", "components": ["api_gateway"], "pattern": "serverless"},
    {"name": "Compute Layer", "components": ["lambda"], "pattern": "serverless"},
    {"name": "Data Layer", "components": ["dynamodb"], "pattern": "serverless"}
  ]
}

EXAMPLE 2 - Event-Driven Architecture:
Input: "event driven system: s3 uploads trigger eventbridge which invokes 2 lambdas that write to dynamodb"
Output:
{
  "rewritten_description": "Build an event-driven architecture with the following structured flow:\n\nEvent Sources Layer:\n- Amazon S3 receives file uploads from users\n- S3 generates upload events\n\nEvent Routing Layer:\n- Amazon EventBridge receives events from S3\n- EventBridge routes events to subscribers\n\nEvent Processing Layer:\n- AWS Lambda Function 1 processes events from EventBridge\n- AWS Lambda Function 2 processes events from EventBridge\n- Both Lambda functions execute business logic based on events\n\nEvent Storage Layer:\n- Amazon DynamoDB stores processed event data\n- Lambda Function 1 writes results to DynamoDB\n- Lambda Function 2 writes results to DynamoDB\n\nCLUSTERING:\n- Group S3 in the \"Event Sources\" cluster\n- Group EventBridge in the \"Integration\" layer\n- Group Lambda Function 1 and Lambda Function 2 in the \"Event Processing\" cluster\n- Group DynamoDB in the \"Event Storage\" cluster\n\nCONNECTIONS:\n- S3 connects to EventBridge (event notifications)\n- EventBridge connects to Lambda Function 1 (event routing)\n- EventBridge connects to Lambda Function 2 (event routing)\n- Lambda Function 1 connects to DynamoDB (data writes)\n- Lambda Function 2 connects to DynamoDB (data writes)",
  "improvements": [
    "Clarified event flow and relationships",
    "Identified event-driven architectural pattern",
    "Structured flow by event processing stages",
    "Added explicit clustering and connection information"
  ],
  "components_identified": ["s3", "eventbridge", "lambda", "dynamodb"],
  "suggested_clusters": [
    {"name": "Event Sources", "components": ["s3"], "pattern": "event-driven"},
    {"name": "Event Processing", "components": ["lambda"], "pattern": "event-driven"},
    {"name": "Event Storage", "components": ["dynamodb"], "pattern": "event-driven"}
  ]
}
"""
        
        # Add available icons information if registry is available
        if self.registry:
            try:
                # Get available nodes for all providers (will be filtered per request)
                aws_nodes = self.registry.get_node_list("aws")
                azure_nodes = self.registry.get_node_list("azure")
                gcp_nodes = self.registry.get_node_list("gcp")
                
                # Format node lists (limit to first 100 for readability)
                def format_node_list(nodes, limit=100):
                    if len(nodes) <= limit:
                        return ", ".join(nodes)
                    return ", ".join(nodes[:limit]) + f", ... (and {len(nodes) - limit} more)"
                
                icon_info = f"""

AVAILABLE ICONS BY PROVIDER:
AWS: {format_node_list(aws_nodes)}
Azure: {format_node_list(azure_nodes)}
GCP: {format_node_list(gcp_nodes)}

When rewriting prompts, prefer components from the appropriate provider's available icons list.
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
        # Get available icons for the provider
        available_icons_info = ""
        if self.registry:
            try:
                available_nodes = self.registry.get_node_list(provider)
                if available_nodes:
                    # Format for prompt (limit to 100)
                    if len(available_nodes) <= 100:
                        nodes_str = ", ".join(available_nodes)
                    else:
                        nodes_str = ", ".join(available_nodes[:100]) + f", ... (and {len(available_nodes) - 100} more)"
                    available_icons_info = f"\n\nAvailable icons for {provider.upper()}: {nodes_str}\nPrefer these components when rewriting the prompt."
            except Exception as e:
                logger.warning(f"[PROMPT_REWRITER] Failed to get available icons for {provider}: {e}")
        
        prompt = f"""Rewrite this architecture description to improve diagram generation quality:

{description}

Provider: {provider.upper()}
{available_icons_info}

Analyze the description, check icon availability, identify architectural patterns, and suggest clustering.

IMPORTANT: The rewritten_description must follow this exact structure and MUST NOT exceed 2000 characters:
1. Start with a brief introduction
2. Include layer-by-layer flow sections (use layer names as headers, e.g., "API Layer (Frontend):")
3. Each layer section should list components with their roles
4. Include a "CLUSTERING:" section with explicit cluster groupings
5. Include a "CONNECTIONS:" section showing component relationships

Keep descriptions concise. The rewritten_description field is limited to 2000 characters maximum.
Format the output with clear sections, bullet points, and explicit clustering/connection information.
"""
        
        try:
            response = self.agent(prompt)
            result = response.structured_output
            
            # Enforce 2000 character limit on rewritten_description
            rewritten_desc = result.rewritten_description or description
            MAX_DESCRIPTION_LENGTH = 2000
            if len(rewritten_desc) > MAX_DESCRIPTION_LENGTH:
                logger.warning(f"[PROMPT_REWRITER] Truncating rewritten_description from {len(rewritten_desc)} to {MAX_DESCRIPTION_LENGTH} characters")
                # Truncate at word boundary if possible
                truncated = rewritten_desc[:MAX_DESCRIPTION_LENGTH]
                last_space = truncated.rfind(' ')
                if last_space > MAX_DESCRIPTION_LENGTH * 0.9:  # Only truncate at word if near limit
                    rewritten_desc = truncated[:last_space] + "..."
                else:
                    rewritten_desc = truncated + "..."
            
            # Convert Pydantic model to dict
            return {
                "rewritten_description": rewritten_desc,
                "improvements": result.improvements,
                "components_identified": result.components_identified,
                "suggested_clusters": [
                    {
                        "name": cluster.name,
                        "components": cluster.components,
                        "pattern": cluster.pattern
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

