"""
GCP Architectural Advisor - Provides GCP architectural guidance based on Google Cloud Architecture Framework.
"""
import os
import logging
from typing import Optional, List, Dict, Tuple
from ..models.spec import ArchitectureSpec, Component, Connection, Cluster, GraphvizAttributes

logger = logging.getLogger(__name__)


class GCPArchitecturalAdvisor:
    """Provides GCP architectural guidance using Google Cloud Architecture Framework."""
    
    # Component layer ordering (lower number = appears first/left in diagram)
    LAYER_ORDER = {
        # Internet/Edge Layer
        "cloud_dns": 0,
        "cloud_cdn": 1,
        "cloud_armor": 1,
        "cloud_armor_security": 1,
        
        # Network Layer
        "vpc": 2,
        "cloud_vpn": 2,
        "cloud_interconnect": 2,
        "load_balancing": 3,
        "cloud_nat": 3,
        
        # Application/API Layer
        "api_gateway": 4,
        "cloud_endpoints": 4,
        
        # Compute Layer
        "cloud_function": 5,
        "compute_engine": 5,
        "app_engine": 5,
        "cloud_run": 5,
        "gke": 5,
        "batch": 5,
        
        # Integration Layer
        "pubsub": 6,
        "cloud_scheduler": 6,
        "cloud_tasks": 6,
        "workflow": 6,
        
        # Data Layer
        "cloud_storage": 7,
        "filestore": 7,
        "persistent_disk": 7,
        "firestore": 7,
        "bigtable": 7,
        "spanner": 7,
        "memorystore": 7,
        "datastore": 7,
        "cloud_sql": 7,
        
        # Analytics Layer
        "bigquery": 8,
        "dataflow": 8,
        "dataproc": 8,
        "data_fusion": 8,
        "data_catalog": 8,
        
        # Security/Management Layer
        "iam": 9,
        "cloud_kms": 9,
        "secret_manager": 9,
        "cloud_monitoring": 9,
        "cloud_logging": 9,
        "security_command_center": 9,
    }
    
    # Component dependencies (what should exist if this component exists)
    DEPENDENCIES = {
        "compute_engine": ["vpc"],
        "cloud_sql": ["vpc"],
        "gke": ["vpc"],
        "cloud_run": [],  # Can exist without VPC (fully managed)
        "cloud_function": [],  # Can exist without VPC (1st gen) or with VPC (2nd gen)
        "app_engine": [],  # Fully managed, no VPC required
        "api_gateway": [],
        "cloud_storage": [],
        "firestore": [],
        "bigtable": [],
    }
    
    # Common architectural patterns
    PATTERNS = {
        "serverless": {
            "components": ["api_gateway", "cloud_function", "firestore"],
            "connections": [
                ("api_gateway", "cloud_function"),
                ("cloud_function", "firestore")
            ],
            "order": ["api_gateway", "cloud_function", "firestore"]
        },
        "three_tier": {
            "components": ["load_balancing", "compute_engine", "cloud_sql"],
            "connections": [
                ("load_balancing", "compute_engine"),
                ("compute_engine", "cloud_sql")
            ],
            "order": ["load_balancing", "compute_engine", "cloud_sql"]
        },
        "microservices": {
            "components": ["load_balancing", "gke", "cloud_sql"],
            "connections": [
                ("load_balancing", "gke"),
                ("gke", "cloud_sql")
            ],
            "order": ["load_balancing", "gke", "cloud_sql"]
        },
        "data_pipeline": {
            "components": ["cloud_storage", "dataflow", "bigquery"],
            "connections": [
                ("cloud_storage", "dataflow"),
                ("dataflow", "bigquery")
            ],
            "order": ["cloud_storage", "dataflow", "bigquery"]
        },
        "vpc_network": {
            "components": ["vpc", "load_balancing", "cloud_nat"],
            "connections": [
                ("vpc", "load_balancing"),
                ("vpc", "cloud_nat")
            ],
            "order": ["vpc", "load_balancing", "cloud_nat"]
        }
    }
    
    def __init__(self):
        """Initialize the advisor."""
        logger.info(f"[ADVISOR] GCP Architectural Advisor initialized")
        logger.info(f"[ADVISOR] Static mode: Using static architectural guidance")
    
    def get_layer_order(self, component_type: str) -> int:
        """Get the layer order for a component type."""
        node_id = component_type.lower()
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
        """Validate and suggest missing connections based on GCP patterns."""
        component_map = {c.id: c for c in components}
        existing_conns = {(c.from_id, c.to_id) for c in connections}
        suggested_conns = []
        warnings = []
        
        # Check for VPC patterns
        vpc_components = [c for c in components if c.get_node_id() == "vpc"]
        compute_engine_components = [c for c in components if c.get_node_id() == "compute_engine"]
        cloud_sql_components = [c for c in components if c.get_node_id() == "cloud_sql"]
        gke_components = [c for c in components if c.get_node_id() == "gke"]
        
        # VPC should contain Compute Engine instances (containment relationship)
        for vpc in vpc_components:
            for vm in compute_engine_components:
                conn_key = (vpc.id, vm.id)
                if conn_key not in existing_conns:
                    has_connection = any(c.from_id == vm.id or c.to_id == vm.id for c in connections)
                    if not has_connection:
                        suggested_conns.append(Connection(
                            from_id=vpc.id,
                            to_id=vm.id,
                            label="contains",
                            direction="bidirectional",
                            graphviz_attrs={"style": "dashed", "arrowhead": "none"}
                        ))
        
        # Check for common patterns
        api_gateway = next((c for c in components if c.get_node_id() == "api_gateway"), None)
        cloud_functions = [c for c in components if c.get_node_id() == "cloud_function"]
        firestore = next((c for c in components if c.get_node_id() == "firestore"), None)
        
        # Serverless pattern: API Gateway → Cloud Function → Firestore
        if api_gateway and cloud_functions:
            for func in cloud_functions:
                conn_key = (api_gateway.id, func.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=api_gateway.id,
                        to_id=func.id
                    ))
        
        if cloud_functions and firestore:
            for func in cloud_functions:
                conn_key = (func.id, firestore.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=func.id,
                        to_id=firestore.id
                    ))
        
        # Check for Load Balancing → Compute Engine pattern
        load_balancing = next((c for c in components if c.get_node_id() == "load_balancing"), None)
        if load_balancing and compute_engine_components:
            for vm in compute_engine_components:
                conn_key = (load_balancing.id, vm.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=load_balancing.id,
                        to_id=vm.id
                    ))
        
        # Check for Load Balancing → GKE pattern
        if load_balancing and gke_components:
            for gke in gke_components:
                conn_key = (load_balancing.id, gke.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=load_balancing.id,
                        to_id=gke.id
                    ))
        
        # Compute Engine → Cloud SQL pattern
        if compute_engine_components and cloud_sql_components:
            for vm in compute_engine_components:
                for sql in cloud_sql_components:
                    conn_key = (vm.id, sql.id)
                    if conn_key not in existing_conns:
                        suggested_conns.append(Connection(
                            from_id=vm.id,
                            to_id=sql.id
                        ))
        
        # GKE → Cloud SQL pattern
        if gke_components and cloud_sql_components:
            for gke in gke_components:
                for sql in cloud_sql_components:
                    conn_key = (gke.id, sql.id)
                    if conn_key not in existing_conns:
                        suggested_conns.append(Connection(
                            from_id=gke.id,
                            to_id=sql.id
                        ))
        
        # Check for Cloud NAT routing relationships
        cloud_nat = next((c for c in components if c.get_node_id() == "cloud_nat"), None)
        if cloud_nat and vpc_components:
            for vpc in vpc_components:
                conn_key = (cloud_nat.id, vpc.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=cloud_nat.id,
                        to_id=vpc.id,
                        label="provides internet to",
                        direction="forward",
                        graphviz_attrs={"style": "solid", "color": "blue"}
                    ))
        
        # Add warnings for best practices
        if vpc_components and compute_engine_components:
            warnings.append("Consider deploying Compute Engine instances across multiple zones for high availability (GCP best practice)")
        
        return suggested_conns, warnings
    
    def get_architectural_guidance(self, description: str) -> str:
        """Get architectural guidance based on Google Cloud Architecture Framework."""
        enhanced_guidance = self._get_enhanced_guidance_with_context(description)
        return enhanced_guidance
    
    def _get_enhanced_guidance_with_context(self, description: str) -> str:
        """Get enhanced guidance based on description context."""
        description_lower = description.lower()
        
        components_mentioned = []
        if "vpc" in description_lower or "network" in description_lower:
            components_mentioned.append("VPC")
        if "compute engine" in description_lower or "vm" in description_lower:
            components_mentioned.append("Compute Engine")
        if "cloud function" in description_lower or "function" in description_lower:
            components_mentioned.append("Cloud Function")
        if "cloud sql" in description_lower or "sql" in description_lower:
            components_mentioned.append("Cloud SQL")
        if "api gateway" in description_lower or "api" in description_lower:
            components_mentioned.append("API Gateway")
        
        base_guidance = self._get_static_guidance()
        
        if components_mentioned:
            context_note = f"\n\nBased on your description mentioning {', '.join(components_mentioned)}:\n"
            context_note += "- Ensure proper component ordering and connections\n"
            context_note += "- Follow GCP best practices for these components\n"
            return base_guidance + context_note
        
        return base_guidance
    
    def _get_static_guidance(self) -> str:
        """Get static architectural guidance based on Google Cloud Architecture Framework."""
        return """
GCP Architectural Best Practices (Based on Google Cloud Architecture Framework):

1. Component Ordering (Left to Right):
   - Internet/Edge: Cloud DNS, Cloud CDN, Cloud Armor
   - Network: VPC, Cloud VPN, Cloud Interconnect, Load Balancing, Cloud NAT
   - Application: API Gateway, Cloud Endpoints
   - Compute: Cloud Functions, Compute Engine, App Engine, Cloud Run, GKE
   - Integration: Pub/Sub, Cloud Scheduler, Cloud Tasks, Workflows
   - Data: Cloud Storage, Filestore, Firestore, Bigtable, Spanner, Cloud SQL
   - Analytics: BigQuery, Dataflow, Dataproc, Data Fusion
   - Security/Management: IAM, Cloud KMS, Secret Manager, Cloud Monitoring

2. VPC Network Best Practices:
   - Deploy resources across multiple zones for high availability
   - Use firewall rules to control traffic to Compute Engine instances
   - Use VPC firewall rules for network-level traffic control
   - Enable VPC Flow Logs for network monitoring
   - Plan IP address space allocation accounting for expansion
   - Use Shared VPC for better network management across projects
   - Ensure non-overlapping IP address ranges across VPCs

3. Connection Patterns:
   - VPC contains Compute Engine instances (containment relationship)
   - Load Balancing connects to Compute Engine/GKE (data flow)
   - API Gateway connects to Cloud Functions (data flow)
   - Cloud Functions connect to Firestore (data flow)
   - Compute Engine/GKE connect to Cloud SQL (data flow)
   - Cloud NAT provides internet to VPC (routing relationship)

4. Common Patterns:
   - Serverless: API Gateway → Cloud Function → Firestore
   - Three-Tier: Load Balancing → Compute Engine → Cloud SQL
   - Microservices: Load Balancing → GKE → Cloud SQL
   - Data Pipeline: Cloud Storage → Dataflow → BigQuery
   - VPC Network: VPC → Load Balancing → Cloud NAT

5. Dependencies:
   - Compute Engine requires VPC (deploy in multiple zones)
   - Cloud SQL requires VPC (use regional instances for HA)
   - GKE requires VPC
   - Cloud Functions can use 1st gen (no VPC) or 2nd gen (with VPC)
   - Cloud Run is fully managed (no VPC required)
   - App Engine is fully managed (no VPC required)

6. Security Best Practices:
   - Use firewall rules for instance-level traffic control
   - Use Cloud Armor for DDoS protection and WAF
   - Enable Cloud Security Command Center for threat detection
   - Use Secret Manager for secrets management
   - Implement IAM for access management
   - Use Private Google Access for VPC resources
   - Use Private Service Connect for secure connectivity to Google services
"""
    
    def _get_component_display_name(self, node_id: str) -> str:
        """Get display name for a component type."""
        names = {
            "vpc": "VPC",
            "compute_engine": "Compute Engine",
            "cloud_function": "Cloud Function",
            "cloud_sql": "Cloud SQL",
            "load_balancing": "Load Balancing",
            "cloud_nat": "Cloud NAT",
        }
        return names.get(node_id, node_id.replace("_", " ").title())
    
    def enhance_spec(self, spec: ArchitectureSpec) -> ArchitectureSpec:
        """Enhance spec with ordering and suggested connections."""
        logger.info(f"[ADVISOR] === Starting GCP spec enhancement ===")
        logger.info(f"[ADVISOR] Components: {len(spec.components)}, Connections: {len(spec.connections)}")
        
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
        
        # Post-process connections to style them based on relationship type
        new_connections = self._style_connections_by_type(new_connections, sorted_components)
        
        # Auto-create clusters if none exist and we have enough components
        auto_clusters = []
        if not spec.clusters and len(sorted_components) >= 3:
            logger.info(f"[ADVISOR] Auto-creating clusters for better organization...")
            auto_clusters = self._auto_create_clusters(sorted_components)
            if auto_clusters:
                logger.info(f"[ADVISOR] Created {len(auto_clusters)} clusters")
        
        final_components = sorted_components
        final_connections = new_connections
        final_clusters = auto_clusters if auto_clusters else spec.clusters
        
        # Prepare graphviz attributes for better edge routing
        graphviz_attrs = spec.graphviz_attrs
        if not graphviz_attrs:
            graphviz_attrs = GraphvizAttributes()
        
        # Always apply strict orthogonal routing for clean, structured lines
        logger.info(f"[ADVISOR] Applying strict orthogonal routing for clean structured lines ({len(final_connections)} connections)...")
        
        # CRITICAL: Always use "ortho" for strict 90-degree angle connectors
        if "splines" not in graphviz_attrs.graph_attr:
            graphviz_attrs.graph_attr["splines"] = "ortho"
        
        # CRITICAL: Prevent node overlaps
        if "overlap" not in graphviz_attrs.graph_attr:
            graphviz_attrs.graph_attr["overlap"] = "false"
        
        # Always enforce left-to-right direction for all architecture diagrams
        # This ensures a clear, consistent flow from left to right
        spec.direction = "LR"
        graphviz_attrs.graph_attr["rankdir"] = "LR"
        
        # Improve spacing for better edge routing
        if "nodesep" not in graphviz_attrs.graph_attr:
            graphviz_attrs.graph_attr["nodesep"] = "1.0"
        if "ranksep" not in graphviz_attrs.graph_attr:
            graphviz_attrs.graph_attr["ranksep"] = "1.5"
        
        # For complex diagrams with many connections, merge parallel edges
        if len(final_connections) > 10:
            if "concentrate" not in graphviz_attrs.graph_attr:
                graphviz_attrs.graph_attr["concentrate"] = "true"
        
        # Set default edge attributes
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
        
        logger.info(f"[ADVISOR] Edge routing: splines={graphviz_attrs.graph_attr.get('splines')}, overlap={graphviz_attrs.graph_attr.get('overlap')}, rankdir={graphviz_attrs.graph_attr.get('rankdir')}")
        
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
                "mcp_enabled": False
            }
        )
        
        logger.info(f"[ADVISOR] === GCP enhancement complete ===")
        logger.info(f"[ADVISOR] Final: {len(sorted_components)} components, {len(new_connections)} connections, {len(enhanced_spec.clusters)} clusters")
        return enhanced_spec
    
    def _auto_create_clusters(self, components: List[Component]) -> List[Cluster]:
        """Automatically create clusters based on component types and architectural layers."""
        clusters = []
        component_ids = {c.id for c in components}
        
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
        for layer_name, comp_ids in layer_groups.items():
            if len(comp_ids) >= 2:
                cluster_id = f"cluster_{cluster_id_counter}"
                clusters.append(Cluster(
                    id=cluster_id,
                    name=layer_name,
                    component_ids=comp_ids,
                    parent_id=None
                ))
                cluster_id_counter += 1
        
        # Special handling: VPC hierarchy
        vpc_components = [c for c in components if c.get_node_id() == "vpc"]
        vpc_related = [c for c in components if c.get_node_id() in ["load_balancing", "cloud_nat"]]
        
        if vpc_components and vpc_related:
            vpc_in_cluster = False
            for cluster in clusters:
                if vpc_components[0].id in cluster.component_ids:
                    vpc_in_cluster = True
                    for comp in vpc_related:
                        if comp.id not in cluster.component_ids:
                            cluster.component_ids.append(comp.id)
                    break
            
            if not vpc_in_cluster:
                vpc_cluster_ids = [c.id for c in vpc_components + vpc_related]
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
            type_groups = {}
            for comp in components:
                node_id = comp.get_node_id()
                if node_id not in type_groups:
                    type_groups[node_id] = []
                type_groups[node_id].append(comp.id)
            
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
    
    def _style_connections_by_type(self, connections: List[Connection], components: List[Component]) -> List[Connection]:
        """Style connections based on their relationship type."""
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
                conn.graphviz_attrs.setdefault("style", "dashed")
                conn.graphviz_attrs.setdefault("dir", "none")
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
