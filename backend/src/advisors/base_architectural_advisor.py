"""
Base Architectural Advisor - Shared functionality for all cloud providers.

This base class provides common clustering, validation, and spacing logic
that is shared across AWS, Azure, and GCP advisors.
"""
import logging
from typing import List, Dict, Tuple
from abc import ABC, abstractmethod

from ..models.spec import Component, Connection, Cluster

logger = logging.getLogger(__name__)


class BaseArchitecturalAdvisor(ABC):
    """Base class for architectural advisors with shared clustering and validation logic."""
    
    # Layer to group mapping (shared across all providers)
    LAYER_TO_GROUP_MAP = {
        0: "Frontend/Edge",
        1: "Frontend/Edge",
        2: "Network",
        3: "Network",
        4: "Application",
        5: "Compute",
        6: "Integration",
        7: "Data",
        8: "Analytics",
        9: "Security/Management"
    }
    
    @abstractmethod
    def get_layer_order(self, component_type: str) -> int:
        """Get the layer order for a component type (provider-specific)."""
        pass
    
    def _get_cluster_threshold(self, total_components: int) -> int:
        """
        Get minimum cluster size based on total component count.
        
        Adaptive thresholding:
        - Large diagrams (20+ components): Require 3+ components per cluster
        - Medium diagrams (10-19 components): Require 2+ components per cluster
        - Small diagrams (<10 components): Require 2+ components per cluster
        
        Args:
            total_components: Total number of components in the diagram
            
        Returns:
            Minimum number of components required to form a cluster
        """
        if total_components >= 20:
            return 3  # Require more components for large diagrams
        elif total_components >= 10:
            return 2
        else:
            return 2  # Keep small diagrams simple
    
    def _calculate_dynamic_spacing(
        self, 
        component_count: int, 
        connection_count: int
    ) -> Tuple[float, float]:
        """
        Calculate dynamic spacing based on diagram complexity.
        
        Spacing scales with complexity to prevent crowding in large diagrams
        while keeping small diagrams compact.
        
        Args:
            component_count: Number of components in the diagram
            connection_count: Number of connections in the diagram
            
        Returns:
            Tuple of (nodesep, ranksep) values for Graphviz
        """
        base_nodesep = 1.0
        base_ranksep = 1.5
        
        # Calculate complexity score (components + weighted connections)
        complexity = component_count + (connection_count * 0.5)
        
        # Scale spacing based on complexity
        if complexity > 30:
            nodesep_multiplier = 1.3
            ranksep_multiplier = 1.4
        elif complexity > 20:
            nodesep_multiplier = 1.2
            ranksep_multiplier = 1.3
        elif complexity > 15:
            nodesep_multiplier = 1.1
            ranksep_multiplier = 1.15
        else:
            nodesep_multiplier = 1.0
            ranksep_multiplier = 1.0
        
        nodesep = base_nodesep * nodesep_multiplier
        ranksep = base_ranksep * ranksep_multiplier
        
        return nodesep, ranksep
    
    def _validate_connections(
        self, 
        connections: List[Connection], 
        components: List[Component]
    ) -> List[str]:
        """
        Validate connections make sense given layer ordering.
        
        Checks for backwards connections (e.g., Data → Frontend) that might
        indicate architectural issues or AI agent errors.
        
        Args:
            connections: List of connections to validate
            components: List of components (for looking up layer orders)
            
        Returns:
            List of warning messages for potentially invalid connections
        """
        warnings = []
        comp_map = {c.id: c for c in components}
        
        for conn in connections:
            from_comp = comp_map.get(conn.from_id)
            to_comp = comp_map.get(conn.to_id)
            
            if not from_comp or not to_comp:
                continue  # Skip if components not found
            
            from_layer = self.get_layer_order(from_comp.get_node_id())
            to_layer = self.get_layer_order(to_comp.get_node_id())
            
            # Warn if connection goes backwards (unless bidirectional)
            if to_layer < from_layer and conn.direction != "bidirectional":
                # Allow some backwards connections (e.g., Data → Analytics is OK)
                if not (from_layer == 7 and to_layer == 8):  # Data → Analytics is valid
                    warnings.append(
                        f"Connection '{conn.from_id}' → '{conn.to_id}' goes backwards "
                        f"(layer {from_layer} → {to_layer}). "
                        f"Consider bidirectional direction or verify architecture."
                    )
        
        return warnings
    
    def _group_components_by_layer(self, components: List[Component]) -> Dict[str, List[str]]:
        """
        Group components by architectural layer using shared mapping.
        
        Uses LAYER_TO_GROUP_MAP to convert layer numbers (0-9) to
        group names (Frontend/Edge, Network, etc.).
        
        Args:
            components: List of components to group
            
        Returns:
            Dictionary mapping group names to lists of component IDs
        """
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
            group_name = self.LAYER_TO_GROUP_MAP.get(layer_order, "Compute")  # Default fallback
            layer_groups[group_name].append(comp.id)
        
        return layer_groups

