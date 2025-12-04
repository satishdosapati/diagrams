"""
DiagramsEngine - Generates diagrams using Diagrams library with multi-provider support.
"""
import tempfile
import subprocess
import os
from pathlib import Path

from ..models.spec import ArchitectureSpec
from ..resolvers.component_resolver import ComponentResolver


class DiagramsEngine:
    """Generates architecture diagrams using the Diagrams library."""
    
    def __init__(self, output_dir: str = "./output"):
        """Initialize the engine with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate(self, spec: ArchitectureSpec) -> str:
        """
        Generate diagram from ArchitectureSpec.
        
        Args:
            spec: Architecture specification
            
        Returns:
            Path to generated diagram file
        """
        # Create resolver
        resolver = ComponentResolver(primary_provider=spec.provider)
        
        # Generate Python code
        code = self._generate_code(spec, resolver)
        
        # Execute code and generate diagram
        output_path = self._execute_code(code, spec.title)
        
        return output_path
    
    def _generate_code(self, spec: ArchitectureSpec, resolver: ComponentResolver) -> str:
        """Generate Python code for Diagrams library."""
        lines = []
        
        # Generate imports based on components used
        imports = self._generate_imports(spec, resolver)
        lines.extend(imports)
        lines.append("")
        
        # Diagram context
        filename = spec.title.lower().replace(" ", "_")
        output_path = str(self.output_dir / filename)
        lines.append(f'with Diagram("{spec.title}", show=False, filename="{output_path}"):')
        
        # Generate component variables
        component_vars = {}
        indent = "    "
        
        for comp in spec.components:
            var_name = comp.id.replace("-", "_")
            node_class = resolver.resolve_component_class(comp)
            
            module = node_class.__module__
            class_name = node_class.__name__
            
            lines.append(f'{indent}{var_name} = {class_name}("{comp.name}")')
            component_vars[comp.id] = var_name
        
        # Generate connections
        if spec.connections:
            lines.append("")
            for conn in spec.connections:
                from_var = component_vars.get(conn.from_id)
                to_var = component_vars.get(conn.to_id)
                
                if from_var and to_var:
                    if conn.label:
                        lines.append(f'{indent}{from_var} >> "{conn.label}" >> {to_var}')
                    else:
                        lines.append(f'{indent}{from_var} >> {to_var}')
        
        return "\n".join(lines)
    
    def _generate_imports(self, spec: ArchitectureSpec, resolver: ComponentResolver) -> list[str]:
        """Generate import statements based on components used."""
        imports_set = set()
        imports_set.add("from diagrams import Diagram")
        
        for comp in spec.components:
            node_class = resolver.resolve_component_class(comp)
            module = node_class.__module__
            class_name = node_class.__name__
            imports_set.add(f"from {module} import {class_name}")
        
        return sorted(imports_set)
    
    def _execute_code(self, code: str, title: str) -> str:
        """Execute generated code safely."""
        # Create temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                cwd=str(self.output_dir),
                timeout=30
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Diagram generation failed: {result.stderr}")
            
            # Find generated file
            filename = title.lower().replace(" ", "_")
            output_path = self.output_dir / f"{filename}.png"
            
            if not output_path.exists():
                raise RuntimeError(f"Diagram file not found: {output_path}")
            
            return str(output_path)
            
        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.unlink(temp_file)

