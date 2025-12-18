"""
AWS Architectural Advisor - Uses AWS Knowledge Base MCP to provide architectural guidance.
"""
import os
import logging
from typing import Optional, List, Dict, Tuple
from ..models.spec import ArchitectureSpec, Component, Connection, Cluster, GraphvizAttributes

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
        
        # VPC should contain subnets - use bidirectional connection for containment
        for vpc in vpc_components:
            for subnet in subnet_components:
                conn_key = (vpc.id, subnet.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=vpc.id,
                        to_id=subnet.id,
                        label="contains",
                        direction="bidirectional",  # Containment is bidirectional relationship
                        graphviz_attrs={"style": "dashed", "arrowhead": "none"}  # Dashed, no arrowhead for containment
                    ))
        
        # Subnets should contain EC2 instances - use bidirectional connection for containment
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
                            label="contains",
                            direction="bidirectional",  # Containment is bidirectional relationship
                            graphviz_attrs={"style": "dashed", "arrowhead": "none"}  # Dashed, no arrowhead for containment
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
        
        # Check for routing relationships (Internet Gateway → Public Subnet, NAT Gateway → Private Subnet)
        internet_gateway = next((c for c in components if c.get_node_id() == "internet_gateway"), None)
        nat_gateway = next((c for c in components if c.get_node_id() == "nat_gateway"), None)
        public_subnets = [c for c in subnet_components if "public" in c.get_node_id() or "public" in c.name.lower()]
        private_subnets = [c for c in subnet_components if "private" in c.get_node_id() or "private" in c.name.lower()]
        
        # Internet Gateway routes to Public Subnets
        if internet_gateway and public_subnets:
            for subnet in public_subnets:
                conn_key = (internet_gateway.id, subnet.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=internet_gateway.id,
                        to_id=subnet.id,
                        label="routes to",
                        direction="forward",
                        graphviz_attrs={"style": "solid", "color": "blue"}
                    ))
        
        # NAT Gateway provides internet to Private Subnets
        if nat_gateway and private_subnets:
            for subnet in private_subnets:
                conn_key = (nat_gateway.id, subnet.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=nat_gateway.id,
                        to_id=subnet.id,
                        label="provides internet to",
                        direction="forward",
                        graphviz_attrs={"style": "solid", "color": "blue"}
                    ))
        
        # Add warnings for best practices
        if vpc_components and subnet_components:
            # Check if subnets are in multiple AZs (best practice)
            subnet_azs = set()
            for subnet in subnet_components:
                # Try to detect AZ from name (e.g., "Public Subnet AZ1", "Private Subnet us-east-1a")
                name_lower = subnet.name.lower()
                if "az" in name_lower or "availability zone" in name_lower:
                    # Extract AZ identifier if present
                    import re
                    az_match = re.search(r'(az|availability zone)[\s-]?([a-z0-9]+)', name_lower)
                    if az_match:
                        subnet_azs.add(az_match.group(2))
            
            if len(subnet_azs) < 2 and len(subnet_components) >= 2:
                warnings.append("Consider deploying subnets across multiple Availability Zones for high availability (AWS best practice)")
        
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
        """Get static architectural guidance based on AWS Well-Architected Framework."""
        return """
AWS Architectural Best Practices (Based on AWS Well-Architected Framework):

1. Component Ordering (Left to Right):
   - Internet/Edge: Route53, CloudFront, WAF
   - Network: VPC, Internet Gateway, Subnets, NAT Gateway
   - Application: API Gateway, ALB, ELB
   - Compute: Lambda, EC2, ECS, EKS
   - Integration: SQS, SNS, EventBridge
   - Data: S3, DynamoDB, RDS, Aurora
   - Analytics: Kinesis, Athena, EMR
   - Security/Management: IAM, KMS, CloudWatch

2. VPC Network Best Practices:
   - Create subnets in multiple Availability Zones for high availability
   - Use security groups to control traffic to EC2 instances
   - Use network ACLs to control traffic at subnet level
   - Use VPC Flow Logs for monitoring network traffic
   - Plan IP subnet allocation accounting for expansion
   - Prefer hub-and-spoke topologies over many-to-many mesh
   - Ensure non-overlapping private IP address ranges

3. Connection Patterns:
   - VPC contains Subnets (containment relationship, not data flow)
   - Subnets contain EC2 instances (containment relationship)
   - Internet Gateway routes to Public Subnets (routing relationship)
   - NAT Gateway provides internet to Private Subnets (routing relationship)
   - API Gateway connects to Lambda (data flow)
   - Lambda connects to DynamoDB (data flow)
   - ALB connects to EC2/ECS (data flow)
   - EC2/ECS connects to RDS (data flow)

4. Common Patterns:
   - Serverless: API Gateway → Lambda → DynamoDB
   - Three-Tier: ALB → EC2 → RDS
   - Microservices: ALB → ECS → RDS
   - Data Pipeline: S3 → Glue → Athena → QuickSight
   - VPC Network: VPC contains Subnets, Internet Gateway routes to Public Subnets

5. Dependencies:
   - EC2 requires VPC and Subnet (deploy in multiple AZs)
   - RDS requires VPC and Subnet (use Multi-AZ for HA)
   - Lambda can use default VPC or custom VPC
   - API Gateway is regional (no VPC required)

6. Security Best Practices:
   - Use security groups for instance-level traffic control
   - Use network ACLs for subnet-level traffic control
   - Enable VPC Flow Logs for network monitoring
   - Use IAM for access management
   - Consider AWS Network Firewall for advanced filtering
   - Use Amazon GuardDuty for threat detection
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
        
        # Enforce canonical patterns (remove anti-patterns)
        logger.info(f"[ADVISOR] Enforcing canonical architectural patterns...")
        new_connections = self._enforce_canonical_patterns(new_connections, sorted_components)
        
        # Add connection labels based on patterns
        logger.info(f"[ADVISOR] Adding connection labels for clarity...")
        new_connections = self._add_connection_labels(new_connections, sorted_components)
        labeled_count = sum(1 for c in new_connections if c.label)
        logger.info(f"[ADVISOR] Added labels to {labeled_count} out of {len(new_connections)} connections")
        
        # Enhance component names with full AWS service names and subtitles
        logger.info(f"[ADVISOR] Enhancing component names with full AWS service names...")
        sorted_components = self._enhance_component_names(sorted_components)
        
        # Post-process connections to style them based on relationship type
        new_connections = self._style_connections_by_type(new_connections, sorted_components)
        
        # Auto-create clusters if none exist and we have enough components
        auto_clusters = []
        if not spec.clusters and len(sorted_components) >= 3:
            logger.info(f"[ADVISOR] Auto-creating clusters for better organization...")
            auto_clusters = self._auto_create_clusters(sorted_components)
            if auto_clusters:
                logger.info(f"[ADVISOR] Created {len(auto_clusters)} clusters")
        
        # Skip blank node optimization - with strict orthogonal routing (splines="ortho"),
        # blank nodes create convoluted paths instead of simplifying them.
        # Orthogonal routing handles edge routing better on its own.
        final_components = sorted_components
        final_connections = new_connections
        final_clusters = auto_clusters if auto_clusters else spec.clusters
        
        # DISABLED: Blank node optimization conflicts with orthogonal routing
        # With splines="ortho", Graphviz handles routing better without intermediate waypoints
        # Blank nodes were useful for curved routing but create unnecessary complexity with orthogonal routing
        # if final_clusters and len(new_connections) >= 5:
        #     logger.info(f"[ADVISOR] Optimizing edges with blank nodes...")
        #     optimized_components, optimized_connections = self._optimize_edges_with_blank_nodes(...)
        #     ...
        
        # Prepare graphviz attributes for better edge routing
        graphviz_attrs = spec.graphviz_attrs
        if not graphviz_attrs:
            graphviz_attrs = GraphvizAttributes()
        
        # Always apply strict orthogonal routing for clean, structured lines
        # This ensures all connectors use 90-degree angles (orthogonal routing)
        # Matching the clean, structured appearance of professional AWS diagrams
        logger.info(f"[ADVISOR] Applying strict orthogonal routing for clean structured lines ({len(final_connections)} connections)...")
        
        # CRITICAL: Always use "ortho" for strict 90-degree angle connectors
        # This produces clean, structured lines like professional architecture diagrams
        if "splines" not in graphviz_attrs.graph_attr:
            graphviz_attrs.graph_attr["splines"] = "ortho"
        
        # CRITICAL: Prevent node overlaps - required for proper orthogonal routing
        # Without this, Graphviz may revert to curved/spline routing
        if "overlap" not in graphviz_attrs.graph_attr:
            graphviz_attrs.graph_attr["overlap"] = "false"
        
        # Always enforce left-to-right direction for all architecture diagrams
        # This ensures a clear, consistent flow from left to right, matching professional diagram conventions
        spec.direction = "LR"
        # Also set rankdir in graph_attr for Graphviz compatibility
        graphviz_attrs.graph_attr["rankdir"] = "LR"
        
        # Improve spacing for better edge routing (always apply if not set)
        # Increased spacing helps orthogonal routing work better and prevents crowding
        if "nodesep" not in graphviz_attrs.graph_attr:
            graphviz_attrs.graph_attr["nodesep"] = "1.0"  # Increased from 0.8 for better spacing
        if "ranksep" not in graphviz_attrs.graph_attr:
            graphviz_attrs.graph_attr["ranksep"] = "2.0"  # Increased from 1.2 for better spacing
        
        # For complex diagrams with many connections, merge parallel edges
        # This reduces visual clutter when multiple sources connect to the same target
        if len(final_connections) > 10:
            if "concentrate" not in graphviz_attrs.graph_attr:
                graphviz_attrs.graph_attr["concentrate"] = "true"
        
        # Set default edge attributes for cleaner appearance (always apply if not set)
        if not graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr = {}
        if "arrowsize" not in graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr["arrowsize"] = "0.8"
        if "penwidth" not in graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr["penwidth"] = "1.0"
        
        # Set label positioning attributes for edge labels (connectors)
        # CRITICAL: With orthogonal routing (splines=ortho), labels can be scattered across
        # different segments of the multi-segment path. These settings improve consistency:
        
        # labeldistance: Distance from edge (lower = closer, default 1.0)
        # Increased to 1.5 for better visibility and to reduce overlap with edge segments
        if "labeldistance" not in graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr["labeldistance"] = "1.5"
        # labelfontsize: Font size for edge labels
        if "labelfontsize" not in graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr["labelfontsize"] = "9"  # Slightly smaller to reduce clutter
        # labelloc: Label position relative to edge (t=top, c=center, b=bottom)
        if "labelloc" not in graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr["labelloc"] = "c"  # Center label on edge
        # labelangle: Angle of label text relative to edge (0=horizontal, positive=clockwise)
        # For orthogonal edges, slight angle (-25) works better than horizontal (0)
        # This prevents labels from being placed at different segments of the path
        if "labelangle" not in graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr["labelangle"] = "-25"  # Slight angle for better positioning
        # labelpos: Position along edge path (0=start, 0.5=middle, 1=end)
        # Forces labels to middle of edge path for consistent placement with orthogonal routing
        if "labelpos" not in graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr["labelpos"] = "0.5"  # Middle of edge
        # labelfloat: Allow label to float for better placement (true/false)
        # Enables Graphviz to find better positions for labels with orthogonal routing
        if "labelfloat" not in graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr["labelfloat"] = "true"
        # decorate: Draw line from label to edge (true/false)
        # Set to false to avoid extra decoration lines that can clutter orthogonal diagrams
        if "decorate" not in graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr["decorate"] = "false"
        
        # Set default node attributes for label positioning (always apply if not set)
        if not graphviz_attrs.node_attr:
            graphviz_attrs.node_attr = {}
        # labelloc: Label position relative to node (t=top, b=bottom, l=left, r=right, c=center)
        if "labelloc" not in graphviz_attrs.node_attr:
            graphviz_attrs.node_attr["labelloc"] = "b"  # Below icon
        # labeldistance: Distance from node (lower = closer)
        if "labeldistance" not in graphviz_attrs.node_attr:
            graphviz_attrs.node_attr["labeldistance"] = "0.3"  # Closer to icon
        
        logger.info(f"[ADVISOR] Edge routing: splines={graphviz_attrs.graph_attr.get('splines')}, overlap={graphviz_attrs.graph_attr.get('overlap')}, rankdir={graphviz_attrs.graph_attr.get('rankdir')}, concentrate={graphviz_attrs.graph_attr.get('concentrate', 'false')}")
        
        # Create enhanced spec
        enhanced_spec = ArchitectureSpec(
            title=spec.title,
            provider=spec.provider,
            is_multi_cloud=spec.is_multi_cloud,
            components=final_components,
            connections=final_connections,
            clusters=final_clusters,
            graphviz_attrs=graphviz_attrs,
            direction=spec.direction,
            outformat=spec.outformat,
            metadata={
                **spec.metadata,
                "enhanced": True,
                "warnings": warnings,
                "advisor_consulted": True,
                "auto_clustered": bool(auto_clusters),
                "edge_optimized": len(final_components) > len(sorted_components),
                # "mcp_enabled": self.use_mcp  # MCP implementation commented out
                "mcp_enabled": False
            }
        )
        
        logger.info(f"[ADVISOR] === Enhancement complete ===")
        labeled_conns = sum(1 for c in final_connections if c.label)
        logger.info(f"[ADVISOR] Final: {len(sorted_components)} components, {len(new_connections)} connections ({labeled_conns} with labels), {len(enhanced_spec.clusters)} clusters")
        return enhanced_spec
    
    def _auto_create_clusters(self, components: List[Component]) -> List[Cluster]:
        """
        Automatically create clusters based on component types and architectural layers.
        
        Clustering strategy:
        1. Detect architectural pattern (event-driven, data pipeline, microservices, etc.)
        2. Use pattern-specific cluster names for better clarity
        3. Group by architectural layer (Frontend, Backend, Data, etc.)
        4. Group VPC-related components hierarchically
        5. Group similar component types (all databases, all compute, etc.)
        
        Args:
            components: List of components to cluster
            
        Returns:
            List of Cluster objects
        """
        clusters = []
        component_ids = {c.id for c in components}
        
        # Detect architectural pattern
        node_ids = [c.get_node_id() for c in components]
        has_eventbridge = "eventbridge" in node_ids
        has_kinesis = any(nid in {"kinesis", "kinesis_data_streams"} for nid in node_ids)
        has_api_gateway = "api_gateway" in node_ids
        has_multiple_lambdas = node_ids.count("lambda") >= 2
        has_vpc = "vpc" in node_ids
        
        # Determine pattern-specific cluster names
        if has_eventbridge:
            # Event-Driven pattern
            layer_names = {
                "Frontend/Edge": "Event Sources",
                "Network": "Network",
                "Application": "Application",
                "Compute": "Event Processing",
                "Integration": "Integration",
                "Data": "Event Storage",
                "Analytics": "Analytics",
                "Security/Management": "Security/Management"
            }
        elif has_kinesis:
            # Data Pipeline pattern
            layer_names = {
                "Frontend/Edge": "Data Sources",
                "Network": "Network",
                "Application": "Application",
                "Compute": "Processing Layer",
                "Integration": "Integration",
                "Data": "Storage Layer",
                "Analytics": "Analytics Layer",
                "Security/Management": "Security/Management"
            }
        elif has_api_gateway and has_multiple_lambdas:
            # Microservices pattern
            layer_names = {
                "Frontend/Edge": "API Layer",
                "Network": "Network",
                "Application": "Application",
                "Compute": "Service Layer",
                "Integration": "Integration",
                "Data": "Data Layer",
                "Analytics": "Analytics",
                "Security/Management": "Security/Management"
            }
        elif has_api_gateway:
            # Serverless pattern
            layer_names = {
                "Frontend/Edge": "API Layer",
                "Network": "Network",
                "Application": "Application",
                "Compute": "Compute Layer",
                "Integration": "Integration",
                "Data": "Data Layer",
                "Analytics": "Analytics",
                "Security/Management": "Security/Management"
            }
        elif has_vpc:
            # Network pattern
            layer_names = {
                "Frontend/Edge": "Public Layer",
                "Network": "Network",
                "Application": "Application",
                "Compute": "Compute",
                "Integration": "Integration",
                "Data": "Private Layer",
                "Analytics": "Analytics",
                "Security/Management": "Security/Management"
            }
        else:
            # Default layer names
            layer_names = {
                "Frontend/Edge": "Frontend/Edge",
                "Network": "Network",
                "Application": "Application",
                "Compute": "Compute",
                "Integration": "Integration",
                "Data": "Data",
                "Analytics": "Analytics",
                "Security/Management": "Security/Management"
            }
        
        # Group components by layer
        layer_groups = {
            "Frontend/Edge": [],
            "Network": [],
            "Application": [],
            "Compute": [],
            "Integration": [],
            "Data": [],
            "Analytics": [],
            "Security/Management": []
        }
        
        for comp in components:
            node_id = comp.get_node_id()
            layer_order = self.get_layer_order(node_id)
            
            if layer_order == 0 or layer_order == 1:
                layer_groups["Frontend/Edge"].append(comp.id)
            elif layer_order == 2 or layer_order == 3:
                layer_groups["Network"].append(comp.id)
            elif layer_order == 4:
                layer_groups["Application"].append(comp.id)
            elif layer_order == 5:
                layer_groups["Compute"].append(comp.id)
            elif layer_order == 6:
                layer_groups["Integration"].append(comp.id)
            elif layer_order == 7:
                layer_groups["Data"].append(comp.id)
            elif layer_order == 8:
                layer_groups["Analytics"].append(comp.id)
            elif layer_order == 9:
                layer_groups["Security/Management"].append(comp.id)
        
        # Create clusters for layers with 2+ components
        cluster_id_counter = 1
        for layer_key, comp_ids in layer_groups.items():
            if len(comp_ids) >= 2:
                cluster_id = f"cluster_{cluster_id_counter}"
                # Use pattern-specific name if available
                cluster_name = layer_names.get(layer_key, layer_key)
                clusters.append(Cluster(
                    id=cluster_id,
                    name=cluster_name,
                    component_ids=comp_ids,
                    parent_id=None
                ))
                cluster_id_counter += 1
                logger.debug(f"[ADVISOR] Created cluster: {cluster_name} with {len(comp_ids)} components")
        
        # Special handling: VPC hierarchy
        vpc_components = [c for c in components if c.get_node_id() == "vpc"]
        subnet_components = [c for c in components if "subnet" in c.get_node_id()]
        vpc_related = [c for c in components if c.get_node_id() in ["nat_gateway", "internet_gateway"]]
        
        if vpc_components and (subnet_components or vpc_related):
            # Check if VPC components are already in a cluster
            vpc_in_cluster = False
            for cluster in clusters:
                if vpc_components[0].id in cluster.component_ids:
                    vpc_in_cluster = True
                    # Add VPC-related components to this cluster
                    for comp in subnet_components + vpc_related:
                        if comp.id not in cluster.component_ids:
                            cluster.component_ids.append(comp.id)
                    break
            
            if not vpc_in_cluster:
                # Create VPC cluster
                vpc_cluster_ids = [c.id for c in vpc_components + subnet_components + vpc_related]
                if len(vpc_cluster_ids) >= 2:
                    clusters.append(Cluster(
                        id=f"cluster_{cluster_id_counter}",
                        name="VPC Network",
                        component_ids=vpc_cluster_ids,
                        parent_id=None
                    ))
                    cluster_id_counter += 1
        
        # If we have many components but no good clusters, try grouping by type
        if not clusters and len(components) >= 4:
            # Group by component type
            type_groups = {}
            for comp in components:
                node_id = comp.get_node_id()
                if node_id not in type_groups:
                    type_groups[node_id] = []
                type_groups[node_id].append(comp.id)
            
            # Create clusters for types with 2+ components
            for node_type, comp_ids in type_groups.items():
                if len(comp_ids) >= 2:
                    type_name = node_type.replace("_", " ").title()
                    clusters.append(Cluster(
                        id=f"cluster_{cluster_id_counter}",
                        name=f"{type_name} Services",
                        component_ids=comp_ids,
                        parent_id=None
                    ))
                    cluster_id_counter += 1
        
        return clusters
    
    def _optimize_edges_with_blank_nodes(self, spec: ArchitectureSpec) -> Tuple[List[Component], List[Connection]]:
        """
        Intelligently insert blank nodes to reduce edge clutter.
        
        Detects patterns that benefit from blank nodes:
        - Multiple connections between clusters
        - Fan-out patterns (one source → many targets)
        - Fan-in patterns (many sources → one target)
        - Cluster-to-cluster connections
        
        Args:
            spec: Architecture specification
            
        Returns:
            Tuple of (new_components, new_connections) with blank nodes inserted
        """
        new_components = list(spec.components)
        new_connections = list(spec.connections)
        
        if not spec.clusters or len(spec.connections) < 5:
            # Not enough complexity to benefit from blank nodes
            return new_components, new_connections
        
        # Build cluster membership map
        component_to_cluster = {}
        for cluster in spec.clusters:
            for comp_id in cluster.component_ids:
                component_to_cluster[comp_id] = cluster.id
        
        # Detect cluster-to-cluster connections
        cluster_connections = {}
        for conn in spec.connections:
            from_cluster = component_to_cluster.get(conn.from_id)
            to_cluster = component_to_cluster.get(conn.to_id)
            
            if from_cluster and to_cluster and from_cluster != to_cluster:
                key = (from_cluster, to_cluster)
                if key not in cluster_connections:
                    cluster_connections[key] = []
                cluster_connections[key].append(conn)
        
        # Insert blank nodes for cluster-to-cluster connections with 2+ edges
        blank_node_counter = 1
        processed_connections = set()
        
        for (from_cluster_id, to_cluster_id), conns in cluster_connections.items():
            if len(conns) >= 2:
                # Create blank node
                blank_id = f"blank_{blank_node_counter}"
                blank_node = Component(
                    id=blank_id,
                    name="",
                    type="blank",
                    is_blank_node=True,
                    graphviz_attrs={
                        "shape": "plaintext",
                        "width": "0",
                        "height": "0"
                    }
                )
                new_components.append(blank_node)
                
                # Replace direct connections with connections via blank node
                for conn in conns:
                    if (conn.from_id, conn.to_id) not in processed_connections:
                        # Remove original connection
                        new_connections.remove(conn)
                        processed_connections.add((conn.from_id, conn.to_id))
                        
                        # Add connection from source to blank node
                        new_connections.append(Connection(
                            from_id=conn.from_id,
                            to_id=blank_id,
                            label=conn.label,
                            graphviz_attrs=conn.graphviz_attrs,
                            direction=conn.direction
                        ))
                        
                        # Add connection from blank node to target
                        new_connections.append(Connection(
                            from_id=blank_id,
                            to_id=conn.to_id,
                            direction="forward"
                        ))
                
                blank_node_counter += 1
        
        # Detect fan-out patterns (one source → many targets in same cluster)
        source_targets = {}
        for conn in new_connections:
            if conn.from_id not in source_targets:
                source_targets[conn.from_id] = []
            source_targets[conn.from_id].append(conn.to_id)
        
        for source_id, target_ids in source_targets.items():
            if len(target_ids) >= 3:
                # Check if targets are in the same cluster
                target_clusters = [component_to_cluster.get(tid) for tid in target_ids]
                if len(set(target_clusters)) == 1 and target_clusters[0]:  # All in same cluster
                    # Create blank node for fan-out
                    blank_id = f"blank_{blank_node_counter}"
                    blank_node = Component(
                        id=blank_id,
                        name="",
                        type="blank",
                        is_blank_node=True,
                        graphviz_attrs={
                            "shape": "plaintext",
                            "width": "0",
                            "height": "0"
                        }
                    )
                    new_components.append(blank_node)
                    
                    # Replace connections
                    for target_id in target_ids:
                        # Find and replace connection
                        for conn in new_connections[:]:
                            if conn.from_id == source_id and conn.to_id == target_id:
                                new_connections.remove(conn)
                                # Add connection via blank node
                                new_connections.append(Connection(
                                    from_id=source_id,
                                    to_id=blank_id,
                                    direction="forward"
                                ))
                                new_connections.append(Connection(
                                    from_id=blank_id,
                                    to_id=target_id,
                                    direction="forward"
                                ))
                    
                    blank_node_counter += 1
        
        return new_components, new_connections
    
    def _enforce_canonical_patterns(self, connections: List[Connection], components: List[Component]) -> List[Connection]:
        """
        Enforce canonical architectural patterns by removing anti-patterns.
        
        Patterns enforced:
        - Event-Driven: Remove direct source-to-processor connections when EventBridge exists
        - Serverless: Ensure API Gateway → Lambda → DynamoDB order
        - Microservices: Ensure API Gateway → Services → Database order
        
        Args:
            connections: List of connections
            components: List of components
            
        Returns:
            Filtered list of connections with anti-patterns removed
        """
        component_map = {c.id: c for c in components}
        node_id_map = {c.id: c.get_node_id() for c in components}
        
        # Detect EventBridge pattern
        eventbridge_components = [c.id for c in components if c.get_node_id() == "eventbridge"]
        
        if eventbridge_components:
            eventbridge_id = eventbridge_components[0]
            logger.info(f"[ADVISOR] EventBridge detected, enforcing canonical event-driven pattern")
            
            # Find event sources (S3, API Gateway, IoT, etc.)
            event_source_types = {"s3", "api_gateway", "iot_core", "lambda"}
            event_sources = [c.id for c in components if c.get_node_id() in event_source_types]
            
            # Find processors (Lambda functions)
            processors = [c.id for c in components if c.get_node_id() == "lambda"]
            
            # Remove direct source-to-processor connections (should go through EventBridge)
            filtered_connections = []
            removed_count = 0
            
            for conn in connections:
                from_node_id = node_id_map.get(conn.from_id)
                to_node_id = node_id_map.get(conn.to_id)
                
                # Check if this is a direct source-to-processor connection
                is_direct_bypass = (
                    conn.from_id in event_sources and 
                    conn.to_id in processors and
                    conn.from_id != eventbridge_id and
                    conn.to_id != eventbridge_id
                )
                
                if is_direct_bypass:
                    logger.debug(f"[ADVISOR] Removing direct bypass: {conn.from_id} → {conn.to_id} (should go through EventBridge)")
                    removed_count += 1
                    continue
                
                filtered_connections.append(conn)
            
            if removed_count > 0:
                logger.info(f"[ADVISOR] Removed {removed_count} direct bypass connections (canonical pattern enforced)")
            
            return filtered_connections
        
        return connections
    
    def _add_connection_labels(self, connections: List[Connection], components: List[Component]) -> List[Connection]:
        """
        Add descriptive labels to connections based on architectural patterns.
        
        Args:
            connections: List of connections
            components: List of components
            
        Returns:
            List of connections with labels added
        """
        component_map = {c.id: c for c in components}
        node_id_map = {c.id: c.get_node_id() for c in components}
        
        labeled_connections = []
        
        for conn in connections:
            from_node_id = node_id_map.get(conn.from_id)
            to_node_id = node_id_map.get(conn.to_id)
            
            # Skip if label already exists or if we can't identify node types
            if conn.label or not from_node_id or not to_node_id:
                labeled_connections.append(conn)
                continue
            
            # Determine label based on pattern
            label = None
            
            # Event-Driven patterns
            if from_node_id == "eventbridge" and to_node_id == "lambda":
                label = "Event Stream"
            elif from_node_id in {"s3", "api_gateway", "iot_core"} and to_node_id == "eventbridge":
                label = "Events"
            
            # Serverless patterns
            elif from_node_id == "api_gateway" and to_node_id == "lambda":
                label = "HTTP Request"
            elif from_node_id == "lambda" and to_node_id == "dynamodb":
                label = "Query/Write"
            
            # Data Pipeline patterns
            elif from_node_id in {"kinesis", "kinesis_data_streams"} and to_node_id == "lambda":
                label = "Data Stream"
            elif from_node_id == "lambda" and to_node_id == "s3":
                label = "Storage"
            elif from_node_id == "lambda" and to_node_id in {"redshift", "athena"}:
                label = "Analytics"
            
            # Microservices patterns
            elif from_node_id == "api_gateway" and to_node_id in {"lambda", "ecs", "eks"}:
                label = "API Request"
            elif from_node_id in {"lambda", "ecs", "eks"} and to_node_id in {"dynamodb", "rds"}:
                label = "Query"
            
            # Network patterns
            elif from_node_id == "internet_gateway" and to_node_id in {"subnet", "public_subnet"}:
                label = "Traffic"
            elif from_node_id == "nat_gateway" and to_node_id in {"subnet", "private_subnet"}:
                label = "Outbound Traffic"
            
            # Queue/Stream patterns
            elif from_node_id in {"sqs", "sns"} and to_node_id == "lambda":
                label = "Message"
            elif from_node_id == "lambda" and to_node_id in {"sqs", "sns"}:
                label = "Publish"
            
            # Create new Connection with label if we found one
            if label:
                new_conn = Connection(
                    from_id=conn.from_id,
                    to_id=conn.to_id,
                    label=label,
                    graphviz_attrs=conn.graphviz_attrs,
                    direction=conn.direction
                )
                logger.debug(f"[ADVISOR] Added label '{label}' to connection: {conn.from_id} → {conn.to_id}")
                labeled_connections.append(new_conn)
            else:
                labeled_connections.append(conn)
        
        return labeled_connections
    
    def _enhance_component_names(self, components: List[Component]) -> List[Component]:
        """
        Enhance component names with full AWS service names and descriptive subtitles.
        
        Args:
            components: List of components
            
        Returns:
            List of components with enhanced names
        """
        enhanced_components = []
        
        # Mapping of node_id to full AWS service name
        aws_service_names = {
            "eventbridge": "Amazon EventBridge",
            "dynamodb": "Amazon DynamoDB",
            "api_gateway": "Amazon API Gateway",
            "lambda": "AWS Lambda Function",
            "s3": "Amazon S3",
            "rds": "Amazon RDS",
            "kinesis": "Amazon Kinesis",
            "kinesis_data_streams": "Amazon Kinesis Data Streams",
            "redshift": "Amazon Redshift",
            "sqs": "Amazon SQS",
            "sns": "Amazon SNS",
            "cloudfront": "Amazon CloudFront",
            "route53": "Amazon Route53",
            "vpc": "Amazon VPC",
            "ec2": "Amazon EC2",
            "ecs": "Amazon ECS",
            "eks": "Amazon EKS",
            "alb": "Application Load Balancer",
            "elb": "Elastic Load Balancer",
            "athena": "Amazon Athena",
            "glue": "AWS Glue",
            "quicksight": "Amazon QuickSight",
        }
        
        # Detect diagram type from components to add appropriate subtitles
        has_eventbridge = any(c.get_node_id() == "eventbridge" for c in components)
        has_kinesis = any(c.get_node_id() in {"kinesis", "kinesis_data_streams"} for c in components)
        has_api_gateway = any(c.get_node_id() == "api_gateway" for c in components)
        has_redshift = any(c.get_node_id() == "redshift" for c in components)
        
        for comp in components:
            node_id = comp.get_node_id()
            full_name = aws_service_names.get(node_id, comp.name)
            
            # Add subtitles based on context
            subtitle = None
            
            # Event-Driven context
            if has_eventbridge:
                if node_id == "eventbridge":
                    subtitle = "Event Bus"
                elif node_id == "dynamodb":
                    subtitle = "Event Storage"
            
            # Data Pipeline context
            elif has_kinesis:
                if node_id in {"kinesis", "kinesis_data_streams"}:
                    subtitle = "Data Stream"
                elif node_id == "s3":
                    subtitle = "Data Lake"
                elif node_id == "redshift":
                    subtitle = "Data Warehouse"
            
            # Serverless context
            elif has_api_gateway:
                if node_id == "api_gateway":
                    subtitle = "API Management"
                elif node_id == "lambda":
                    subtitle = "Business Logic"
                elif node_id == "dynamodb":
                    subtitle = "Data Store"
            
            # Analytics context
            elif has_redshift:
                if node_id == "redshift":
                    subtitle = "Data Warehouse"
                elif node_id == "s3":
                    subtitle = "Data Lake"
            
            # Network context
            elif node_id == "vpc":
                subtitle = "Network Isolation"
            elif node_id == "nat_gateway":
                subtitle = "Outbound Internet"
            elif node_id == "internet_gateway":
                subtitle = "Internet Access"
            
            # Build final name
            if subtitle:
                enhanced_name = f"{full_name} ({subtitle})"
            else:
                enhanced_name = full_name
            
            # Only update if name changed
            if enhanced_name != comp.name:
                comp.name = enhanced_name
                logger.debug(f"[ADVISOR] Enhanced component name: {comp.id} → {enhanced_name}")
            
            enhanced_components.append(comp)
        
        return enhanced_components
    
    def _style_connections_by_type(self, connections: List[Connection], components: List[Component]) -> List[Connection]:
        """
        Style connections based on their relationship type (containment, routing, data flow).
        
        Relationship types detected from labels:
        - "contains", "hosts" → Containment (bidirectional, dashed, no arrowhead)
        - "routes to", "provides" → Routing (forward, solid)
        - "backup to", "stores in" → Data flow (forward, solid)
        - Default → Data flow (forward, solid)
        """
        styled_connections = []
        component_map = {c.id: c for c in components}
        
        for conn in connections:
            label_lower = (conn.label or "").lower()
            
            # Containment relationships
            if any(keyword in label_lower for keyword in ["contains", "hosts"]):
                if not conn.direction:
                    conn.direction = "bidirectional"
                if not conn.graphviz_attrs:
                    conn.graphviz_attrs = {}
                # Use dashed line with dimmed color for containment (no arrowhead via dir="none")
                conn.graphviz_attrs.setdefault("style", "dashed")
                conn.graphviz_attrs.setdefault("dir", "none")  # No arrow direction for containment
                conn.graphviz_attrs.setdefault("color", "gray60")
                conn.graphviz_attrs.setdefault("penwidth", "1.5")
            
            # Routing relationships
            elif any(keyword in label_lower for keyword in ["routes to", "provides", "routes"]):
                if not conn.direction:
                    conn.direction = "forward"
                if not conn.graphviz_attrs:
                    conn.graphviz_attrs = {}
                conn.graphviz_attrs.setdefault("style", "solid")
                conn.graphviz_attrs.setdefault("color", "blue")
            
            # Backup/storage relationships
            elif any(keyword in label_lower for keyword in ["backup", "stores", "saves"]):
                if not conn.direction:
                    conn.direction = "forward"
                if not conn.graphviz_attrs:
                    conn.graphviz_attrs = {}
                conn.graphviz_attrs.setdefault("style", "dotted")
                conn.graphviz_attrs.setdefault("color", "green")
            
            # Default: data flow (forward, solid)
            else:
                if not conn.direction:
                    conn.direction = "forward"
            
            styled_connections.append(conn)
        
        return styled_connections

