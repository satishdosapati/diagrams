"""
AWS Architectural Advisor - Uses AWS Knowledge Base MCP to provide architectural guidance.
"""
import os
from typing import Optional, List, Dict, Tuple
from ..models.spec import ArchitectureSpec, Component, Connection


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
        self.use_mcp = os.getenv("USE_AWS_MCP", "false").lower() == "true"
    
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
        if not self.use_mcp:
            return self._get_static_guidance()
        
        # TODO: Integrate with AWS Documentation MCP tools
        # For now, return static guidance
        return self._get_static_guidance()
    
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
        # Sort components by layer
        sorted_components = self.sort_components_by_layer(spec.components)
        
        # Get suggested connections
        suggested_conns, warnings = self.validate_connections(
            sorted_components,
            spec.connections
        )
        
        # Merge suggested connections (avoid duplicates)
        existing_conn_keys = {(c.from_id, c.to_id) for c in spec.connections}
        new_connections = spec.connections.copy()
        
        for suggested in suggested_conns:
            conn_key = (suggested.from_id, suggested.to_id)
            if conn_key not in existing_conn_keys:
                new_connections.append(suggested)
        
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
                "warnings": warnings
            }
        )
        
        return enhanced_spec

