# Edge Routing Solutions for Complex Diagrams

## Problem Statement

As diagram complexity grows, arrows/edges become messy, overlapping, and difficult to follow. This document provides comprehensive solutions based on Graphviz and diagrams package documentation.

## Research Sources

- [Graphviz Documentation](https://www.graphviz.org/)
- [Graphviz Attributes Reference](https://graphviz.org/doc/info/attrs.html)
- [Diagrams Package - Edges Guide](https://diagrams.mingrammer.com/docs/guides/edge)
- [Graphviz Splines Documentation](https://graphviz.org/docs/attrs/splines/)

---

## Solutions Overview

### 1. Graph-Level Attributes (Primary Solutions)

These attributes control edge routing at the diagram level and are the most effective for complex diagrams.

#### 1.1. `splines` Attribute ⭐⭐⭐⭐⭐

**Purpose:** Controls how edges are drawn/routed between nodes.

**Options:**
- `"true"` (default in `dot` engine) - Edges drawn as splines routed around nodes
- `"false"` - Edges drawn as straight line segments
- `"polyline"` - Edges drawn as polylines (sequences of straight-line segments)
- `"ortho"` - Edges routed as polylines with axis-aligned segments (90-degree angles)
- `"curved"` - Edges drawn as curved arcs

**Recommendation for Complex Diagrams:**
```python
# For very complex diagrams (>15 connections)
graph_attr={"splines": "polyline"}

# For moderately complex diagrams (10-15 connections)
graph_attr={"splines": "ortho"}

# For simpler diagrams but still want clean routing
graph_attr={"splines": "polyline"}
```

**Important Notes:**
- When using `splines=true` or `splines=curved`, nodes should NOT overlap, or routing may revert to straight lines
- `splines=ortho` creates cleaner, more structured diagrams but may not work well for all layouts
- `splines=polyline` is a good compromise - cleaner than spline but more flexible than ortho

#### 1.2. `concentrate` Attribute ⭐⭐⭐⭐

**Purpose:** Merges parallel edges that share the same headport (endpoint) into a single edge.

**Usage:**
```python
graph_attr={"concentrate": "true"}
```

**When to Use:**
- Multiple edges connecting to the same target node
- Reduces visual clutter significantly
- Works best with `splines=true` or `splines=polyline`

**Example Scenario:**
```
Before: EC2-1 -> RDS, EC2-2 -> RDS, EC2-3 -> RDS (3 separate arrows)
After:  EC2-1, EC2-2, EC2-3 -> RDS (merged arrow)
```

#### 1.3. `overlap` Attribute ⭐⭐⭐⭐

**Purpose:** Prevents node overlaps, which is critical for proper edge routing.

**Options:**
- `"false"` - Enables automatic node overlap removal using Voronoi-based technique
- `"prism"` - Uses Prism algorithm for overlap removal
- `"scale"` - Scales the graph to prevent overlaps
- `"true"` (default) - Allows overlaps (NOT recommended for complex diagrams)

**Recommendation:**
```python
graph_attr={"overlap": "false"}
```

**Why Important:**
- Overlapping nodes cause edge routing to fail or create messy paths
- Essential when using `splines=true` or `splines=curved`

#### 1.4. Spacing Attributes ⭐⭐⭐⭐

**Purpose:** Control node and rank spacing to give edges more room to route cleanly.

**Attributes:**
- `nodesep` - Minimum horizontal distance between nodes in the same rank (default: 0.25 inches)
- `ranksep` - Minimum vertical distance between ranks (default: 0.5 inches for dot)

**Recommendations:**
```python
# For complex diagrams, increase spacing
graph_attr={
    "nodesep": "0.8",  # Increased from default 0.25
    "ranksep": "1.2"   # Increased from default 0.5
}
```

**Benefits:**
- More space = cleaner edge routing
- Reduces edge crossings
- Improves readability

#### 1.5. `radius` Attribute (for orthogonal edges)

**Purpose:** Controls the radius of rounded corners on orthogonal edges.

**Usage:**
```python
graph_attr={
    "splines": "ortho",
    "radius": "0.3"  # Rounded corners (default: 0 = square corners)
}
```

---

### 2. Edge-Level Attributes (Fine-Tuning)

These attributes control individual edges and can be used to optimize specific connections.

#### 2.1. `constraint` Attribute ⭐⭐⭐

**Purpose:** Controls whether an edge influences node ranking.

**Usage:**
```python
# Edge that shouldn't affect layout
Edge(constraint="false")
```

**When to Use:**
- For edges that are informational but shouldn't affect node positioning
- Can help reduce edge crossings

#### 2.2. `minlen` Attribute ⭐⭐⭐

**Purpose:** Sets minimum rank difference between head and tail nodes.

**Usage:**
```python
# Force more separation between nodes
Edge(minlen=2)
```

**Benefits:**
- Enforces greater separation between connected nodes
- Helps create more readable layouts
- Reduces edge density

#### 2.3. `weight` Attribute ⭐⭐⭐

**Purpose:** Assigns importance to an edge, influencing its length and straightness.

**Usage:**
```python
# Higher weight = shorter, straighter edge
Edge(weight=2)  # Default is 1
```

**Benefits:**
- Emphasizes important paths
- Reduces edge crossings
- Makes critical connections more visible

#### 2.4. `headport` and `tailport` Attributes ⭐⭐⭐⭐

**Purpose:** Controls which side/port of a node the edge connects to.

**Compass Points:**
- `n` (north), `ne` (northeast), `e` (east), `se` (southeast)
- `s` (south), `sw` (southwest), `w` (west), `nw` (northwest)
- `c` (center), `_` (default side)

**Usage:**
```python
# Connect from south of source to north of target
Edge(tailport="s", headport="n")
```

**Benefits:**
- Directs edges to specific sides of nodes
- Reduces edge crossings
- Creates more organized routing
- Especially useful for database connections (connect from bottom)

**Example for Database Connections:**
```python
# EC2 instances connect to RDS from bottom
ec2_1 >> Edge(tailport="s", headport="n") >> rds
ec2_2 >> Edge(tailport="s", headport="n") >> rds
```

#### 2.5. `samehead` and `sametail` Attributes ⭐⭐⭐

**Purpose:** Groups edges that share the same head/tail to converge at the same point.

**Usage:**
```python
# Multiple edges converging at same point
ec2_1 >> Edge(samehead="db_group") >> rds
ec2_2 >> Edge(samehead="db_group") >> rds
ec2_3 >> Edge(samehead="db_group") >> rds
```

**Benefits:**
- Reduces visual clutter
- Groups related connections
- Works well with `concentrate=true`

---

### 3. Layout Engine Considerations

Different Graphviz layout engines handle edge routing differently:

#### `dot` Engine (Default)
- Hierarchical/top-down layouts
- Best for: Flowcharts, organizational charts, architecture diagrams
- Default `splines=true` (splines routed around nodes)
- Works well with `splines=ortho` or `splines=polyline`

#### `neato` Engine
- Spring-model layouts
- Best for: Network diagrams, undirected graphs
- May require different spline settings

#### `fdp` Engine
- Force-directed placement
- Best for: Large, complex graphs
- May benefit from `splines=polyline`

**Recommendation:** Stick with `dot` engine for architecture diagrams (it's the default).

---

## Practical Recommendations

### For Your Multi-Region Architecture Diagram

Based on the screenshot showing EC2 instances and ALBs connecting to RDS databases with messy arrows:

#### Solution 1: Graph-Level Optimization (Recommended First)

```python
graph_attr={
    "splines": "polyline",      # Cleaner than spline, more flexible than ortho
    "concentrate": "true",       # Merge parallel edges
    "overlap": "false",          # Prevent node overlaps
    "nodesep": "0.8",            # More horizontal spacing
    "ranksep": "1.2"            # More vertical spacing
}
```

#### Solution 2: Edge-Level Port Control

For database connections specifically:

```python
# Use port control to route from bottom of EC2 to top of RDS
ec2_1 >> Edge(tailport="s", headport="n", style="dashed") >> rds_primary
ec2_2 >> Edge(tailport="s", headport="n", style="dashed") >> rds_primary
alb >> Edge(tailport="s", headport="n", style="dashed") >> rds_primary
```

#### Solution 3: Combined Approach (Best Results)

```python
# Graph-level
graph_attr={
    "splines": "polyline",
    "concentrate": "true",
    "overlap": "false",
    "nodesep": "1.0",
    "ranksep": "1.5"
}

# Edge-level (for database connections)
edge_attr={
    "arrowsize": "0.8",
    "penwidth": "1.0"
}

# Individual connections with ports
ec2_1 >> Edge(tailport="s", headport="n", style="dashed", minlen=2) >> rds_primary
```

---

## Implementation in Your Codebase

### Current Implementation

Your codebase already has some edge routing optimizations in `aws_architectural_advisor.py`:

```python
# Lines 560-593
if len(final_connections) > 15:
    graphviz_attrs.graph_attr["splines"] = "polyline"
    graphviz_attrs.graph_attr["concentrate"] = "true"
elif len(final_connections) > 10:
    graphviz_attrs.graph_attr["splines"] = "ortho"
else:
    graphviz_attrs.graph_attr["splines"] = "polyline"
```

### Recommended Enhancements

1. **Add `overlap=false`** for all complex diagrams
2. **Increase spacing** (`nodesep`, `ranksep`) for diagrams with >10 connections
3. **Add port control** for database connections (tailport="s", headport="n")
4. **Use `samehead`** for multiple edges to same target

### Code Example for Enhanced Edge Routing

```python
# In aws_architectural_advisor.py or diagrams_engine.py

def _apply_edge_routing_optimizations(graphviz_attrs, num_connections, has_database_connections=False):
    """Apply edge routing optimizations based on diagram complexity."""
    
    # Always prevent overlaps
    graphviz_attrs.graph_attr["overlap"] = "false"
    
    # Adjust splines based on complexity
    if num_connections > 15:
        graphviz_attrs.graph_attr["splines"] = "polyline"
        graphviz_attrs.graph_attr["concentrate"] = "true"
        graphviz_attrs.graph_attr["nodesep"] = "1.0"
        graphviz_attrs.graph_attr["ranksep"] = "1.5"
    elif num_connections > 10:
        graphviz_attrs.graph_attr["splines"] = "ortho"
        graphviz_attrs.graph_attr["nodesep"] = "0.8"
        graphviz_attrs.graph_attr["ranksep"] = "1.2"
    else:
        graphviz_attrs.graph_attr["splines"] = "polyline"
        graphviz_attrs.graph_attr["nodesep"] = "0.8"
        graphviz_attrs.graph_attr["ranksep"] = "1.0"
    
    # Set default edge attributes
    if not graphviz_attrs.edge_attr:
        graphviz_attrs.edge_attr = {}
    graphviz_attrs.edge_attr.setdefault("arrowsize", "0.8")
    graphviz_attrs.edge_attr.setdefault("penwidth", "1.0")
    
    # For database connections, suggest port control
    if has_database_connections:
        # This would be applied at connection level
        # See connection-level port control below
        pass
```

### Connection-Level Port Control

To implement port control for database connections, modify `diagrams_engine.py`:

```python
# In _generate_single_connection method
def _generate_single_connection(self, from_var, to_var, conn, lines, indent, is_group=False):
    # ... existing code ...
    
    # Detect database connections and apply port control
    is_db_connection = False
    if conn.graphviz_attrs:
        # Check if connection involves database
        # This could be detected from component types
        pass
    
    if is_db_connection and not conn.graphviz_attrs.get("tailport"):
        # Add port control for database connections
        conn.graphviz_attrs = conn.graphviz_attrs or {}
        conn.graphviz_attrs["tailport"] = "s"  # Connect from bottom
        conn.graphviz_attrs["headport"] = "n"   # Connect to top
```

---

## Testing Recommendations

1. **Test with your multi-region architecture diagram:**
   - Apply `splines="polyline"` + `concentrate="true"`
   - Add `overlap="false"`
   - Increase `nodesep` and `ranksep`
   - Compare before/after

2. **Test edge port control:**
   - Apply `tailport="s"` and `headport="n"` to database connections
   - Verify arrows route from bottom of EC2 to top of RDS

3. **Test with different complexity levels:**
   - Simple (<5 connections)
   - Medium (5-10 connections)
   - Complex (10-15 connections)
   - Very complex (>15 connections)

---

## Quick Reference: Attribute Priority

For complex diagrams, apply attributes in this order:

1. **Essential (Always):**
   - `overlap="false"`
   - `splines="polyline"` or `splines="ortho"`

2. **Highly Recommended (>10 connections):**
   - `concentrate="true"`
   - Increased `nodesep` and `ranksep`

3. **Fine-Tuning (Specific cases):**
   - Edge ports (`tailport`, `headport`)
   - Edge weights (`weight`, `minlen`)
   - Edge grouping (`samehead`, `sametail`)

---

## References

- [Graphviz Splines Attribute](https://graphviz.org/docs/attrs/splines/)
- [Graphviz Concentrate Attribute](https://graphviz.org/docs/attrs/concentrate/)
- [Graphviz Overlap Attribute](https://graphviz.org/docs/attrs/overlap/)
- [Graphviz Edge Attributes](https://graphviz.org/docs/edges/)
- [Graphviz Port Positions](https://graphviz.org/docs/attrs/headport/)
- [Diagrams Package Edges Guide](https://diagrams.mingrammer.com/docs/guides/edge)
- [Graphviz Attributes Reference](https://graphviz.org/doc/info/attrs.html)

---

## Summary

**For your specific problem (messy arrows in complex diagrams):**

1. ✅ **Use `splines="polyline"`** - Cleaner routing than default splines
2. ✅ **Use `concentrate="true"`** - Merges parallel edges
3. ✅ **Use `overlap="false"`** - Prevents node overlaps (critical!)
4. ✅ **Increase spacing** - More room for edges to route
5. ✅ **Use port control** - Direct edges to specific node sides
6. ✅ **Consider `splines="ortho"`** - For very structured diagrams

These solutions are documented in Graphviz and diagrams package documentation and should significantly improve arrow routing in your complex diagrams.

