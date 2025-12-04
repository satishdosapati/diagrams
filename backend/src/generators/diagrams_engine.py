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
    
    def __init__(self, output_dir: str = None):
        """Initialize the engine with output directory."""
        if output_dir is None:
            output_dir = os.getenv("OUTPUT_DIR", "./output")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def render(self, spec: ArchitectureSpec) -> str:
        """
        Render diagram from ArchitectureSpec.
        
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
        # diagrams library filename parameter should be just the base name (no path, no extension)
        filename = spec.title.lower().replace(" ", "_")
        lines.append(f'with Diagram("{spec.title}", show=False, filename="{filename}"):')
        
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
        # Note: The diagrams library doesn't support labeled edges via >> operator
        # Labels are ignored and simple connections are created
        if spec.connections:
            lines.append("")
            for conn in spec.connections:
                from_var = component_vars.get(conn.from_id)
                to_var = component_vars.get(conn.to_id)
                
                if from_var and to_var:
                    # Create simple connection (labels not supported by diagrams library)
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
                error_msg = f"Diagram generation failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
                raise RuntimeError(error_msg)
            
            # Find generated file - diagrams library generates files based on filename parameter
            # List all PNG files in output directory to find the generated one
            filename_base = title.lower().replace(" ", "_")
            expected_path = self.output_dir / f"{filename_base}.png"
            
            # Check if expected file exists
            if expected_path.exists():
                return str(expected_path)
            
            # If not found, search for PNG files created recently (within last 5 seconds)
            # This handles cases where the filename might differ slightly
            import time
            current_time = time.time()
            png_files = list(self.output_dir.glob("*.png"))
            
            # Find most recently created PNG file
            if png_files:
                # Sort by modification time, most recent first
                png_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                most_recent = png_files[0]
                # Check if it was created recently (within last 5 seconds)
                file_time = most_recent.stat().st_mtime
                if current_time - file_time < 5:
                    return str(most_recent)
            
            # If still not found, provide detailed error
            available_files = [f.name for f in self.output_dir.glob("*.png")]
            error_msg = (
                f"Diagram file not found: {expected_path}\n"
                f"Available PNG files: {available_files}\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )
            raise RuntimeError(error_msg)
            
        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.unlink(temp_file)

