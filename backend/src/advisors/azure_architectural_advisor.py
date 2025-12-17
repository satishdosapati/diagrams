"""
Azure Architectural Advisor - Provides Azure architectural guidance based on Azure Well-Architected Framework.
"""
import os
import logging
from typing import Optional, List, Dict, Tuple
from ..models.spec import ArchitectureSpec, Component, Connection, Cluster, GraphvizAttributes
from .base_architectural_advisor import BaseArchitecturalAdvisor

logger = logging.getLogger(__name__)


class AzureArchitecturalAdvisor(BaseArchitecturalAdvisor):
    """Provides Azure architectural guidance using Azure Well-Architected Framework."""
    
    # Component layer ordering (lower number = appears first/left in diagram)
    LAYER_ORDER = {
        # Internet/Edge Layer
        "dns": 0,
        "cdn": 1,
        "traffic_manager": 1,
        "firewall": 1,
        
        # Network Layer
        "virtual_network": 2,
        "vpn_gateway": 2,
        "expressroute": 2,
        "load_balancer": 3,
        "application_gateway": 3,
        
        # Application/API Layer
        "api_management": 4,
        "app_service": 4,
        
        # Compute Layer
        "azure_function": 5,
        "azure_vm": 5,
        "container_instances": 5,
        "kubernetes_services": 5,
        "batch": 5,
        "service_fabric": 5,
        
        # Integration Layer
        "service_bus": 6,
        "event_grid": 6,
        "event_hubs": 6,
        "logic_apps": 6,
        
        # Data Layer
        "blob_storage": 7,
        "file_storage": 7,
        "data_lake": 7,
        "cosmos_db": 7,
        "sql_database": 7,
        "database_for_mysql": 7,
        "database_for_postgresql": 7,
        "redis_cache": 7,
        
        # Analytics Layer
        "data_factory": 8,
        "stream_analytics": 8,
        "synapse_analytics": 8,
        "databricks": 8,
        "hdinsight": 8,
        
        # Security/Management Layer
        "key_vaults": 9,
        "active_directory": 9,
        "monitor": 9,
        "security_center": 9,
    }
    
    # Component dependencies (what should exist if this component exists)
    DEPENDENCIES = {
        "azure_vm": ["virtual_network"],
        "sql_database": ["virtual_network"],
        "database_for_mysql": ["virtual_network"],
        "database_for_postgresql": ["virtual_network"],
        "kubernetes_services": ["virtual_network"],
        "container_instances": ["virtual_network"],
        "azure_function": [],  # Can exist without VNet (consumption plan)
        "app_service": [],  # Can exist without VNet (default hosting)
        "api_management": [],
        "blob_storage": [],
        "cosmos_db": [],
    }
    
    # Common architectural patterns
    PATTERNS = {
        "serverless": {
            "components": ["api_management", "azure_function", "cosmos_db"],
            "connections": [
                ("api_management", "azure_function"),
                ("azure_function", "cosmos_db")
            ],
            "order": ["api_management", "azure_function", "cosmos_db"]
        },
        "three_tier": {
            "components": ["application_gateway", "azure_vm", "sql_database"],
            "connections": [
                ("application_gateway", "azure_vm"),
                ("azure_vm", "sql_database")
            ],
            "order": ["application_gateway", "azure_vm", "sql_database"]
        },
        "microservices": {
            "components": ["application_gateway", "kubernetes_services", "cosmos_db"],
            "connections": [
                ("application_gateway", "kubernetes_services"),
                ("kubernetes_services", "cosmos_db")
            ],
            "order": ["application_gateway", "kubernetes_services", "cosmos_db"]
        },
        "data_pipeline": {
            "components": ["blob_storage", "data_factory", "synapse_analytics"],
            "connections": [
                ("blob_storage", "data_factory"),
                ("data_factory", "synapse_analytics")
            ],
            "order": ["blob_storage", "data_factory", "synapse_analytics"]
        },
        "vnet_network": {
            "components": ["virtual_network", "load_balancer", "application_gateway"],
            "connections": [
                ("virtual_network", "load_balancer"),
                ("virtual_network", "application_gateway")
            ],
            "order": ["virtual_network", "load_balancer", "application_gateway"]
        }
    }
    
    def __init__(self):
        """Initialize the advisor."""
        logger.info(f"[ADVISOR] Azure Architectural Advisor initialized")
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
        """Validate and suggest missing connections based on Azure patterns."""
        component_map = {c.id: c for c in components}
        existing_conns = {(c.from_id, c.to_id) for c in connections}
        suggested_conns = []
        warnings = []
        
        # Check for Virtual Network patterns
        vnet_components = [c for c in components if c.get_node_id() == "virtual_network"]
        vm_components = [c for c in components if c.get_node_id() == "azure_vm"]
        sql_components = [c for c in components if c.get_node_id() in ["sql_database", "database_for_mysql", "database_for_postgresql"]]
        
        # Virtual Network should contain VMs (containment relationship)
        for vnet in vnet_components:
            for vm in vm_components:
                conn_key = (vnet.id, vm.id)
                if conn_key not in existing_conns:
                    has_connection = any(c.from_id == vm.id or c.to_id == vm.id for c in connections)
                    if not has_connection:
                        suggested_conns.append(Connection(
                            from_id=vnet.id,
                            to_id=vm.id,
                            label="contains",
                            direction="bidirectional",
                            graphviz_attrs={"style": "dashed", "arrowhead": "none"}
                        ))
        
        # Check for common patterns
        api_management = next((c for c in components if c.get_node_id() == "api_management"), None)
        function_apps = [c for c in components if c.get_node_id() == "azure_function"]
        cosmos_db = next((c for c in components if c.get_node_id() == "cosmos_db"), None)
        
        # Serverless pattern: API Management → Azure Function → Cosmos DB
        if api_management and function_apps:
            for func in function_apps:
                conn_key = (api_management.id, func.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=api_management.id,
                        to_id=func.id
                    ))
        
        if function_apps and cosmos_db:
            for func in function_apps:
                conn_key = (func.id, cosmos_db.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=func.id,
                        to_id=cosmos_db.id
                    ))
        
        # Check for Application Gateway → VM pattern
        app_gateway = next((c for c in components if c.get_node_id() == "application_gateway"), None)
        if app_gateway and vm_components:
            for vm in vm_components:
                conn_key = (app_gateway.id, vm.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=app_gateway.id,
                        to_id=vm.id
                    ))
        
        # Check for Load Balancer → VM pattern
        load_balancer = next((c for c in components if c.get_node_id() == "load_balancer"), None)
        if load_balancer and vm_components:
            for vm in vm_components:
                conn_key = (load_balancer.id, vm.id)
                if conn_key not in existing_conns:
                    suggested_conns.append(Connection(
                        from_id=load_balancer.id,
                        to_id=vm.id
                    ))
        
        # VM → SQL Database pattern
        if vm_components and sql_components:
            for vm in vm_components:
                for sql in sql_components:
                    conn_key = (vm.id, sql.id)
                    if conn_key not in existing_conns:
                        suggested_conns.append(Connection(
                            from_id=vm.id,
                            to_id=sql.id
                        ))
        
        # Add warnings for best practices
        if vnet_components and vm_components:
            warnings.append("Consider deploying VMs across multiple Availability Zones for high availability (Azure best practice)")
        
        return suggested_conns, warnings
    
    def get_architectural_guidance(self, description: str) -> str:
        """Get architectural guidance based on Azure Well-Architected Framework."""
        enhanced_guidance = self._get_enhanced_guidance_with_context(description)
        return enhanced_guidance
    
    def _get_enhanced_guidance_with_context(self, description: str) -> str:
        """Get enhanced guidance based on description context."""
        description_lower = description.lower()
        
        components_mentioned = []
        if "virtual network" in description_lower or "vnet" in description_lower:
            components_mentioned.append("Virtual Network")
        if "vm" in description_lower or "virtual machine" in description_lower:
            components_mentioned.append("VM")
        if "function" in description_lower or "azure function" in description_lower:
            components_mentioned.append("Azure Function")
        if "sql" in description_lower or "database" in description_lower:
            components_mentioned.append("SQL Database")
        if "api" in description_lower or "management" in description_lower:
            components_mentioned.append("API Management")
        
        base_guidance = self._get_static_guidance()
        
        if components_mentioned:
            context_note = f"\n\nBased on your description mentioning {', '.join(components_mentioned)}:\n"
            context_note += "- Ensure proper component ordering and connections\n"
            context_note += "- Follow Azure best practices for these components\n"
            return base_guidance + context_note
        
        return base_guidance
    
    def _get_static_guidance(self) -> str:
        """Get static architectural guidance based on Azure Well-Architected Framework."""
        return """
Azure Architectural Best Practices (Based on Azure Well-Architected Framework):

1. Component Ordering (Left to Right):
   - Internet/Edge: DNS, CDN, Traffic Manager, Firewall
   - Network: Virtual Network, VPN Gateway, ExpressRoute, Load Balancer, Application Gateway
   - Application: API Management, App Service
   - Compute: Azure Functions, VMs, Container Instances, AKS, Batch
   - Integration: Service Bus, Event Grid, Event Hubs, Logic Apps
   - Data: Blob Storage, File Storage, Cosmos DB, SQL Database
   - Analytics: Data Factory, Stream Analytics, Synapse Analytics, Databricks
   - Security/Management: Key Vault, Active Directory, Monitor, Security Center

2. Virtual Network Best Practices:
   - Deploy resources across multiple Availability Zones for high availability
   - Use Network Security Groups (NSGs) to control traffic to VMs
   - Use Application Security Groups for logical grouping of VMs
   - Enable Network Watcher for network monitoring
   - Plan IP address space allocation accounting for expansion
   - Use hub-and-spoke topology for better network management
   - Ensure non-overlapping IP address ranges across VNets

3. Connection Patterns:
   - Virtual Network contains VMs (containment relationship)
   - Application Gateway connects to VMs (data flow)
   - Load Balancer connects to VMs (data flow)
   - API Management connects to Azure Functions (data flow)
   - Azure Functions connect to Cosmos DB (data flow)
   - VMs connect to SQL Database (data flow)

4. Common Patterns:
   - Serverless: API Management → Azure Function → Cosmos DB
   - Three-Tier: Application Gateway → VM → SQL Database
   - Microservices: Application Gateway → AKS → Cosmos DB
   - Data Pipeline: Blob Storage → Data Factory → Synapse Analytics
   - VNet Network: Virtual Network → Load Balancer → Application Gateway

5. Dependencies:
   - VMs require Virtual Network (deploy in multiple AZs)
   - SQL Database requires Virtual Network (use geo-replication for HA)
   - AKS requires Virtual Network
   - Azure Functions can use consumption plan (no VNet) or premium plan (with VNet)
   - App Service can use default hosting (no VNet) or VNet integration

6. Security Best Practices:
   - Use NSGs for VM-level traffic control
   - Use Azure Firewall for advanced filtering
   - Enable Azure Security Center for threat detection
   - Use Key Vault for secrets management
   - Implement Azure AD for identity management
   - Use Private Endpoints for secure connectivity to PaaS services
"""
    
    def _get_component_display_name(self, node_id: str) -> str:
        """Get display name for a component type."""
        names = {
            "virtual_network": "Virtual Network",
            "azure_vm": "VM",
            "azure_function": "Azure Function",
            "sql_database": "SQL Database",
            "application_gateway": "Application Gateway",
            "load_balancer": "Load Balancer",
        }
        return names.get(node_id, node_id.replace("_", " ").title())
    
    def enhance_spec(self, spec: ArchitectureSpec) -> ArchitectureSpec:
        """Enhance spec with ordering and suggested connections."""
        logger.info(f"[ADVISOR] === Starting Azure spec enhancement ===")
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
        
        # Validate connections for architectural correctness
        validation_warnings = self._validate_connections(new_connections, sorted_components)
        if validation_warnings:
            logger.warning(f"[ADVISOR] Connection validation warnings: {len(validation_warnings)}")
            for warning in validation_warnings[:5]:  # Log first 5 warnings
                logger.warning(f"[ADVISOR] {warning}")
        
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
        
        # Calculate dynamic spacing based on diagram complexity
        # Spacing scales with complexity to prevent crowding in large diagrams
        nodesep, ranksep = self._calculate_dynamic_spacing(
            len(final_components), 
            len(final_connections)
        )
        if "nodesep" not in graphviz_attrs.graph_attr:
            graphviz_attrs.graph_attr["nodesep"] = str(nodesep)
        if "ranksep" not in graphviz_attrs.graph_attr:
            graphviz_attrs.graph_attr["ranksep"] = str(ranksep)
        
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
        # labeldistance: Distance from edge (lower = closer, default 1.0)
        if "labeldistance" not in graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr["labeldistance"] = "0.6"  # Closer to edge
        # labelfontsize: Font size for edge labels
        if "labelfontsize" not in graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr["labelfontsize"] = "10"
        # labelloc: Label position relative to edge (t=top, c=center, b=bottom)
        if "labelloc" not in graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr["labelloc"] = "c"  # Center label on edge
        # labelangle: Angle of label text relative to edge (0=horizontal, positive=clockwise)
        # For orthogonal edges, horizontal labels (0) work best
        if "labelangle" not in graphviz_attrs.edge_attr:
            graphviz_attrs.edge_attr["labelangle"] = "0"  # Keep labels horizontal
        
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
        
        logger.info(f"[ADVISOR] === Azure enhancement complete ===")
        logger.info(f"[ADVISOR] Final: {len(sorted_components)} components, {len(new_connections)} connections, {len(enhanced_spec.clusters)} clusters")
        return enhanced_spec
    
    def _auto_create_clusters(self, components: List[Component]) -> List[Cluster]:
        """Automatically create clusters based on component types and architectural layers."""
        clusters = []
        component_ids = {c.id for c in components}
        
        # Group components by layer using shared base class method
        layer_groups = self._group_components_by_layer(components)
        
        # Use adaptive cluster threshold based on total component count
        min_cluster_size = self._get_cluster_threshold(len(components))
        
        # Create clusters for layers with sufficient components
        cluster_id_counter = 1
        for layer_name, comp_ids in layer_groups.items():
            if len(comp_ids) >= min_cluster_size:
                cluster_id = f"cluster_{cluster_id_counter}"
                clusters.append(Cluster(
                    id=cluster_id,
                    name=layer_name,
                    component_ids=comp_ids,
                    parent_id=None
                ))
                cluster_id_counter += 1
        
        # Special handling: Virtual Network hierarchy
        vnet_components = [c for c in components if c.get_node_id() == "virtual_network"]
        vnet_related = [c for c in components if c.get_node_id() in ["load_balancer", "application_gateway"]]
        
        if vnet_components and vnet_related:
            vnet_in_cluster = False
            for cluster in clusters:
                if vnet_components[0].id in cluster.component_ids:
                    vnet_in_cluster = True
                    for comp in vnet_related:
                        if comp.id not in cluster.component_ids:
                            cluster.component_ids.append(comp.id)
                    break
            
            if not vnet_in_cluster:
                vnet_cluster_ids = [c.id for c in vnet_components + vnet_related]
                if len(vnet_cluster_ids) >= 2:
                    clusters.append(Cluster(
                        id=f"cluster_{cluster_id_counter}",
                        name="Virtual Network",
                        component_ids=vnet_cluster_ids,
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
