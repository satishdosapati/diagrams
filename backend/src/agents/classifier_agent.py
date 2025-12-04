"""
Diagram type classifier agent.
"""
import os
from strands import Agent
from strands.models import BedrockModel
from pydantic import BaseModel
from typing import Literal, Optional


class DiagramClassification(BaseModel):
    """Classification of diagram type."""
    diagram_type: Literal[
        "cloud_architecture",
        "system_architecture",
        "network_topology",
        "data_pipeline",
        "c4_model"
    ]
    provider: Optional[Literal["aws", "azure", "gcp"]] = None
    complexity: Literal["simple", "medium", "complex"] = "medium"


class ClassifierAgent:
    """Agent that classifies diagram type from description."""
    
    def __init__(self):
        """Initialize classifier agent."""
        model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
        
        # Create Bedrock model (region configured via AWS_REGION env var or boto3 default)
        model = BedrockModel(model_id=model_id)
        
        self.agent = Agent(
            model=model,
            structured_output_model=DiagramClassification,
            system_prompt="""Classify architecture diagram requests into types:

- cloud_architecture: AWS/Azure/GCP service diagrams
- system_architecture: Application/system design (microservices, monoliths)
- network_topology: Network/VPC diagrams
- data_pipeline: ETL/data flow diagrams
- c4_model: C4 model diagrams (system context, containers, components)

Also detect the cloud provider if mentioned (AWS, Azure, GCP).
"""
        )
    
    def classify(self, description: str) -> DiagramClassification:
        """
        Classify diagram type from description.
        
        Args:
            description: Natural language description
            
        Returns:
            Diagram classification
        """
        prompt = f"""Classify this architecture description:

{description}

Return the diagram type and provider."""
        
        response = self.agent(prompt)
        return response.structured_output

