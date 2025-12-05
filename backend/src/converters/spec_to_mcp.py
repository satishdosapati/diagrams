"""
Convert ArchitectureSpec to MCP Diagram Server input format.

This module provides conversion utilities to transform ArchitectureSpec objects
into formats that can be used with the AWS Diagram MCP Server.
"""
import logging
from typing import Dict, Any

from ..models.spec import ArchitectureSpec
from ..generators.diagrams_engine import DiagramsEngine
from ..resolvers.component_resolver import ComponentResolver

logger = logging.getLogger(__name__)


class SpecToMCPConverter:
    """Converts ArchitectureSpec to MCP server input format."""
    
    def __init__(self):
        """Initialize the converter."""
        self.engine = DiagramsEngine()
    
    def convert_to_code(self, spec: ArchitectureSpec) -> str:
        """
        Convert ArchitectureSpec to Python code string for MCP server.
        
        Args:
            spec: ArchitectureSpec object
            
        Returns:
            Python code string using diagrams library DSL
        """
        try:
            resolver = ComponentResolver(primary_provider=spec.provider)
            code = self.engine._generate_code(spec, resolver)
            logger.debug(f"Converted ArchitectureSpec '{spec.title}' to Python code ({len(code)} chars)")
            return code
        except Exception as e:
            logger.error(f"Error converting spec to code: {e}", exc_info=True)
            raise
    
    def convert_to_mcp_input(
        self,
        spec: ArchitectureSpec,
        include_code: bool = True
    ) -> Dict[str, Any]:
        """
        Convert ArchitectureSpec to MCP server tool input format.
        
        Args:
            spec: ArchitectureSpec object
            include_code: Whether to include generated Python code
            
        Returns:
            Dict formatted for MCP server generate_diagram tool
        """
        # Map diagram type
        diagram_type = self._map_diagram_type(spec)
        
        # Generate code if requested
        code = None
        if include_code:
            code = self.convert_to_code(spec)
        
        # Build MCP input
        mcp_input = {
            "title": spec.title,
            "diagram_type": diagram_type
        }
        
        if code:
            mcp_input["code"] = code
        
        # Add metadata
        if spec.outformat:
            mcp_input["outformat"] = spec.outformat
        
        if spec.direction:
            mcp_input["direction"] = spec.direction
        
        if spec.graphviz_attrs:
            mcp_input["graphviz_attrs"] = {
                "graph_attr": spec.graphviz_attrs.graph_attr or {},
                "node_attr": spec.graphviz_attrs.node_attr or {},
                "edge_attr": spec.graphviz_attrs.edge_attr or {}
            }
        
        return mcp_input
    
    def _map_diagram_type(self, spec: ArchitectureSpec) -> str:
        """
        Map ArchitectureSpec diagram type to MCP server diagram type.
        
        Args:
            spec: ArchitectureSpec object
            
        Returns:
            MCP diagram type string
        """
        diagram_type = spec.metadata.get("diagram_type", "cloud_architecture")
        
        # Mapping from internal types to MCP server types
        type_mapping = {
            "cloud_architecture": "aws_architecture",
            "system_architecture": "aws_architecture",
            "network_topology": "flow_diagram",
            "data_pipeline": "flow_diagram",
            "c4_model": "class_diagram",
            "sequence": "sequence_diagram",
            "flow": "flow_diagram",
            "class": "class_diagram"
        }
        
        return type_mapping.get(diagram_type, "aws_architecture")


# Global converter instance
_converter: SpecToMCPConverter = None


def get_converter() -> SpecToMCPConverter:
    """Get or create global converter instance."""
    global _converter
    if _converter is None:
        _converter = SpecToMCPConverter()
    return _converter
