# Implementation: Edge Routing & Zoom Features

## Summary

This document describes the implementation of enhanced edge routing optimizations and zoom functionality for diagram generation and viewing.

## Changes Implemented

### 1. Enhanced Edge Routing Optimizations (Backend)

**File:** `backend/src/advisors/aws_architectural_advisor.py`

#### Improvements:

1. **Overlap Prevention (CRITICAL)**
   - Added `overlap="false"` to all diagrams
   - Prevents node overlaps which cause edge routing failures
   - Essential for proper edge routing with splines

2. **Improved Spacing Based on Complexity**
   - **Very Complex (>15 connections):**
     - `splines="polyline"`
     - `concentrate="true"` (merges parallel edges)
     - `nodesep="1.0"` (increased horizontal spacing)
     - `ranksep="1.5"` (increased vertical spacing)
   
   - **Moderately Complex (10-15 connections):**
     - `splines="ortho"` (orthogonal edges)
     - `nodesep="0.9"`
     - `ranksep="1.3"`
   
   - **Simple (5-10 connections):**
     - `splines="polyline"`
     - `nodesep="0.8"`
     - `ranksep="1.2"`

3. **Port Control for Database Connections**
   - Automatically detects database components (RDS, DynamoDB, Aurora, etc.)
   - Applies port control: `tailport="s"` (south/bottom) and `headport="n"` (north/top)
   - Routes database connections from bottom of source to top of database
   - Significantly improves routing clarity for database connections

4. **Consistent Node/Icon Sizing**
   - Sets `fixedsize="shape"` to maintain aspect ratio
   - Sets consistent `width="1.0"` and `height="1.0"` (in inches)
   - Ensures all icons are roughly the same size

### 2. Zoom Functionality (Frontend)

**New Component:** `frontend/src/components/DiagramViewer.tsx`

#### Features:

1. **Zoom Controls**
   - Zoom In (+25% per click, max 500%)
   - Zoom Out (-25% per click, min 25%)
   - Reset Zoom (returns to 100%)
   - Visual zoom level indicator

2. **Pan/Drag Functionality**
   - When zoomed in (>100%), users can drag to pan
   - Cursor changes to "grab" when zoomed in
   - Smooth transitions

3. **Mouse Wheel Zoom**
   - Ctrl+Wheel (or Cmd+Wheel on Mac) to zoom in/out
   - Intuitive for users familiar with image viewers

4. **UI Features**
   - Zoom controls positioned in top-right corner
   - Zoom level indicator in bottom-left when zoomed
   - Responsive design
   - Disabled states for buttons at min/max zoom

#### Integration:

- **Updated:** `frontend/src/components/DiagramGenerator.tsx`
  - Replaced static `<img>` with `<DiagramViewer>` component
  - Only applies to image formats (PNG, SVG, PDF)
  - DOT format still shows text instructions

- **Updated:** `frontend/src/components/AdvancedCodeMode.tsx`
  - Replaced static `<img>` with `<DiagramViewer>` component
  - Consistent zoom experience across both modes

## Technical Details

### Edge Routing Attributes

```python
# Graph-level attributes applied:
graph_attr = {
    "overlap": "false",        # CRITICAL: Prevents node overlaps
    "splines": "polyline",     # Cleaner routing than default splines
    "concentrate": "true",     # Merges parallel edges (if >15 connections)
    "nodesep": "0.8-1.0",      # Horizontal spacing
    "ranksep": "1.0-1.5"       # Vertical spacing
}

# Edge-level attributes:
edge_attr = {
    "arrowsize": "0.8",
    "penwidth": "1.0"
}

# Node-level attributes:
node_attr = {
    "fixedsize": "shape",      # Maintains aspect ratio
    "width": "1.0",            # Consistent size
    "height": "1.0"
}

# Connection-level (database connections):
conn.graphviz_attrs = {
    "tailport": "s",           # Connect from bottom
    "headport": "n"            # Connect to top
}
```

### Zoom Component Props

```typescript
interface DiagramViewerProps {
  diagramUrl: string          // URL of the diagram image
  alt?: string                // Alt text (default: "Generated architecture diagram")
  className?: string           // Additional CSS classes
}
```

## Benefits

### Edge Routing Improvements:

1. **Cleaner Arrows**
   - No overlapping edges
   - Better routing around nodes
   - Parallel edges merged when appropriate

2. **Better Database Connections**
   - Port control routes from bottom to top
   - Reduces visual clutter
   - Easier to trace connections

3. **Consistent Icon Sizes**
   - All icons same size
   - Professional appearance
   - Better visual balance

### Zoom Functionality:

1. **Better UX for Complex Diagrams**
   - Users can zoom in to see details
   - Pan to navigate large diagrams
   - Intuitive controls

2. **Accessibility**
   - Zoom helps users with vision difficulties
   - Keyboard shortcuts (Ctrl+Wheel)
   - Clear visual feedback

## Testing Recommendations

1. **Edge Routing:**
   - Test with multi-region architecture (like your screenshot)
   - Verify database connections route cleanly
   - Check that edges don't overlap
   - Verify icon sizes are consistent

2. **Zoom:**
   - Test zoom in/out buttons
   - Test mouse wheel zoom (Ctrl+Wheel)
   - Test drag/pan when zoomed
   - Test reset zoom
   - Test on different screen sizes

## Future Enhancements

Potential improvements:
- Zoom to fit button
- Zoom to specific region/component
- Keyboard shortcuts (+, -, 0 for zoom)
- Touch gestures for mobile (pinch to zoom)
- Export zoomed view
- Zoom level presets (50%, 100%, 150%, 200%)

## References

- [Edge Routing Solutions Documentation](./EDGE_ROUTING_SOLUTIONS.md)
- [Graphviz Attributes Reference](https://graphviz.org/doc/info/attrs.html)
- [Diagrams Package Edges Guide](https://diagrams.mingrammer.com/docs/guides/edge)
