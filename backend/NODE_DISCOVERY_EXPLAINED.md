# How Node Discovery Works - Visual Explanation

## Overview

The system discovers nodes through a **hybrid approach** that combines:
1. **Static configuration** (YAML registry)
2. **Runtime introspection** (library discovery)
3. **Intelligent matching** (fuzzy resolution)

## Discovery Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER REQUEST                                 │
│              Component(type="bedrock")                          │
└────────────────────┬──────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              ComponentResolver.resolve_component_class()         │
└────────────────────┬──────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  Extract node_id: "bedrock" │
        └────────────┬────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌──────────────────┐      ┌──────────────────────┐
│ STEP 1:          │      │ Get Category Hint    │
│ Library Discovery│◄─────│ from Registry        │
│ (PRIMARY)        │      │ category: "ml"       │
└────────┬──────────┘      └──────────────────────┘
         │
         │ LibraryDiscovery.find_class("bedrock", "ml")
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Check cached classes in diagrams.aws.ml                 │
│ 2. Normalize input: "bedrock" → "bedrock"                  │
│ 3. Search for match:                                        │
│    - Exact match: "Bedrock" ✅                              │
│    - Normalized match                                       │
│    - Partial match                                          │
│    - Fuzzy match                                            │
└────────────┬────────────────────────────────────────────────┘
             │
             │ Found: ("diagrams.aws.ml", "Bedrock")
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ Import and Return:                                         │
│   import diagrams.aws.ml                                    │
│   return Bedrock class ✅                                   │
└─────────────────────────────────────────────────────────────┘

If Step 1 fails:
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Intelligent Resolution (Fuzzy Matching)            │
│   - Normalize: "bedrock" → "bedrock"                       │
│   - Fuzzy match against registry                            │
│   - Keyword matching                                        │
│   - Context-aware matching                                  │
└────────────┬────────────────────────────────────────────────┘
             │
             │ Resolved to: "bedrock"
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Registry Fallback                                  │
│   - Get mapping: ("ml", "Bedrock")                         │
│   - Validate class exists in library                       │
│   - Import and return ✅                                     │
└─────────────────────────────────────────────────────────────┘

If all steps fail:
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Comprehensive Error                                │
│   - Show suggestions                                        │
│   - List available classes                                  │
│   - Provide helpful error message                           │
└─────────────────────────────────────────────────────────────┘
```

## Component Discovery Layers

### Layer 1: Static Registry (YAML)
```
backend/config/aws_nodes.yaml
├── modules:
│   └── ml: diagrams.aws.ml
└── nodes:
    └── bedrock:
        ├── category: ml
        ├── class_name: Bedrock
        └── description: "Amazon Bedrock"
```

**Purpose**: 
- Provides hints for category lookup
- Fallback when library discovery fails
- Documentation of available nodes

### Layer 2: Runtime Library Discovery
```
LibraryDiscovery.__init__()
├── For each category (compute, storage, ml, ...):
│   ├── Import module: diagrams.aws.ml
│   ├── Inspect classes using Python introspection
│   └── Cache: {"diagrams.aws.ml": {"Bedrock", "SageMaker", ...}}
│
└── find_class("bedrock", "ml")
    ├── Normalize: "bedrock" → "bedrock"
    ├── Search cached classes
    └── Return: ("diagrams.aws.ml", "Bedrock")
```

**Purpose**:
- **Source of truth** - uses actual installed library
- Discovers new classes automatically
- Validates registry entries

### Layer 3: Intelligent Resolution
```
IntelligentNodeResolver
├── Build keyword index from registry
│   └── "bedrock" → ["bedrock", "amazon", "ml", "ai", ...]
│
└── resolve("bedrock")
    ├── Exact match
    ├── Normalized match
    ├── Fuzzy match (similarity scoring)
    └── Keyword match
```

**Purpose**:
- Handles typos and variations
- Context-aware matching
- Provides suggestions

## Bedrock-Specific Flow

For `bedrock` node:

1. **Input**: `Component(type="bedrock", provider="aws")`

2. **Extract node_id**: `"bedrock"`

3. **Get category hint**: Registry lookup → `category: "ml"`

4. **Library Discovery**:
   ```
   discovery.find_class("bedrock", category_hint="ml")
   ├── Search in: diagrams.aws.ml (cached)
   ├── Normalize: "bedrock"
   ├── Match: "Bedrock" (exact match, case-insensitive)
   └── Return: ("diagrams.aws.ml", "Bedrock") ✅
   ```

5. **Import**:
   ```python
   import diagrams.aws.ml
   return diagrams.aws.ml.Bedrock
   ```

6. **Result**: Bedrock class ready to use ✅

## Why This Works

### ✅ Library-First Approach
- Uses actual installed library as source of truth
- Automatically discovers new classes
- Validates registry entries

### ✅ Registry as Fallback
- Provides hints for faster lookup
- Fallback if library discovery fails
- Documentation of available nodes

### ✅ Intelligent Matching
- Handles user typos
- Context-aware resolution
- Provides helpful suggestions

## Common Issues and Solutions

### Issue: "Class 'Bedrock' not found"
**Cause**: Class name mismatch between registry and library
**Solution**: Check actual class name in library:
```python
import diagrams.aws.ml
print([c for c in dir(diagrams.aws.ml) if 'bedrock' in c.lower()])
```

### Issue: "Module 'diagrams.aws.ml' not available"
**Cause**: Diagrams library version doesn't include ml module
**Solution**: Update diagrams library:
```bash
pip install --upgrade diagrams
```

### Issue: Resolution succeeds but diagram fails
**Cause**: Graphviz not installed or PATH issue
**Solution**: Install Graphviz and ensure it's in PATH

## Debugging Tips

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check What's Discovered
```python
from backend.src.resolvers.library_discovery import LibraryDiscovery

discovery = LibraryDiscovery("aws")
ml_classes = discovery.get_classes_for_category("ml")
print("ML classes:", sorted(ml_classes))
```

### Test Resolution Directly
```python
from backend.src.resolvers.component_resolver import ComponentResolver
from backend.src.models.spec import Component

resolver = ComponentResolver(primary_provider="aws")
component = Component(id="test", name="Bedrock", type="bedrock", provider="aws")
bedrock_class = resolver.resolve_component_class(component)
print(f"Resolved: {bedrock_class.__name__} from {bedrock_class.__module__}")
```

