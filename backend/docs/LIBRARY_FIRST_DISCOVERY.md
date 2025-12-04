# Library-First Discovery Implementation

## Overview

This document describes the library-first discovery approach implemented to resolve component types using the actual installed diagrams library as the source of truth, rather than relying solely on registry files.

## Problem Solved

**Previous Issue:**
- Registry file (`aws_nodes.yaml`) mapped `alb → ApplicationLoadBalancer`
- But the installed diagrams library only had `ALB` class
- Import failures occurred: `AttributeError: module has no attribute 'ApplicationLoadBalancer'`

**Solution:**
- Discover available classes from the installed library at runtime
- Use library discovery as primary source of truth
- Registry becomes a fallback/hint mechanism
- Always aligned with what's actually available

## Architecture

### Components

1. **LibraryDiscovery** (`backend/src/resolvers/library_discovery.py`)
   - Introspects diagrams library modules at runtime
   - Discovers available classes
   - Caches results for performance
   - Provides fuzzy matching and normalization

2. **Enhanced ComponentResolver** (`backend/src/resolvers/component_resolver.py`)
   - Library-first resolution strategy
   - Multiple fallback mechanisms
   - Comprehensive error handling
   - Detailed error messages with suggestions

3. **InputValidator** (`backend/src/validators/input_validator.py`)
   - Validates user input before processing
   - Rejects out-of-context inputs early
   - Provides helpful error messages

## Resolution Flow

```
User Input
    ↓
InputValidator (NEW)
    ↓ (if valid)
Library Discovery (PRIMARY)
    ├─ Exact match
    ├─ Normalized match
    ├─ Partial match
    └─ Fuzzy match (≥60%)
    ↓ (if not found)
Registry with Validation (FALLBACK)
    ├─ Check registry mapping
    ├─ Validate class exists in library
    └─ Use if valid
    ↓ (if not found)
Intelligent Resolution (CONTEXT-AWARE)
    ├─ Use component name context
    ├─ Try resolved ID in library
    └─ Use if found
    ↓ (if not found)
Comprehensive Error (LAST RESORT)
    ├─ Registry suggestions
    ├─ Library suggestions
    ├─ Available classes by category
    └─ Helpful error message
```

## Key Features

### 1. Library Discovery

- **Runtime Introspection**: Discovers classes from installed library
- **Caching**: Caches discovered classes for performance
- **Multi-Module Search**: Searches across all provider modules
- **Fuzzy Matching**: Handles typos and variations

### 2. Enhanced Error Handling

- **Pre-import Validation**: Validates classes exist before importing
- **Multiple Suggestion Sources**: Registry + Library suggestions
- **Categorized Display**: Shows available classes by category
- **Context-Aware**: Uses component names for better suggestions

### 3. Input Validation

- **Early Rejection**: Rejects out-of-context inputs before processing
- **Keyword Detection**: Identifies non-cloud architecture requests
- **Helpful Messages**: Provides examples and guidance

## Usage Examples

### Example 1: ALB Resolution

```python
# User input: "Create an ALB"
component = Component(id="alb1", name="Load Balancer", type="alb")

# Resolution:
# 1. Library discovery finds "ALB" in diagrams.aws.network
# 2. Returns: diagrams.aws.network.ALB
# ✅ Success!
```

### Example 2: Invalid Input

```python
# User input: "I want to bake a cake"

# InputValidator rejects early:
# ❌ Error: "I can only help you create cloud architecture diagrams..."
```

### Example 3: Typo Handling

```python
# User input: "appliation_load_balancer" (typo)
# Library discovery fuzzy match finds "ALB" (85% similarity)
# ✅ Success with warning!
```

## Benefits

1. **Always Aligned**: Uses actual installed library, not registry
2. **Resilient**: Multiple fallback strategies
3. **User-Friendly**: Better error messages with suggestions
4. **Performance**: Caching and optimized search
5. **Maintainable**: Adapts to library changes automatically

## Files Modified/Created

### New Files
- `backend/src/resolvers/library_discovery.py` - Library discovery service
- `backend/src/validators/input_validator.py` - Input validation
- `backend/src/validators/__init__.py` - Validators package init

### Modified Files
- `backend/src/resolvers/component_resolver.py` - Enhanced with library-first approach
- `backend/src/agents/diagram_agent.py` - Integrated input validation

## Testing

To test the implementation:

```python
from src.resolvers.component_resolver import ComponentResolver
from src.models.spec import Component

resolver = ComponentResolver("aws")

# Test valid component
component = Component(id="alb1", name="ALB", type="alb")
class_obj = resolver.resolve_component_class(component)
print(f"Resolved: {class_obj.__name__}")  # Should print: ALB

# Test invalid component
try:
    invalid = Component(id="xyz", name="XYZ", type="xyz_service")
    resolver.resolve_component_class(invalid)
except ValueError as e:
    print(f"Error: {e}")  # Should show helpful suggestions
```

## Migration Notes

- **Backward Compatible**: Registry still works as fallback
- **No Breaking Changes**: Existing code continues to work
- **Gradual Adoption**: Can validate registry against library

## Future Improvements

1. Auto-generate registry from library discovery
2. Registry validation script
3. Performance metrics and monitoring
4. Support for custom diagram libraries

