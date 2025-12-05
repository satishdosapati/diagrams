"""
UniversalGenerator - Routes to appropriate rendering engine based on diagram type.
"""
import logging
from typing import Protocol
from abc import ABC, abstractmethod

from ..models.spec import ArchitectureSpec

logger = logging.getLogger(__name__)


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
        logger.info(f"[UNIVERSAL_GENERATOR] Generating diagram: type={diagram_type}, provider={spec.provider}")
        logger.info(f"[UNIVERSAL_GENERATOR] Components: {len(spec.components)}, Connections: {len(spec.connections)}")
        
        # Route to appropriate engine
        engine = self.engines.get(diagram_type)
        if not engine:
            # Default to cloud architecture
            logger.warning(f"[UNIVERSAL_GENERATOR] Unknown diagram type '{diagram_type}', using cloud_architecture")
            engine = self.engines["cloud_architecture"]
        
        # Render
        logger.debug(f"[UNIVERSAL_GENERATOR] Using engine: {type(engine).__name__}")
        output_path = engine.render(spec)
        logger.info(f"[UNIVERSAL_GENERATOR] Diagram generated: {output_path}")
        
        return output_path

