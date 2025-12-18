# Bedrock Version Issue - Root Cause Found!

## Problem Identified

Production logs reveal the **actual root cause**:

```
[RESOLVER] All classes in module: ['ApacheMxnetOnAWS', 'AugmentedAi', 'Comprehend', ...]
```

**Bedrock is NOT in the list!** This means the production diagrams library version doesn't include Bedrock.

## Root Cause

**Production has `diagrams==0.23.4` pinned**, but Bedrock was added in a later version (likely 0.24.0+).

- **Local version**: 0.24.4 ✅ (has Bedrock)
- **Production version**: 0.23.4 ❌ (no Bedrock)

## Solution

### 1. Update requirements.txt

Changed from:
```
diagrams==0.23.4
```

To:
```
diagrams>=0.24.0
```

This allows the diagrams library to be upgraded to a version that includes Bedrock.

### 2. Enhanced Error Message

Added helpful error message suggesting library upgrade:
```
⚠️  This class exists in the registry but not in the installed diagrams library. 
This usually means the diagrams library version is outdated. 
Try upgrading: pip install --upgrade diagrams
```

## Deployment Steps

### 1. Update Requirements
```bash
cd /opt/diagram-generator/backend
source venv/bin/activate
pip install --upgrade diagrams
# Or update requirements.txt and run:
pip install -r requirements.txt --upgrade
deactivate
```

### 2. Verify Bedrock Exists
```bash
python3 -c "import diagrams.aws.ml; print('Bedrock:', hasattr(diagrams.aws.ml, 'Bedrock'))"
```

### 3. Restart Service
```bash
sudo systemctl restart diagram-api
```

### 4. Test
```bash
# Check logs
sudo journalctl -u diagram-api.service -f

# Should now see:
# INFO - [RESOLVER] Found 'Bedrock' in library for 'bedrock'
```

## Why This Happened

1. **Version pinning**: `diagrams==0.23.4` locked production to an older version
2. **Bedrock added later**: Bedrock was added in diagrams library version 0.24.0+
3. **Registry vs Library mismatch**: Registry has Bedrock, but library doesn't

## Prevention

- Use `>=` instead of `==` for libraries that add new classes frequently
- Or regularly update pinned versions when new AWS services are added
- Check diagrams library changelog for new classes

## Alternative: Graceful Degradation

If upgrading isn't possible, we could:
1. Remove Bedrock from registry (not ideal)
2. Add fallback to similar ML service (e.g., SageMaker)
3. Show warning but continue with alternative

But **upgrading is the best solution** since Bedrock is a real AWS service that should be supported.

