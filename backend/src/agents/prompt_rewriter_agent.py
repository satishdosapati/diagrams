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
6. Silently replace unavailable components with available alternatives when possible

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

ICON AVAILABILITY CHECK:
- Prefer components that exist in the available icons list
- If user mentions unavailable component, silently suggest closest available alternative
- Use full service names (e.g., "Amazon API Gateway" not "API Gateway")
- Ensure rewritten prompt uses components that will successfully resolve

OUTPUT FORMAT:
- rewritten_description: Enhanced prompt with clustering hints embedded naturally
- improvements: List of specific improvements made (e.g., "Added clustering hints", "Replaced unavailable component")
- components_identified: List of node_ids found in the prompt
- suggested_clusters: List of cluster suggestions with component groupings

EXAMPLE:
Input: "serverless app with api gateway lambda dynamodb"
Output:
{
  "rewritten_description": "Create a serverless architecture with Amazon API Gateway, AWS Lambda functions, and Amazon DynamoDB. Group API Gateway in the API Layer cluster. Group Lambda functions in the Compute Layer cluster. Group DynamoDB in the Data Layer cluster.",
  "improvements": [
    "Added full AWS service names",
    "Identified serverless architectural pattern",
    "Suggested clustering by architectural layers"
  ],
  "components_identified": ["api_gateway", "lambda", "dynamodb"],
  "suggested_clusters": [
    {"name": "API Layer", "components": ["api_gateway"], "pattern": "serverless"},
    {"name": "Compute Layer", "components": ["lambda"], "pattern": "serverless"},
    {"name": "Data Layer", "components": ["dynamodb"], "pattern": "serverless"}
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
If a component is not available, suggest the closest available alternative silently.
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
Rewrite the prompt with clustering hints embedded naturally in the description.
"""
        
        try:
            response = self.agent(prompt)
            result = response.structured_output
            
            # Convert Pydantic model to dict
            return {
                "rewritten_description": result.rewritten_description,
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

