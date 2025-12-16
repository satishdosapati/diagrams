"""
Graphviz attribute presets for common diagram styling themes.

These presets can be used to quickly apply consistent styling to diagrams.
Reference: https://www.graphviz.org/doc/info/attrs.html
"""

from typing import Dict
from ..models.spec import GraphvizAttributes


GRAPHVIZ_PRESETS: Dict[str, GraphvizAttributes] = {
    "dark_theme": GraphvizAttributes(
        graph_attr={
            "bgcolor": "#1e1e1e",
            "fontcolor": "white",
            "fontname": "Arial",
            "fontsize": "12"
        },
        node_attr={
            "style": "filled",
            "fillcolor": "#2d2d2d",
            "fontcolor": "white",
            "shape": "box",
            "penwidth": "1.5",
            "labelloc": "b",
            "labeldistance": "0.3"
        },
        edge_attr={
            "color": "#888888",
            "fontcolor": "white",
            "penwidth": "1.5",
            "labeldistance": "0.6",
            "labelfontsize": "10",
            "labelloc": "c",
            "labelangle": "0"
        }
    ),
    
    "light_theme": GraphvizAttributes(
        graph_attr={
            "bgcolor": "#ffffff",
            "fontcolor": "#333333",
            "fontname": "Arial",
            "fontsize": "12"
        },
        node_attr={
            "style": "filled",
            "fillcolor": "#f0f0f0",
            "fontcolor": "#333333",
            "shape": "box",
            "penwidth": "1.5",
            "labelloc": "b",
            "labeldistance": "0.3"
        },
        edge_attr={
            "color": "#666666",
            "fontcolor": "#333333",
            "penwidth": "1.5",
            "labeldistance": "0.6",
            "labelfontsize": "10",
            "labelloc": "c",
            "labelangle": "0"
        }
    ),
    
    "horizontal_layout": GraphvizAttributes(
        graph_attr={
            "rankdir": "LR",  # Left to Right
            "nodesep": "0.8",
            "ranksep": "1.0"
        },
        node_attr={},
        edge_attr={}
    ),
    
    "vertical_layout": GraphvizAttributes(
        graph_attr={
            "rankdir": "TB",  # Top to Bottom (default)
            "nodesep": "0.8",
            "ranksep": "1.0"
        },
        node_attr={},
        edge_attr={}
    ),
    
    "compact": GraphvizAttributes(
        graph_attr={
            "nodesep": "0.3",
            "ranksep": "0.3",
            "margin": "0.2"
        },
        node_attr={},
        edge_attr={}
    ),
    
    "spacious": GraphvizAttributes(
        graph_attr={
            "nodesep": "1.5",
            "ranksep": "2.0",
            "margin": "0.5"
        },
        node_attr={},
        edge_attr={}
    ),
    
    "rounded_nodes": GraphvizAttributes(
        graph_attr={},
        node_attr={
            "style": "rounded,filled",
            "shape": "box"
        },
        edge_attr={}
    ),
    
    "minimal": GraphvizAttributes(
        graph_attr={
            "bgcolor": "transparent"
        },
        node_attr={
            "style": "filled",
            "fillcolor": "white",
            "penwidth": "1",
            "labelloc": "b",
            "labeldistance": "0.3"
        },
        edge_attr={
            "color": "#333333",
            "penwidth": "1",
            "labeldistance": "0.6",
            "labelfontsize": "10",
            "labelloc": "c",
            "labelangle": "0"
        }
    ),
    
    "colorful": GraphvizAttributes(
        graph_attr={
            "bgcolor": "#f8f8f8"
        },
        node_attr={
            "style": "filled,rounded",
            "shape": "box",
            "penwidth": "2"
        },
        edge_attr={
            "color": "#4a90e2",
            "penwidth": "2",
            "arrowsize": "1.2",
            "labeldistance": "0.6",
            "labelfontsize": "10",
            "labelloc": "c",
            "labelangle": "0"
        }
    ),
    
    "professional": GraphvizAttributes(
        graph_attr={
            "bgcolor": "#ffffff",
            "fontname": "Helvetica",
            "fontsize": "11",
            "splines": "ortho"  # Orthogonal edges
        },
        node_attr={
            "style": "filled,rounded",
            "fillcolor": "#e8f4f8",
            "fontcolor": "#2c3e50",
            "shape": "box",
            "penwidth": "1.5",
            "labelloc": "b",
            "labeldistance": "0.3"
        },
        edge_attr={
            "color": "#34495e",
            "fontcolor": "#2c3e50",
            "penwidth": "1.5",
            "arrowsize": "0.8",
            "labeldistance": "0.6",
            "labelfontsize": "10",
            "labelloc": "c",
            "labelangle": "0"
        }
    )
}


def get_preset(name: str) -> GraphvizAttributes:
    """
    Get a Graphviz attributes preset by name.
    
    Args:
        name: Preset name (e.g., "dark_theme", "horizontal_layout")
        
    Returns:
        GraphvizAttributes instance
        
    Raises:
        ValueError: If preset name is not found
    """
    if name not in GRAPHVIZ_PRESETS:
        available = ", ".join(GRAPHVIZ_PRESETS.keys())
        raise ValueError(
            f"Preset '{name}' not found. Available presets: {available}"
        )
    return GRAPHVIZ_PRESETS[name]


def list_presets() -> list[str]:
    """Return list of available preset names."""
    return list(GRAPHVIZ_PRESETS.keys())


def merge_presets(*preset_names: str) -> GraphvizAttributes:
    """
    Merge multiple presets, with later presets overriding earlier ones.
    
    Args:
        *preset_names: One or more preset names to merge
        
    Returns:
        Merged GraphvizAttributes instance
        
    Example:
        merged = merge_presets("horizontal_layout", "dark_theme")
    """
    if not preset_names:
        return GraphvizAttributes()
    
    # Start with first preset
    result = get_preset(preset_names[0])
    
    # Merge remaining presets
    for name in preset_names[1:]:
        preset = get_preset(name)
        # Merge dictionaries (later values override earlier ones)
        result.graph_attr = {**result.graph_attr, **preset.graph_attr}
        result.node_attr = {**result.node_attr, **preset.node_attr}
        result.edge_attr = {**result.edge_attr, **preset.edge_attr}
    
    return result

