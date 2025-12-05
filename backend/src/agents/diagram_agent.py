"""
Diagram generation agent using Strands Agents for MVP.
"""
import os
import logging
from typing import Optional
from strands import Agent
from strands.models import BedrockModel

from ..models.spec import ArchitectureSpec
from ..models.node_registry import get_registry
from .classifier_agent import ClassifierAgent
from ..advisors.aws_architectural_advisor import AWSArchitecturalAdvisor
from ..validators.input_validator import InputValidator
from ..integrations.mcp_diagram_client import get_mcp_client

logger = logging.getLogger(__name__)


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
        
        # Initialize AWS Architectural Advisor
        self.aws_advisor = AWSArchitecturalAdvisor()
        
        # Initialize Input Validator
        self.input_validator = InputValidator()
        
        # Initialize MCP client (for optional MCP tool integration)
        self.mcp_client = get_mcp_client()
        self.use_mcp_tools = self.mcp_client.enabled
        
        logger.info(f"[DIAGRAM_AGENT] MCP tools enabled: {self.use_mcp_tools}")
        
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
        
        # Get AWS architectural guidance
        aws_guidance = self.aws_advisor._get_static_guidance()
        
        # Add MCP tools instruction if enabled
        mcp_tools_instruction = ""
        if self.use_mcp_tools:
            mcp_tools_instruction = """

AVAILABLE MCP TOOLS (for diagram code generation and validation):
- generate_diagram_from_code(code, filename=None, timeout=None): Generate diagram PNG from Python code using MCP server
- validate_diagram_code(code): Validate diagram code for security and best practices (uses generate_diagram internally)
- enhance_diagram_code(code, diagram_type): Enhance diagram code with MCP server optimizations

Note: These tools are available for post-processing ArchitectureSpec. The primary task is still to generate ArchitectureSpec from natural language.
"""
        
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

CLUSTERING GUIDELINES (IMPORTANT):
- Always create clusters when you have 3+ components of similar types or layers
- Group related components together for better visual organization:
  * Frontend/Edge: Route53, CloudFront, WAF, API Gateway
  * Network: VPC, Subnets, Internet Gateway, NAT Gateway
  * Compute: EC2, Lambda, ECS, EKS instances
  * Data: RDS, DynamoDB, S3, ElastiCache
  * Integration: SQS, SNS, EventBridge
- For VPC architectures, create nested clusters: VPC → Subnets → Resources
- Use descriptive cluster names like "Frontend Layer", "Backend Services", "Data Layer", "VPC Network"
- Example cluster structure:
  {{
    "clusters": [
      {{
        "id": "frontend",
        "name": "Frontend Layer",
        "component_ids": ["api", "cdn"]
      }},
      {{
        "id": "backend",
        "name": "Backend Services",
        "component_ids": ["lambda1", "lambda2"]
      }}
    ]
  }}

AWS Architectural Best Practices (when provider is AWS):
{aws_guidance}

IMPORTANT for AWS architectures:
- Order components logically: Internet/Edge → Network → Application → Compute → Data
- VPC should contain Subnets (add connection: VPC → Subnet)
- Subnets should contain EC2 instances (add connection: Subnet → EC2)
- Follow common patterns: API Gateway → Lambda → DynamoDB, ALB → EC2 → RDS
- Add missing dependencies (e.g., if EC2 exists, ensure VPC and Subnet exist)

Example 1 - Simple Architecture:
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

Example 2 - Architecture with Clusters:
Input: "Create a microservices architecture with API Gateway, CloudFront, three Lambda functions, and DynamoDB"
Output:
{{
  "title": "Microservices Architecture",
  "provider": "aws",
  "components": [
    {{"id": "api", "name": "API Gateway", "type": "api_gateway"}},
    {{"id": "cdn", "name": "CloudFront", "type": "cloudfront"}},
    {{"id": "lambda1", "name": "Service 1", "type": "lambda"}},
    {{"id": "lambda2", "name": "Service 2", "type": "lambda"}},
    {{"id": "lambda3", "name": "Service 3", "type": "lambda"}},
    {{"id": "db", "name": "Database", "type": "dynamodb"}}
  ],
  "clusters": [
    {{
      "id": "frontend",
      "name": "Frontend Layer",
      "component_ids": ["api", "cdn"]
    }},
    {{
      "id": "backend",
      "name": "Backend Services",
      "component_ids": ["lambda1", "lambda2", "lambda3"]
    }}
  ],
  "connections": [
    {{"from_id": "api", "to_id": "lambda1"}},
    {{"from_id": "api", "to_id": "lambda2"}},
    {{"from_id": "api", "to_id": "lambda3"}},
    {{"from_id": "lambda1", "to_id": "db"}},
    {{"from_id": "lambda2", "to_id": "db"}},
    {{"from_id": "lambda3", "to_id": "db"}}
  ]
}}
{mcp_tools_instruction}
"""
    
    def generate_spec(self, description: str, provider: Optional[str] = None) -> ArchitectureSpec:
        """
        Generate ArchitectureSpec from natural language description.
        
        Args:
            description: Natural language architecture description
            provider: Optional provider hint from UI (aws, azure, gcp). 
                     If provided, this takes precedence over detection.
            
        Returns:
            ArchitectureSpec object
            
        Raises:
            ValueError: If input is invalid or out-of-context
        """
        # Validate input first
        is_valid, error_message = self.input_validator.validate(description)
        if not is_valid:
            raise ValueError(error_message)
        
        # Classify diagram type (pass provider if available)
        classification = self.classifier.classify(description, provider_hint=provider)
        
        # Use provider from UI if provided, otherwise use classification result
        final_provider = provider or classification.provider or "aws"
        
        prompt = f"""Parse this architecture description into an ArchitectureSpec:

{description}

Diagram Type: {classification.diagram_type}
Provider: {final_provider}

IMPORTANT: Use provider "{final_provider}" for all components. Use {final_provider.upper()} node types from the lists above.

Return a valid ArchitectureSpec JSON with components and connections."""
        
        response = self.agent(prompt)
        
        # Get structured output
        spec = response.structured_output
        
        # Set diagram type in metadata
        spec.metadata["diagram_type"] = classification.diagram_type
        
        # Set provider (UI selection takes precedence)
        spec.provider = final_provider
        
        # Enhance spec with AWS architectural guidance if AWS provider
        if final_provider == "aws":
            logger.info("[DIAGRAM_AGENT] Enhancing spec with AWS architectural advisor")
            spec = self.aws_advisor.enhance_spec(spec)
        
        # Optional: Post-process with MCP tools if enabled
        # This allows MCP server to validate/enhance the generated ArchitectureSpec
        if self.use_mcp_tools and final_provider == "aws":
            logger.info("[DIAGRAM_AGENT] Post-processing spec with MCP tools")
            spec = self._post_process_with_mcp(spec)
        
        return spec
    
    def _post_process_with_mcp(self, spec: ArchitectureSpec) -> ArchitectureSpec:
        """
        Post-process ArchitectureSpec using MCP tools.
        
        This generates Python code from the spec, validates/enhances it via MCP,
        and logs the results. The spec itself is not modified, but we log MCP feedback.
        
        Args:
            spec: ArchitectureSpec to post-process
            
        Returns:
            Original spec (MCP processing is for validation/logging only)
        """
        try:
            logger.info("[DIAGRAM_AGENT] === MCP Post-processing ===")
            logger.info(f"[DIAGRAM_AGENT] Spec: {len(spec.components)} components, {len(spec.connections)} connections")
            
            # Generate Python code from spec (for MCP validation)
            from ..generators.diagrams_engine import DiagramsEngine
            from ..resolvers.component_resolver import ComponentResolver
            
            resolver = ComponentResolver(primary_provider=spec.provider)
            engine = DiagramsEngine()
            
            # Generate code
            code = engine._generate_code(spec, resolver)
            logger.debug(f"[DIAGRAM_AGENT] Generated code length: {len(code)} characters")
            
            # Validate code via MCP
            validation_result = self.mcp_client.validate_code(code)
            if validation_result.get("valid"):
                logger.info("[DIAGRAM_AGENT] MCP code validation: PASSED")
                if validation_result.get("warnings"):
                    logger.warning(f"[DIAGRAM_AGENT] MCP validation warnings: {validation_result.get('warnings')}")
            else:
                logger.warning(f"[DIAGRAM_AGENT] MCP code validation: FAILED - {validation_result.get('error')}")
            
            # Generate diagram via MCP (for validation and actual diagram generation)
            # Note: MCP server generates PNG file, doesn't return enhanced code
            # Use spec title as filename (sanitized)
            import re
            safe_filename = re.sub(r'[^\w\-_\.]', '_', spec.title)[:50]  # Sanitize filename
            
            enhance_result = self.mcp_client.generate_diagram(
                code,
                filename=safe_filename,
                timeout=90  # Use default timeout
            )
            
            if enhance_result.get("success"):
                logger.info("[DIAGRAM_AGENT] MCP code enhancement: SUCCESS")
                logger.debug(f"[DIAGRAM_AGENT] Enhanced code available (length: {len(enhance_result.get('code', ''))})")
            else:
                logger.warning(f"[DIAGRAM_AGENT] MCP code enhancement: FAILED - {enhance_result.get('error')}")
            
            logger.info("[DIAGRAM_AGENT] === MCP Post-processing complete ===")
            
        except Exception as e:
            logger.error(f"[DIAGRAM_AGENT] Error in MCP post-processing: {e}", exc_info=True)
            # Don't fail the request if MCP processing fails
        
        return spec

