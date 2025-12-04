"""
Diagram generation agent using Strands Agents for MVP.
"""
import os
from strands import Agent
from strands.models import BedrockModel

from ..models.spec import ArchitectureSpec
from ..models.node_registry import get_registry
from .classifier_agent import ClassifierAgent


class DiagramAgent:
    """Agent that converts natural language to ArchitectureSpec."""
    
    def __init__(self):
        """Initialize the agent with Bedrock model."""
        # Get model configuration from environment
        model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
        
        # Create Bedrock model (region configured via AWS_REGION env var or boto3 default)
        model = BedrockModel(model_id=model_id)
        
        # Initialize classifier
        self.classifier = ClassifierAgent()
        
        # Load registry for generating node lists
        self.registry = get_registry()
        
        # Generate system prompt with node lists from registry
        system_prompt = self._generate_system_prompt()
        
        # Create agent with structured output
        self.agent = Agent(
            model=model,
            structured_output_model=ArchitectureSpec,
            system_prompt=system_prompt
        )
    
    def _generate_system_prompt(self) -> str:
        """Generate system prompt with node lists from registry."""
        # Get node lists for each provider
        aws_nodes = self.registry.get_node_list("aws")
        azure_nodes = self.registry.get_node_list("azure")
        gcp_nodes = self.registry.get_node_list("gcp")
        
        # Format node lists (limit to first 50 for readability)
        def format_node_list(nodes, limit=50):
            if len(nodes) <= limit:
                return ", ".join(nodes)
            return ", ".join(nodes[:limit]) + f", ... (and {len(nodes) - limit} more)"
        
        aws_list = format_node_list(aws_nodes)
        azure_list = format_node_list(azure_nodes)
        gcp_list = format_node_list(gcp_nodes)
        
        return f"""You are an expert at understanding cloud architecture descriptions and converting them into structured specifications.

Your task:
1. Parse natural language descriptions of cloud architectures
2. Extract components (AWS, Azure, or GCP services)
3. Identify connections between components
4. Determine the cloud provider from the description
5. Return a valid ArchitectureSpec JSON

Rules:
- Detect provider from description (AWS/Azure/GCP)
- Use appropriate NodeType values based on provider (use the node_id strings):
  AWS: {aws_list}
  Azure: {azure_list}
  GCP: {gcp_list}
- Generate meaningful component IDs (lowercase, underscores)
- Infer connections from the description
- Create a descriptive title
- Set provider field correctly
- Use the exact node_id strings from the lists above (e.g., "ec2", "lambda", "vpc")

Example:
Input: "Create a serverless API with API Gateway, Lambda, and DynamoDB"
Output:
{{
  "title": "Serverless API",
  "provider": "aws",
  "components": [
    {{"id": "api", "name": "API Gateway", "type": "api_gateway"}},
    {{"id": "lambda", "name": "Function", "type": "lambda"}},
    {{"id": "db", "name": "Database", "type": "dynamodb"}}
  ],
  "connections": [
    {{"from_id": "api", "to_id": "lambda"}},
    {{"from_id": "lambda", "to_id": "db"}}
  ]
}}
"""
    
    def generate_spec(self, description: str) -> ArchitectureSpec:
        """
        Generate ArchitectureSpec from natural language description.
        
        Args:
            description: Natural language architecture description
            
        Returns:
            ArchitectureSpec object
        """
        # Classify diagram type
        classification = self.classifier.classify(description)
        
        prompt = f"""Parse this architecture description into an ArchitectureSpec:

{description}

Diagram Type: {classification.diagram_type}
Provider: {classification.provider or "detect from description"}

Return a valid ArchitectureSpec JSON with components and connections."""
        
        response = self.agent(prompt)
        
        # Get structured output
        spec = response.structured_output
        
        # Set diagram type in metadata
        spec.metadata["diagram_type"] = classification.diagram_type
        
        # Set provider from classification if detected
        if classification.provider:
            spec.provider = classification.provider
        
        return spec

