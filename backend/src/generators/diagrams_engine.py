"""
DiagramsEngine - Generates diagrams using Diagrams library with multi-provider support.
"""
import tempfile
import subprocess
import os
import time
import logging
from pathlib import Path
from typing import Optional, Union, List

from ..models.spec import ArchitectureSpec
from ..resolvers.component_resolver import ComponentResolver

logger = logging.getLogger(__name__)

# Valid Graphviz output formats
VALID_FORMATS = {
    "png", "svg", "pdf", "dot", "eps", "ps", "ps2", "webp", 
    "json", "json0", "svgz", "gv", "canon", "cmap", "cmapx",
    "cmapx_np", "dot_json", "fig", "imap", "imap_np", "ismap",
    "mp", "pic", "plain", "plain-ext", "pov", "tk", "vdx",
    "vml", "vmlz", "x11", "xdot", "xdot1.2", "xdot1.4",
    "xdot_json", "xlib"
}

# Format normalization mapping (invalid -> valid)
FORMAT_NORMALIZATION = {
    "gif": "png",  # GIF not supported, use PNG
}


def normalize_format(format_str: str) -> str:
    """
    Normalize output format to a valid Graphviz format.
    
    Args:
        format_str: Format string (e.g., "png", "svg", "pdf")
        
    Returns:
        Normalized format string (valid Graphviz format)
    """
    if not format_str:
        return "png"
    
    format_lower = format_str.lower().strip()
    
    # Check normalization mapping first
    if format_lower in FORMAT_NORMALIZATION:
        normalized = FORMAT_NORMALIZATION[format_lower]
        logger.warning(f"Format '{format_str}' not supported, using '{normalized}' instead")
        return normalized
    
    # If already valid, return as-is
    if format_lower in VALID_FORMATS:
        return format_lower
    
    # Default to PNG for unknown formats
    logger.warning(f"Unknown format '{format_str}', defaulting to 'png'")
    return "png"


def normalize_format_list(formats: Union[str, List[str]]) -> Union[str, List[str]]:
    """
    Normalize a single format string or list of formats.
    
    Args:
        formats: Single format string or list of format strings
        
    Returns:
        Normalized format(s)
    """
    if isinstance(formats, list):
        return [normalize_format(f) for f in formats]
    return normalize_format(formats)


# Python reserved keywords that cannot be used as variable names
PYTHON_RESERVED_KEYWORDS = {
    "and", "as", "assert", "break", "class", "continue", "def", "del", "elif", "else",
    "except", "False", "finally", "for", "from", "global", "if", "import", "in", "is",
    "lambda", "None", "nonlocal", "not", "or", "pass", "raise", "return", "True", "try",
    "while", "with", "yield"
}


def sanitize_variable_name(name: str) -> str:
    """
    Sanitize a variable name to ensure it's a valid Python identifier and not a reserved keyword.
    
    Args:
        name: Variable name to sanitize
        
    Returns:
        Sanitized variable name that is safe to use in Python code
    """
    if not name:
        return "comp"
    
    # Replace hyphens with underscores
    sanitized = name.replace("-", "_")
    
    # Normalize to check against keywords (Python keywords are case-insensitive for reservation)
    normalized = sanitized.lower()
    
    # Check if it's a reserved keyword (case-insensitive check)
    if normalized in PYTHON_RESERVED_KEYWORDS:
        # Append suffix to make it safe
        sanitized = f"{sanitized}_comp"
    
    # Ensure it starts with a letter or underscore (Python identifier rules)
    if sanitized and not (sanitized[0].isalpha() or sanitized[0] == "_"):
        sanitized = f"_{sanitized}"
    
    # Ensure it's a valid Python identifier
    if not sanitized.isidentifier():
        # Replace invalid characters with underscores
        sanitized = "".join(c if c.isalnum() or c == "_" else "_" for c in sanitized)
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"comp_{sanitized}"
        # Final check - if still not valid, prefix with comp_
        if not sanitized.isidentifier():
            sanitized = f"comp_{sanitized}"
    
    # Final safety check: if somehow it's still a keyword, append suffix again
    if sanitized.lower() in PYTHON_RESERVED_KEYWORDS:
        sanitized = f"{sanitized}_comp"
    
    return sanitized


class DiagramsEngine:
    """Generates architecture diagrams using the Diagrams library."""
    
    def __init__(self, output_dir: str = None):
        """Initialize the engine with output directory."""
        if output_dir is None:
            output_dir = os.getenv("OUTPUT_DIR", "./output")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Cleanup old files on initialization
        self._cleanup_old_files()
    
    def render(self, spec: ArchitectureSpec) -> str:
        """
        Render diagram from ArchitectureSpec.
        
        Args:
            spec: Architecture specification
            
        Returns:
            Path to generated diagram file (primary format, typically PNG)
        """
        # Normalize output format if specified
        if spec.outformat:
            spec.outformat = normalize_format_list(spec.outformat)
        
        # Create resolver
        resolver = ComponentResolver(primary_provider=spec.provider)
        
        # Generate Python code
        code = self._generate_code(spec, resolver)
        
        # Execute code and generate diagram(s)
        output_path = self._execute_code(code, spec.title, spec.outformat)
        
        return output_path
    
    def _generate_code(self, spec: ArchitectureSpec, resolver: ComponentResolver) -> str:
        """Generate Python code for Diagrams library."""
        lines = []
        
        # Generate imports based on components used
        imports = self._generate_imports(spec, resolver)
        lines.extend(imports)
        lines.append("")
        
        # Build Diagram constructor parameters
        filename = spec.title.lower().replace(" ", "_")
        diagram_params = [
            f'"{spec.title}"',
            'show=False',
            f'filename="{filename}"'
        ]
        
        # Add direction parameter if specified
        if spec.direction:
            diagram_params.append(f'direction="{spec.direction}"')
        
        # Add outformat parameter if specified (normalize first)
        if spec.outformat:
            normalized_format = normalize_format_list(spec.outformat)
            if isinstance(normalized_format, list):
                outformat_str = str(normalized_format).replace("'", '"')
                diagram_params.append(f'outformat={outformat_str}')
            else:
                diagram_params.append(f'outformat="{normalized_format}"')
        
        # Add Graphviz attributes if provided
        if spec.graphviz_attrs:
            if spec.graphviz_attrs.graph_attr:
                graph_attr_str = self._format_attr_dict(spec.graphviz_attrs.graph_attr)
                diagram_params.append(f'graph_attr={graph_attr_str}')
            if spec.graphviz_attrs.node_attr:
                node_attr_str = self._format_attr_dict(spec.graphviz_attrs.node_attr)
                diagram_params.append(f'node_attr={node_attr_str}')
            if spec.graphviz_attrs.edge_attr:
                edge_attr_str = self._format_attr_dict(spec.graphviz_attrs.edge_attr)
                diagram_params.append(f'edge_attr={edge_attr_str}')
        
        lines.append(f'with Diagram({", ".join(diagram_params)}):')
        
        # Generate component variables and clusters
        component_vars = {}
        cluster_vars = {}
        indent = "    "
        
        # Build component ID to cluster mapping
        component_to_cluster = {}
        for cluster in spec.clusters:
            for comp_id in cluster.component_ids:
                component_to_cluster[comp_id] = cluster.id
        
        # Generate components (those not in clusters first)
        components_in_clusters = set()
        for cluster in spec.clusters:
            components_in_clusters.update(cluster.component_ids)
        
        # Generate standalone components (not in any cluster)
        for comp in spec.components:
            if comp.id not in components_in_clusters:
                var_name = sanitize_variable_name(comp.id)
                
                # Handle blank/placeholder nodes
                if comp.is_blank_node or (isinstance(comp.type, str) and comp.type.lower() in ["blank", "placeholder"]):
                    # Generate blank node: Node("", shape="plaintext", width="0", height="0")
                    blank_attrs = comp.graphviz_attrs or {}
                    blank_attrs.setdefault("shape", "plaintext")
                    blank_attrs.setdefault("width", "0")
                    blank_attrs.setdefault("height", "0")
                    attrs_str = self._format_attr_dict(blank_attrs)
                    lines.append(f'{indent}{var_name} = Node("", **{attrs_str})')
                    component_vars[comp.id] = var_name
                else:
                    node_class = resolver.resolve_component_class(comp)
                    
                    module = node_class.__module__
                    class_name = node_class.__name__
                    
                    # Check if component has custom Graphviz attributes
                    if comp.graphviz_attrs:
                        attrs_str = self._format_attr_dict(comp.graphviz_attrs)
                        lines.append(f'{indent}{var_name} = {class_name}("{comp.name}", **{attrs_str})')
                    else:
                        lines.append(f'{indent}{var_name} = {class_name}("{comp.name}")')
                    component_vars[comp.id] = var_name
        
        # Generate clusters (with parent_id-based nesting support)
        if spec.clusters:
            lines.append("")
            # Build cluster hierarchy from parent_id references
            cluster_map = {cluster.id: cluster for cluster in spec.clusters}
            root_clusters = [c for c in spec.clusters if not c.parent_id]
            
            # Generate root clusters first, then nested ones
            for cluster in root_clusters:
                self._generate_cluster_with_nesting(
                    cluster, spec.clusters, spec.components, resolver,
                    lines, component_vars, cluster_vars, indent, cluster_map
                )
        
        # Generate connections with group data flow support
        if spec.connections:
            lines.append("")
            self._generate_connections(spec.connections, component_vars, lines, indent)
        
        return "\n".join(lines)
    
    def _generate_cluster_with_nesting(
        self,
        cluster,
        all_clusters: list,
        all_components: list,
        resolver: ComponentResolver,
        lines: list,
        component_vars: dict,
        cluster_vars: dict,
        indent: str,
        cluster_map: dict
    ):
        """Generate cluster code block with parent_id-based nesting support."""
        cluster_var = sanitize_variable_name(cluster.id)
        cluster_vars[cluster.id] = cluster_var
        
        # Build Cluster constructor parameters
        cluster_params = [f'"{cluster.name}"']
        
        # Add cluster Graphviz attributes if provided
        if cluster.graphviz_attrs:
            cluster_attr_str = self._format_attr_dict(cluster.graphviz_attrs)
            cluster_params.append(f'graph_attr={cluster_attr_str}')
        
        lines.append(f'{indent}with Cluster({", ".join(cluster_params)}):')
        cluster_indent = indent + "    "
        
        # Generate components in this cluster
        cluster_component_map = {comp.id: comp for comp in all_components}
        for comp_id in cluster.component_ids:
            comp = cluster_component_map.get(comp_id)
            if comp:
                var_name = sanitize_variable_name(comp.id)
                
                # Handle blank/placeholder nodes
                if comp.is_blank_node or (isinstance(comp.type, str) and comp.type.lower() in ["blank", "placeholder"]):
                    # Generate blank node: Node("", shape="plaintext", width="0", height="0")
                    blank_attrs = comp.graphviz_attrs or {}
                    blank_attrs.setdefault("shape", "plaintext")
                    blank_attrs.setdefault("width", "0")
                    blank_attrs.setdefault("height", "0")
                    attrs_str = self._format_attr_dict(blank_attrs)
                    lines.append(f'{cluster_indent}{var_name} = Node("", **{attrs_str})')
                    component_vars[comp.id] = var_name
                else:
                    node_class = resolver.resolve_component_class(comp)
                    
                    module = node_class.__module__
                    class_name = node_class.__name__
                    
                    # Check if component has custom Graphviz attributes
                    if comp.graphviz_attrs:
                        attrs_str = self._format_attr_dict(comp.graphviz_attrs)
                        lines.append(f'{cluster_indent}{var_name} = {class_name}("{comp.name}", **{attrs_str})')
                    else:
                        lines.append(f'{cluster_indent}{var_name} = {class_name}("{comp.name}")')
                    component_vars[comp.id] = var_name
        
        # Generate nested clusters (children with this cluster as parent)
        child_clusters = [c for c in all_clusters if c.parent_id == cluster.id]
        if child_clusters:
            lines.append("")
            for child_cluster in child_clusters:
                self._generate_cluster_with_nesting(
                    child_cluster, all_clusters, all_components, resolver,
                    lines, component_vars, cluster_vars, cluster_indent, cluster_map
                )
    
    def _generate_connections(
        self, 
        connections: list, 
        component_vars: dict,
        lines: list,
        indent: str
    ):
        """Generate connection code with group data flow and direction support."""
        from collections import defaultdict
        
        # Group connections by (from_var, to_var) to detect duplicates
        # Also group by target for potential group data flow optimization
        connection_map = {}
        target_groups = defaultdict(list)
        
        for conn in connections:
            from_var = component_vars.get(conn.from_id)
            to_var = component_vars.get(conn.to_id)
            
            if not (from_var and to_var):
                continue
            
            conn_key = (from_var, to_var)
            
            # Store connection (keep first occurrence if duplicates)
            if conn_key not in connection_map:
                connection_map[conn_key] = conn
                target_groups[to_var].append((from_var, conn))
        
        # Generate connections - process grouped targets first, then individual
        processed_connections = set()
        
        # First, handle grouped connections (multiple sources to same target)
        for to_var, sources_list in target_groups.items():
            if len(sources_list) > 1:
                # Check if all connections are simple (no labels/attrs) and same direction
                # Only group if they're simple forward connections
                can_group = True
                first_conn = sources_list[0][1]
                
                for from_var, conn in sources_list:
                    if conn.label or conn.graphviz_attrs or conn.direction not in (None, "forward"):
                        can_group = False
                        break
                    if (from_var, to_var) in processed_connections:
                        can_group = False
                        break
                
                if can_group:
                    # Use list-based connection for cleaner grouping
                    sources_vars = [src for src, _ in sources_list]
                    sources_list_str = f"[{', '.join(sources_vars)}]"
                    self._generate_single_connection(
                        sources_list_str, to_var, first_conn, lines, indent, is_group=True
                    )
                    # Mark all grouped connections as processed
                    for from_var, _ in sources_list:
                        processed_connections.add((from_var, to_var))
                    continue
        
        # Generate remaining individual connections
        for conn_key, conn in connection_map.items():
            if conn_key in processed_connections:
                continue
            
            from_var, to_var = conn_key
            self._generate_single_connection(from_var, to_var, conn, lines, indent)
            processed_connections.add(conn_key)
    
    def _generate_single_connection(
        self, 
        from_var: str, 
        to_var: str, 
        conn, 
        lines: list,
        indent: str,
        is_group: bool = False
    ):
        """Generate a single connection with optional label, attributes, and direction."""
        # Determine connection operator based on direction
        if conn.direction == "backward":
            operator = "<<"
        elif conn.direction == "bidirectional":
            operator = "-"
        else:
            operator = ">>"  # default forward
        
        # Handle group connections (list of sources to single target)
        if is_group and isinstance(from_var, str) and from_var.startswith("["):
            # Group connection: [source1, source2, ...] >> target
            if conn.label or conn.graphviz_attrs:
                edge_args = []
                if conn.label:
                    edge_args.append(f'label="{conn.label}"')
                if conn.graphviz_attrs:
                    for key, value in conn.graphviz_attrs.items():
                        if isinstance(value, str):
                            escaped_value = value.replace('"', '\\"')
                            edge_args.append(f'{key}="{escaped_value}"')
                        elif isinstance(value, (int, float)):
                            edge_args.append(f'{key}={value}')
                        elif isinstance(value, bool):
                            edge_args.append(f'{key}={str(value).lower()}')
                        else:
                            escaped_value = str(value).replace('"', '\\"')
                            edge_args.append(f'{key}="{escaped_value}"')
                edge_params = ", ".join(edge_args)
                lines.append(f'{indent}{from_var} >> Edge({edge_params}) >> {to_var}')
            else:
                lines.append(f'{indent}{from_var} >> {to_var}')
            return
        
        # Create connection with optional label and custom attributes
        if conn.label or conn.graphviz_attrs:
            # Build Edge constructor arguments
            edge_args = []
            if conn.label:
                edge_args.append(f'label="{conn.label}"')
            if conn.graphviz_attrs:
                # Add graphviz attributes as kwargs
                for key, value in conn.graphviz_attrs.items():
                    if isinstance(value, str):
                        escaped_value = value.replace('"', '\\"')
                        edge_args.append(f'{key}="{escaped_value}"')
                    elif isinstance(value, (int, float)):
                        edge_args.append(f'{key}={value}')
                    elif isinstance(value, bool):
                        edge_args.append(f'{key}={str(value).lower()}')
                    else:
                        escaped_value = str(value).replace('"', '\\"')
                        edge_args.append(f'{key}="{escaped_value}"')
            edge_params = ", ".join(edge_args)
            
            if operator == "-":
                # Bidirectional with Edge
                lines.append(f'{indent}{from_var} - Edge({edge_params}) - {to_var}')
            elif operator == "<<":
                # Backward with Edge
                lines.append(f'{indent}{to_var} << Edge({edge_params}) << {from_var}')
            else:
                # Forward with Edge
                lines.append(f'{indent}{from_var} >> Edge({edge_params}) >> {to_var}')
        else:
            # Simple connection
            if operator == "-":
                lines.append(f'{indent}{from_var} - {to_var}')
            elif operator == "<<":
                lines.append(f'{indent}{to_var} << {from_var}')
            else:
                lines.append(f'{indent}{from_var} >> {to_var}')
    
    def _format_attr_dict(self, attrs: dict) -> str:
        """
        Format attribute dictionary for Python code generation.
        
        Args:
            attrs: Dictionary of Graphviz attributes
            
        Returns:
            Formatted string representation of the dictionary
        """
        if not attrs:
            return "{}"
        
        formatted_items = []
        for key, value in attrs.items():
            # Handle different value types
            if isinstance(value, str):
                # Escape quotes in strings
                escaped_value = value.replace('"', '\\"')
                formatted_items.append(f'"{key}": "{escaped_value}"')
            elif isinstance(value, (int, float)):
                formatted_items.append(f'"{key}": {value}')
            elif isinstance(value, bool):
                formatted_items.append(f'"{key}": {str(value).lower()}')
            elif isinstance(value, list):
                # Handle lists (e.g., style="filled,rounded")
                if all(isinstance(item, str) for item in value):
                    list_str = ",".join(str(item) for item in value)
                    formatted_items.append(f'"{key}": "{list_str}"')
                else:
                    formatted_items.append(f'"{key}": {value}')
            else:
                # Fallback: convert to string
                escaped_value = str(value).replace('"', '\\"')
                formatted_items.append(f'"{key}": "{escaped_value}"')
        
        return "{" + ", ".join(formatted_items) + "}"
    
    def _generate_imports(self, spec: ArchitectureSpec, resolver: ComponentResolver) -> list[str]:
        """Generate import statements based on components used."""
        imports_set = set()
        imports_set.add("from diagrams import Diagram")
        
        # Check if Cluster import is needed
        if spec.clusters:
            imports_set.add("from diagrams import Cluster")
        
        # Check if Edge import is needed for labeled/custom connections
        needs_edge = any(
            conn.label or conn.graphviz_attrs 
            for conn in spec.connections
        )
        if needs_edge:
            imports_set.add("from diagrams import Edge")
        
        # Check if Node import is needed for blank nodes
        needs_node = any(
            comp.is_blank_node or (isinstance(comp.type, str) and comp.type.lower() in ["blank", "placeholder"])
            for comp in spec.components
        )
        if needs_node:
            imports_set.add("from diagrams import Node")
        
        for comp in spec.components:
            node_class = resolver.resolve_component_class(comp)
            module = node_class.__module__
            class_name = node_class.__name__
            imports_set.add(f"from {module} import {class_name}")
        
        return sorted(imports_set)
    
    def _execute_code(self, code: str, title: str, outformat: Optional[Union[str, List[str]]] = None) -> str:
        """Execute generated code safely and return primary output file path."""
        # Normalize format before execution
        normalized_outformat = normalize_format_list(outformat) if outformat else None
        
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
            
            # Determine primary format (first in list, or default to PNG)
            if isinstance(normalized_outformat, list) and normalized_outformat:
                primary_format = normalized_outformat[0]
            elif isinstance(normalized_outformat, str):
                primary_format = normalized_outformat
            else:
                primary_format = "png"
            
            # Find generated file - diagrams library generates files based on filename parameter
            filename_base = title.lower().replace(" ", "_")
            expected_path = self.output_dir / f"{filename_base}.{primary_format}"
            
            # Check if expected file exists
            if expected_path.exists():
                return str(expected_path)
            
            # If not found, search for files with primary format created recently (within last 5 seconds)
            import time
            current_time = time.time()
            format_files = list(self.output_dir.glob(f"*.{primary_format}"))
            
            # Find most recently created file
            if format_files:
                # Sort by modification time, most recent first
                format_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                most_recent = format_files[0]
                # Check if it was created recently (within last 5 seconds)
                file_time = most_recent.stat().st_mtime
                if current_time - file_time < 5:
                    return str(most_recent)
            
            # Fallback: search for PNG files if primary format not found
            if primary_format != "png":
                png_files = list(self.output_dir.glob("*.png"))
                if png_files:
                    png_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                    most_recent = png_files[0]
                    file_time = most_recent.stat().st_mtime
                    if current_time - file_time < 5:
                        return str(most_recent)
            
            # If still not found, provide detailed error
            available_files = [f.name for f in self.output_dir.glob("*.*")]
            error_msg = (
                f"Diagram file not found: {expected_path}\n"
                f"Available files: {available_files}\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )
            raise RuntimeError(error_msg)
            
        finally:
            # Cleanup temporary Python file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            
            # Periodically cleanup old diagram files (older than 24 hours)
            self._cleanup_old_files()
    
    def _cleanup_old_files(self):
        """Remove diagram files older than 24 hours."""
        try:
            current_time = time.time()
            max_age = 24 * 3600  # 24 hours in seconds
            
            # Supported diagram file extensions
            extensions = ['.png', '.svg', '.pdf', '.dot', '.gif']
            
            for file_path in self.output_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in extensions:
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age:
                        try:
                            file_path.unlink()
                            logger.debug(f"Cleaned up old diagram file: {file_path.name}")
                        except OSError as e:
                            logger.warning(f"Failed to delete old file {file_path.name}: {e}")
        except Exception as e:
            logger.warning(f"Error during file cleanup: {e}")

