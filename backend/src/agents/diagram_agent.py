"""
Diagram generation agent using Strands Agents for MVP.
"""
import os
from strands import Agent
from strands.models import BedrockModel

from ..models.spec import ArchitectureSpec
from .classifier_agent import ClassifierAgent


class DiagramAgent:
    """Agent that converts natural language to ArchitectureSpec."""
    
    def __init__(self):
        """Initialize the agent with Bedrock model."""
        # Get model configuration from environment
        region = os.getenv("AWS_REGION", "us-east-1")
        model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
        
        # Create Bedrock model
        model = BedrockModel(
            model_id=model_id,
            region=region
        )
        
        # Initialize classifier
        self.classifier = ClassifierAgent()
        
        # Create agent with structured output
        self.agent = Agent(
            model=model,
            structured_output=ArchitectureSpec,
            system_prompt="""You are an expert at understanding cloud architecture descriptions and converting them into structured specifications.

Your task:
1. Parse natural language descriptions of cloud architectures
2. Extract components (AWS, Azure, or GCP services)
3. Identify connections between components
4. Determine the cloud provider from the description
5. Return a valid ArchitectureSpec JSON

Rules:
- Detect provider from description (AWS/Azure/GCP)
- Use appropriate NodeType values based on provider:
  AWS: ec2, lambda, s3, dynamodb, rds, api_gateway, elb, ecs, cloudfront, sqs, sns
  Azure: azure_function, azure_vm, blob_storage, cosmos_db
  GCP: cloud_function, compute_engine, cloud_storage, firestore
- Generate meaningful component IDs (lowercase, underscores)
- Infer connections from the description
- Create a descriptive title
- Set provider field correctly

Example:
Input: "Create a serverless API with API Gateway, Lambda, and DynamoDB"
Output:
{
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
"""
        )
    
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

