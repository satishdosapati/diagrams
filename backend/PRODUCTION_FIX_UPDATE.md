# Production Fix - Enhanced Logging

## Issue
Production logs show Bedrock error persists even after deployment. The direct import attempts aren't visible because they're logged at DEBUG level.

## Changes Made

### Enhanced Logging (INFO level for production visibility)

1. **Direct Import Attempts** - Changed from DEBUG to INFO
   - `[RESOLVER] Attempting direct import: diagrams.aws.ml.Bedrock`
   - `[RESOLVER] ✅ Found 'Bedrock' via direct import` (on success)
   - `[RESOLVER] Available classes in module (first 15): [...]` (on failure)

2. **Second Attempt** - Enhanced logging
   - `[RESOLVER] Attempting second direct import for 'Bedrock'`
   - Lists all available classes if Bedrock not found
   - Shows error details if import fails

3. **Error Messages** - More visible
   - Uses ✅/❌ emojis for quick scanning
   - Shows all available classes when Bedrock not found
   - Lists Bedrock variants if found with different casing

## What to Look For in Production Logs

After deploying, you should see:

### Success Case:
```
INFO - [RESOLVER] Attempting direct import: diagrams.aws.ml.Bedrock
INFO - [RESOLVER] ✅ Found 'Bedrock' via direct import from registry hint
```

### Failure Case (for debugging):
```
INFO - [RESOLVER] Attempting direct import: diagrams.aws.ml.Bedrock
WARNING - [RESOLVER] Class 'Bedrock' not found in module 'diagrams.aws.ml' via hasattr check
INFO - [RESOLVER] Available classes in module (first 15): [...]
INFO - [RESOLVER] Attempting second direct import for 'Bedrock'
INFO - [RESOLVER] All classes in module: [...]
```

## Next Steps

1. **Deploy updated code** to production
2. **Check logs** for the new INFO-level messages
3. **If Bedrock still fails**, the logs will show:
   - Whether direct import is being attempted
   - What classes are actually available
   - Why the import is failing

## Root Cause Analysis

The production logs will now reveal:
- ✅ Is direct import being attempted? (INFO log)
- ✅ Does Bedrock exist in the module? (hasattr check)
- ✅ What classes are actually available? (full list)
- ✅ Why is it failing? (exception details)

This will help us understand if:
- Bedrock doesn't exist in production diagrams library version
- There's a module import issue
- There's a class name mismatch
- There's an exception being silently caught

