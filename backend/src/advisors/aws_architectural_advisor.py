"""
AWS Architectural Advisor - Uses AWS Knowledge Base MCP to provide architectural guidance.
"""
import os
import logging
from typing import Optional, List, Dict, Tuple
from ..models.spec import ArchitectureSpec, Component, Connection

logger = logging.getLogger(__name__)


class AWSArchitecturalAdvisor:
    """Provides AWS architectural guidance using knowledge base."""
    
    # Component layer ordering (lower number = appears first/left in diagram)
    LAYER_ORDER = {
        # Internet/Edge Layer
        "route53": 0,
        "cloudfront": 1,
        "waf": 1,
        "shield": 1,
        
        # Network Layer
        "internet_gateway": 2,
        "vpc": 2,
        "vpn_gateway": 2,
        "direct_connect": 2,
        "transit_gateway": 2,
        "nat_gateway": 3,
        "subnet": 3,
        "private_subnet": 3,
        "public_subnet": 3,
        
        # Application/API Layer
        "api_gateway": 4,
        "app_sync": 4,
        "alb": 4,
        "elb": 4,
        "nlb": 4,
        
        # Compute Layer
        "lambda": 5,
        "ec2": 5,
        "ecs": 5,
        "eks": 5,
        "fargate": 5,
        "batch": 5,
        "elastic_beanstalk": 5,
        "lightsail": 5,
        
        # Integration Layer
        "sqs": 6,
        "sns": 6,
        "eventbridge": 6,
        "step_functions": 6,
        
        # Data Layer
        "s3": 7,
        "dynamodb": 7,
        "rds": 7,
        "aurora": 7,
        "redshift": 7,
        "elasticache": 7,
        "efs": 7,
        "ebs": 7,
        "glacier": 7,
        
        # Analytics Layer
        "kinesis": 8,
        "kinesis_data_streams": 8,
        "kinesis_data_firehose": 8,
        "athena": 8,
        "emr": 8,
        "glue": 8,
        "quicksight": 8,
        
        # Security/Management Layer
        "iam": 9,
        "kms": 9,
        "secrets_manager": 9,
        "cognito": 9,
        "cloudwatch": 9,
        "cloudformation": 9,
    }
    
    # Component dependencies (what should exist if this component exists)
    DEPENDENCIES = {
        "ec2": ["vpc", "subnet"],
        "rds": ["vpc", "subnet"],
        "aurora": ["vpc", "subnet"],
        "redshift": ["vpc", "subnet"],
        "elasticache": ["vpc", "subnet"],
        "lambda": [],  # Can exist without VPC (default VPC)
        "api_gateway": [],
        "s3": [],
        "dynamodb": [],
    }
    
    # Common architectural patterns
    PATTERNS = {
        "serverless": {
            "components": ["api_gateway", "lambda", "dynamodb"],
            "connections": [
                ("api_gateway", "lambda"),
                ("lambda", "dynamodb")
            ],
            "order": ["api_gateway", "lambda", "dynamodb"]
        },
        "three_tier": {
            "components": ["alb", "ec2", "rds"],
            "connections": [
                ("alb", "ec2"),
                ("ec2", "rds")
            ],
            "order": ["alb", "ec2", "rds"]
        },
        "microservices": {
            "components": ["alb", "ecs", "rds"],
            "connections": [
                ("alb", "ecs"),
                ("ecs", "rds")
            ],
            "order": ["alb", "ecs", "rds"]
        },
        "data_pipeline": {
            "components": ["s3", "glue", "athena", "quicksight"],
            "connections": [
                ("s3", "glue"),
                ("glue", "athena"),
                ("athena", "quicksight")
            ],
            "order": ["s3", "glue", "athena", "quicksight"]
        },
        "vpc_network": {
            "components": ["vpc", "internet_gateway", "subnet", "nat_gateway"],
            "connections": [
                ("vpc", "internet_gateway"),
                ("vpc", "subnet"),
                ("subnet", "nat_gateway")
            ],
            "order": ["vpc", "internet_gateway", "subnet", "nat_gateway"]
        }
    }
    
    def __init__(self):
        """Initialize the advisor."""
        # MCP implementation commented out for now
        # self.use_mcp = os.getenv("USE_AWS_MCP", "false").lower() == "true"
        self.use_mcp = False  # Always use static guidance
        logger.info(f"[ADVISOR] AWS Architectural Advisor initialized")
        logger.info(f"[ADVISOR] Static mode: Using static architectural guidance")
        # if self.use_mcp:
        #     logger.info("[ADVISOR] MCP mode: Queries will be logged and prepared for MCP server")
        # else:
        #     logger.info("[ADVISOR] Static mode: Using static architectural guidance")
    
    def get_layer_order(self, component_type: str) -> int:
        """Get the layer order for a component type."""
        node_id = component_type.lower().replace("_", "")
        return self.LAYER_ORDER.get(node_id, 5)  # Default to compute layer
    
    def sort_components_by_layer(self, components: List[Component]) -> List[Component]:
        """Sort components by architectural layer (left to right ordering)."""
        return sorted(components, key=lambda c: self.get_layer_order(c.get_node_id()))
    
    def suggest_missing_components(self, components: List[Component]) -> List[Dict]:
        """Suggest missing components based on dependencies."""
        suggestions = []
        component_types = {c.get_node_id() for c in components}
        
        for comp in components:
            node_id = comp.get_node_id()
            deps = self.DEPENDENCIES.get(node_id, [])
            
            for dep in deps:
                if dep not in component_types:
                    # Check if any similar component exists
                    has_similar = any(
                        dep in c.get_node_id() or c.get_node_id() in dep
                        for c in components
                    )
                    if not has_similar:
                        suggestions.append({
                            "type": dep,
                            "name": self._get_component_display_name(dep),
                            "reason": f"Required for {comp.name} ({node_id})"
                        })
        
        return suggestions
    
    def validate_connections(self, components: List[Component], connections: List[Connection]) -> Tuple[List[Connection], List[str]]:
        """Validate and suggest missing connections based on AWS patterns."""
        component_map = {c.id: c for c in components}
        existing_conns = {(c.from_id, c.to_id) for c in connections}
        suggested_conns = []
        warnings = []
        
        # Check for VPC containment patterns
        vpc_components = [c for c in components if c.get_node_id() == "vpc"]
        subnet_components = [c for c in components if "subnet" in c.get_node_id()]
        ec2_components = [c for c in components if c.get_node_id() == "ec2"]
        
        # VPC should contain subnets
        for vpc in vpc_components:
            for subnet in subnet_components:
                conn_key = (vpc.id, subnet.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=vpc.id,
                        to_id=subnet.id,
                        label="contains"
                    ))
        
        # Subnets should contain EC2 instances
        for subnet in subnet_components:
            for ec2 in ec2_components:
                conn_key = (subnet.id, ec2.id)
                if conn_key not in existing_conns:
                    # Check if EC2 is already connected to something else
                    has_connection = any(c.from_id == ec2.id or c.to_id == ec2.id for c in connections)
                    if not has_connection:
                        suggested_conns.append(Connection(
                            from_id=subnet.id,
                            to_id=ec2.id,
                            label="contains"
                        ))
        
        # Check for common patterns
        api_gateway = next((c for c in components if c.get_node_id() == "api_gateway"), None)
        lambda_funcs = [c for c in components if c.get_node_id() == "lambda"]
        dynamodb = next((c for c in components if c.get_node_id() == "dynamodb"), None)
        
        # Serverless pattern: API Gateway → Lambda → DynamoDB
        if api_gateway and lambda_funcs:
            for lambda_func in lambda_funcs:
                conn_key = (api_gateway.id, lambda_func.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=api_gateway.id,
                        to_id=lambda_func.id
                    ))
        
        if lambda_funcs and dynamodb:
            for lambda_func in lambda_funcs:
                conn_key = (lambda_func.id, dynamodb.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=lambda_func.id,
                        to_id=dynamodb.id
                    ))
        
        # Check for ALB → EC2 pattern
        alb = next((c for c in components if c.get_node_id() == "alb"), None)
        if alb and ec2_components:
            for ec2 in ec2_components:
                conn_key = (alb.id, ec2.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=alb.id,
                        to_id=ec2.id
                    ))
        
        return suggested_conns, warnings
    
    def get_architectural_guidance(self, description: str) -> str:
        """Get architectural guidance from AWS knowledge base (if MCP enabled)."""
        # MCP implementation commented out - always use static guidance
        # if not self.use_mcp:
        #     logger.debug("MCP disabled, using static guidance")
        #     return self._get_static_guidance()
        
        # Use enhanced static guidance with context
        enhanced_guidance = self._get_enhanced_guidance_with_context(description)
        return enhanced_guidance
        
        # MCP implementation commented out for now
        # # Use AWS Documentation MCP tools
        # logger.info("Querying AWS Documentation MCP for architectural guidance")
        # try:
        #     # Search for relevant AWS architecture patterns
        #     search_query = f"AWS architecture patterns best practices {description}"
        #     logger.info(f"MCP Search Query: {search_query}")
        #     
        #     # Note: MCP tools are available in the environment, but we need to import them
        #     # For now, we'll use a try-except to handle if MCP tools aren't available
        #     try:
        #         # Try to use AWS Documentation MCP search
        #         # This would be: mcp_AWS_Documentation_search_documentation
        #         # But we need to check if it's available in the current context
        #         logger.info("Attempting to query AWS Documentation MCP...")
        #         
        #         # Since MCP tools are provided by the environment, we'll use a fallback approach
        #         # In a real implementation, you'd call the MCP tool directly
        #         # For now, we'll enhance static guidance with description context
        #         enhanced_guidance = self._get_enhanced_guidance_with_context(description)
        #         logger.info("MCP guidance retrieved successfully")
        #         return enhanced_guidance
        #         
        #     except Exception as e:
        #         logger.warning(f"MCP query failed, falling back to static guidance: {str(e)}")
        #         return self._get_static_guidance()
        #         
        # except Exception as e:
        #     logger.error(f"Error getting architectural guidance: {str(e)}", exc_info=True)
        #     return self._get_static_guidance()
    
    def _get_enhanced_guidance_with_context(self, description: str) -> str:
        """Get enhanced guidance based on description context."""
        description_lower = description.lower()
        
        # Identify key components mentioned
        components_mentioned = []
        if "vpc" in description_lower or "network" in description_lower:
            components_mentioned.append("VPC")
        if "ec2" in description_lower or "instance" in description_lower:
            components_mentioned.append("EC2")
        if "lambda" in description_lower or "function" in description_lower:
            components_mentioned.append("Lambda")
        if "rds" in description_lower or "database" in description_lower:
            components_mentioned.append("RDS")
        if "api" in description_lower or "gateway" in description_lower:
            components_mentioned.append("API Gateway")
        
        base_guidance = self._get_static_guidance()
        
        if components_mentioned:
            context_note = f"\n\nBased on your description mentioning {', '.join(components_mentioned)}:\n"
            context_note += "- Ensure proper component ordering and connections\n"
            context_note += "- Follow AWS best practices for these components\n"
            return base_guidance + context_note
        
        return base_guidance
    
    # MCP implementation commented out for now
    # def query_aws_mcp(self, query: str) -> Optional[str]:
    #     """
    #     Query AWS Documentation MCP for architectural guidance.
    #     
    #     Note: MCP tools are invoked through the MCP protocol/server.
    #     This method logs the query but actual MCP invocation happens
    #     at the agent level where MCP tools are available.
    #     """
    #     if not self.use_mcp:
    #         logger.debug("MCP disabled, skipping query")
    #         return None
    #     
    #     logger.info(f"[MCP] Querying AWS Documentation: {query}")
    #     
    #     # MCP tools are invoked through the MCP server protocol
    #     # The actual invocation happens when the agent uses MCP tools
    #     # We log here to track what would be queried
    #     logger.info(f"[MCP] Query prepared: {query}")
    #     logger.info("[MCP] Note: MCP tools are invoked by the agent, not directly here")
    #     
    #     # Return None - actual MCP calls happen at agent level
    #     # The agent can use MCP tools in its prompts/tools
    #     return None
    
    def _get_static_guidance(self) -> str:
        """Get static architectural guidance."""
        return """
AWS Architectural Best Practices:

1. Component Ordering (Left to Right):
   - Internet/Edge: Route53, CloudFront, WAF
   - Network: VPC, Internet Gateway, Subnets, NAT Gateway
   - Application: API Gateway, ALB, ELB
   - Compute: Lambda, EC2, ECS, EKS
   - Integration: SQS, SNS, EventBridge
   - Data: S3, DynamoDB, RDS, Aurora
   - Analytics: Kinesis, Athena, EMR
   - Security/Management: IAM, KMS, CloudWatch

2. Connection Patterns:
   - VPC contains Subnets (VPC → Subnet)
   - Subnets contain EC2 instances (Subnet → EC2)
   - API Gateway connects to Lambda (API Gateway → Lambda)
   - Lambda connects to DynamoDB (Lambda → DynamoDB)
   - ALB connects to EC2/ECS (ALB → EC2/ECS)
   - EC2/ECS connects to RDS (EC2/ECS → RDS)

3. Common Patterns:
   - Serverless: API Gateway → Lambda → DynamoDB
   - Three-Tier: ALB → EC2 → RDS
   - Microservices: ALB → ECS → RDS
   - Data Pipeline: S3 → Glue → Athena → QuickSight
   - VPC Network: VPC → Internet Gateway → Subnet → NAT Gateway

4. Dependencies:
   - EC2 requires VPC and Subnet
   - RDS requires VPC and Subnet
   - Lambda can use default VPC or custom VPC
   - API Gateway is regional (no VPC required)
"""
    
    def _get_component_display_name(self, node_id: str) -> str:
        """Get display name for a component type."""
        names = {
            "vpc": "VPC",
            "subnet": "Subnet",
            "internet_gateway": "Internet Gateway",
            "nat_gateway": "NAT Gateway",
            "security_group": "Security Group",
        }
        return names.get(node_id, node_id.replace("_", " ").title())
    
    def enhance_spec(self, spec: ArchitectureSpec) -> ArchitectureSpec:
        """Enhance spec with ordering and suggested connections."""
        logger.info(f"[ADVISOR] === Starting spec enhancement ===")
        logger.info(f"[ADVISOR] Components: {len(spec.components)}, Connections: {len(spec.connections)}")
        # MCP implementation commented out for now
        # logger.info(f"[ADVISOR] MCP enabled: {self.use_mcp}")
        
        # MCP implementation commented out for now
        # # If MCP enabled, prepare query
        # if self.use_mcp:
        #     component_types = [c.get_node_id() for c in spec.components]
        #     mcp_query = f"AWS architecture best practices for {', '.join(component_types[:5])}"
        #     logger.info(f"[MCP] === MCP Query Prepared ===")
        #     logger.info(f"[MCP] Query: {mcp_query}")
        #     logger.info(f"[MCP] Note: MCP tools would be invoked here via MCP server")
        #     self.query_aws_mcp(mcp_query)
        
        # Sort components by layer
        logger.info(f"[ADVISOR] Sorting components by architectural layer...")
        sorted_components = self.sort_components_by_layer(spec.components)
        logger.debug(f"[ADVISOR] Sorted order: {[c.get_node_id() for c in sorted_components]}")
        
        # Get suggested connections
        logger.info(f"[ADVISOR] Validating connections and suggesting missing ones...")
        suggested_conns, warnings = self.validate_connections(
            sorted_components,
            spec.connections
        )
        logger.info(f"[ADVISOR] Suggested {len(suggested_conns)} additional connections")
        
        if warnings:
            logger.warning(f"[ADVISOR] Warnings: {warnings}")
        
        # Merge suggested connections (avoid duplicates)
        existing_conn_keys = {(c.from_id, c.to_id) for c in spec.connections}
        new_connections = spec.connections.copy()
        
        for suggested in suggested_conns:
            conn_key = (suggested.from_id, suggested.to_id)
            if conn_key not in existing_conn_keys:
                new_connections.append(suggested)
                logger.debug(f"[ADVISOR] Added: {suggested.from_id} → {suggested.to_id}")
        
        # Create enhanced spec
        enhanced_spec = ArchitectureSpec(
            title=spec.title,
            provider=spec.provider,
            is_multi_cloud=spec.is_multi_cloud,
            components=sorted_components,
            connections=new_connections,
            metadata={
                **spec.metadata,
                "enhanced": True,
                "warnings": warnings,
                "advisor_consulted": True,
                # "mcp_enabled": self.use_mcp  # MCP implementation commented out
                "mcp_enabled": False
            }
        )
        
        logger.info(f"[ADVISOR] === Enhancement complete ===")
        logger.info(f"[ADVISOR] Final: {len(sorted_components)} components, {len(new_connections)} connections")
        return enhanced_spec

