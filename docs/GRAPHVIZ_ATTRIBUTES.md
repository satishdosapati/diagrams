# Graphviz Attributes Support

This document describes how to use custom Graphviz attributes to style and customize diagrams.

## Overview

The diagram generator supports custom Graphviz attributes at three levels:
1. **Graph-level** (`graph_attr`) - Affects the entire diagram
2. **Node-level** (`node_attr`) - Default attributes for all nodes
3. **Edge-level** (`edge_attr`) - Default attributes for all edges

Additionally, you can specify attributes for:
- **Individual components** - Override default node attributes
- **Individual connections** - Override default edge attributes

## Reference

For a complete list of available Graphviz attributes, see:
https://www.graphviz.org/doc/info/attrs.html

## API Usage

### Basic Example

```json
{
  "description": "Simple API with Lambda and DynamoDB",
  "provider": "aws",
  "graphviz_attrs": {
    "graph_attr": {
      "rankdir": "LR",
      "bgcolor": "#f0f0f0"
    },
    "node_attr": {
      "shape": "box",
      "style": "rounded,filled"
    },
    "edge_attr": {
      "color": "#333333",
      "arrowsize": "0.8"
    }
  }
}
```

### Common Graph Attributes

- `rankdir`: Layout direction - `"LR"` (left-right), `"TB"` (top-bottom), `"RL"` (right-left), `"BT"` (bottom-top)
- `bgcolor`: Background color (e.g., `"#ffffff"`, `"transparent"`)
- `fontname`: Font family (e.g., `"Arial"`, `"Helvetica"`)
- `fontsize`: Font size (e.g., `"12"`, `"14"`)
- `nodesep`: Minimum separation between nodes (e.g., `"0.8"`)
- `ranksep`: Minimum separation between ranks (e.g., `"1.0"`)
- `splines`: Edge routing style - `"ortho"` (orthogonal), `"curved"`, `"polyline"`

### Common Node Attributes

- `shape`: Node shape - `"box"`, `"ellipse"`, `"circle"`, `"diamond"`, etc.
- `style`: Node style - `"filled"`, `"rounded"`, `"dashed"`, `"dotted"`, or combinations like `"filled,rounded"`
- `fillcolor`: Fill color (e.g., `"#e8f4f8"`)
- `fontcolor`: Text color (e.g., `"#2c3e50"`)
- `penwidth`: Border width (e.g., `"1.5"`)

### Common Edge Attributes

- `color`: Edge color (e.g., `"#333333"`, `"blue"`)
- `style`: Edge style - `"solid"`, `"dashed"`, `"dotted"`, `"bold"`
- `arrowsize`: Arrow size (e.g., `"0.8"`, `"1.2"`)
- `penwidth`: Edge width (e.g., `"1.5"`, `"2.0"`)
- `label`: Edge label text

## Using Presets

The system includes several preset themes that can be used:

```python
from backend.src.generators.graphviz_presets import get_preset, merge_presets

# Use a single preset
dark_theme = get_preset("dark_theme")

# Merge multiple presets
custom = merge_presets("horizontal_layout", "dark_theme")
```

Available presets:
- `dark_theme` - Dark background with light text
- `light_theme` - Light background with dark text
- `horizontal_layout` - Left-to-right layout
- `vertical_layout` - Top-to-bottom layout
- `compact` - Tight spacing
- `spacious` - Loose spacing
- `rounded_nodes` - Rounded node corners
- `minimal` - Minimal styling
- `colorful` - Colorful styling
- `professional` - Professional business style

## Component-Level Attributes

You can override node attributes for specific components:

```json
{
  "components": [
    {
      "id": "api",
      "name": "API Gateway",
      "type": "api_gateway",
      "graphviz_attrs": {
        "fillcolor": "#ff6b6b",
        "fontcolor": "white",
        "style": "filled,rounded"
      }
    }
  ]
}
```

## Connection-Level Attributes

You can customize individual edges:

```json
{
  "connections": [
    {
      "from_id": "api",
      "to_id": "lambda",
      "label": "HTTP",
      "graphviz_attrs": {
        "color": "blue",
        "style": "bold",
        "arrowsize": "1.2"
      }
    }
  ]
}
```

## Examples

### Horizontal Layout with Dark Theme

```json
{
  "description": "Microservices architecture",
  "provider": "aws",
  "graphviz_attrs": {
    "graph_attr": {
      "rankdir": "LR",
      "bgcolor": "#1e1e1e",
      "fontcolor": "white"
    },
    "node_attr": {
      "style": "filled,rounded",
      "fillcolor": "#2d2d2d",
      "fontcolor": "white"
    },
    "edge_attr": {
      "color": "#888888",
      "fontcolor": "white"
    }
  }
}
```

### Professional Style with Orthogonal Edges

```json
{
  "description": "Enterprise architecture",
  "provider": "aws",
  "graphviz_attrs": {
    "graph_attr": {
      "splines": "ortho",
      "bgcolor": "#ffffff",
      "fontname": "Helvetica"
    },
    "node_attr": {
      "style": "filled,rounded",
      "fillcolor": "#e8f4f8",
      "fontcolor": "#2c3e50"
    },
    "edge_attr": {
      "color": "#34495e",
      "arrowsize": "0.8"
    }
  }
}
```

## Notes

- All attributes are optional - diagrams will use sensible defaults if not specified
- Attribute values are validated by Graphviz - invalid values may cause diagram generation to fail
- String values with quotes should be properly escaped (handled automatically by the API)
- Color values can be hex codes (`"#ffffff"`), named colors (`"red"`), or RGB (`"rgb(255,0,0)"`)
- Multiple style values can be combined with commas (e.g., `"filled,rounded"`)

