# Bedrock Resolution Fix

## Problem

The error message indicated that Bedrock class was not found in `diagrams.aws.ml`:
```
Class 'Bedrock' not found in diagrams.aws.ml for aws.bedrock. 
Available classes in diagrams.aws.ml: ApacheMxnetOnAWS, AugmentedAi, Comprehend, ...
```

However, Bedrock **does exist** in the module and should be discoverable.

## Root Cause

The issue occurs in **Step 3 (Registry Fallback)** of the component resolution process:

1. **Step 1 (Library Discovery)** tries to find Bedrock but may fail due to:
   - Caching issues
   - Class filtering logic (only includes classes defined in the module, not imported)
   - Timing/race conditions

2. **Step 2 (Intelligent Resolution)** doesn't help for exact matches like "bedrock"

3. **Step 3 (Registry Fallback)** validates that the class exists in discovered classes:
   - Gets registry mapping: `("ml", "Bedrock")`
   - Calls `discover_module_classes("diagrams.aws.ml")`
   - Checks if "Bedrock" is in the discovered classes
   - **If not found, raises error** - even though Bedrock actually exists!

## Solution

Added a **direct import fallback** in Step 3 before raising the error:

```python
# If class not in discovered classes, try direct import
try:
    module = importlib.import_module(module_path)
    if hasattr(module, class_name):
        node_class = getattr(module, class_name)
        if inspect.isclass(node_class):
            # Found via direct import - use it!
            return node_class
except (ImportError, AttributeError):
    # Fall through to error
    pass
```

This ensures that even if library discovery misses a class (due to caching, filtering, or other issues), we still try to import it directly before giving up.

## Changes Made

1. **Added `inspect` import** to `component_resolver.py`
2. **Added direct import fallback** in Step 3 before raising error
3. **Added logging** to track when direct import succeeds

## Testing

The fix handles these scenarios:
- ✅ Bedrock found via library discovery (normal case)
- ✅ Bedrock found via direct import (fallback case)
- ✅ Proper error if Bedrock truly doesn't exist

## Files Modified

- `backend/src/resolvers/component_resolver.py`
  - Added `import inspect`
  - Added direct import fallback in `resolve_component_class()` method

## Why This Works

The direct import bypasses the discovery cache and filtering logic, going straight to the source. If the class exists in the module (even if imported from elsewhere), `getattr(module, class_name)` will find it.

This is a **defensive programming** approach - we trust the registry configuration and try multiple methods to find the class before giving up.

