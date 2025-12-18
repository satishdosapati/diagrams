# Bug Fixes

Concise documentation of bug fixes and resolutions.

## 2024-12-18: Bedrock Resolution & Filename Sanitization

### Issue 1: Bedrock Class Not Found
**Problem**: `Class 'Bedrock' not found in diagrams.aws.ml`  
**Root Cause**: Production had `diagrams==0.23.4` pinned, but Bedrock was added in 0.24.0+  
**Fix**:
- Updated `requirements.txt`: `diagrams==0.23.4` → `diagrams>=0.24.0`
- Made library discovery more inclusive (include all classes, not just those with matching `__module__`)
- Added robust direct import fallback with retry logic
- Enhanced error messages with upgrade suggestions

**Files Changed**:
- `backend/requirements.txt`
- `backend/src/resolvers/library_discovery.py`
- `backend/src/resolvers/component_resolver.py`

**Status**: ✅ Fixed - Bedrock resolves successfully after diagrams library upgrade

---

### Issue 2: Filename 400 Error (Zero-Width Space)
**Problem**: `GET /api/diagrams/...` returns 400 Bad Request  
**Root Cause**: Filename contains zero-width space (`\u200d`) from spec title, rejected by validation regex  
**Fix**:
- Added `_sanitize_filename()` method to remove zero-width spaces and invisible Unicode characters
- Sanitize filenames during generation and when serving
- Clean filename before validation in GET endpoint

**Files Changed**:
- `backend/src/generators/diagrams_engine.py`
- `backend/src/api/routes.py`

**Status**: ✅ Fixed - Filenames are sanitized, zero-width spaces removed

---

## Discovery System Improvements

### Library-First Discovery
- **Change**: Made discovery more inclusive - includes ALL classes in modules
- **Benefit**: Automatically discovers new classes without YAML updates
- **Impact**: Works for all components, not just Bedrock

### Direct Import Fallback
- **Change**: Added robust direct import fallback before raising errors
- **Benefit**: Handles edge cases where discovery cache misses classes
- **Impact**: More reliable resolution for all components

