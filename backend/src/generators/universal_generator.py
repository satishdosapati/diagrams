"""
UniversalGenerator - Routes to appropriate rendering engine based on diagram type.
"""
from typing import Protocol
from abc import ABC, abstractmethod

from ..models.spec import ArchitectureSpec


class DiagramEngine(Protocol):
    """Protocol that all rendering engines must implement."""
    def render(self, spec: ArchitectureSpec) -> str:
        """Render spec to diagram file. Returns file path."""
        ...


class UniversalGenerator:
    """
    Universal Generator - single entry point for all diagram types.
    Routes to appropriate engine based on diagram type.
    """
    
    def __init__(self):
        """Initialize with available engines."""
        from .diagrams_engine import DiagramsEngine
        
        # Map diagram types to their engines
        self.engines: dict[str, DiagramEngine] = {
            "cloud_architecture": DiagramsEngine(),
            "system_architecture": DiagramsEngine(),  # Same engine, different config
            "network_topology": DiagramsEngine(),
            "data_pipeline": DiagramsEngine(),
            "c4_model": DiagramsEngine(),  # Will use diagrams.c4 nodes
        }
    
    def generate(self, spec: ArchitectureSpec) -> str:
        """
        Generate diagram from spec.
        
        Args:
            spec: Architecture specification
            
        Returns:
            Path to generated diagram file
        """
        # Determine diagram type from spec metadata or infer
        diagram_type = spec.metadata.get("diagram_type", "cloud_architecture")
        
        # Route to appropriate engine
        engine = self.engines.get(diagram_type)
        if not engine:
            # Default to cloud architecture
            engine = self.engines["cloud_architecture"]
        
        # Render
        output_path = engine.render(spec)
        
        return output_path

