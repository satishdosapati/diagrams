# Migration Guide: Separate Config Files

## Overview

The node registry configuration has been refactored from a single `node_registry.yaml` file into separate provider-specific files for better organization and maintainability.

## New Structure

### Provider-Specific Files

- **`aws_nodes.yaml`** - All AWS node definitions
- **`azure_nodes.yaml`** - All Azure node definitions
- **`gcp_nodes.yaml`** - All GCP node definitions

### File Format

Each provider file has this structure:

```yaml
# Provider module mappings
modules:
  compute: diagrams.aws.compute
  storage: diagrams.aws.storage
  # ... more categories

# Node mappings
nodes:
  ec2:
    category: compute
    class_name: EC2
    description: "EC2 Instance"
  # ... more nodes
```

## Current Status

The system now uses separate provider-specific files exclusively:

1. **Required Files**: All three provider files must exist (`aws_nodes.yaml`, `azure_nodes.yaml`, `gcp_nodes.yaml`)
2. **No Legacy Support**: The old `node_registry.yaml` format is no longer supported
3. **Clean Structure**: Each provider is managed independently

## Migration Steps

If you have a custom `node_registry.yaml`:

1. **Split the file** into three provider-specific files
2. **Extract each provider section** into its own file
3. **Remove the `providers:` wrapper** - each file contains modules and nodes directly
4. **Keep the old file** for reference (optional, can be deleted)

## Benefits

1. ✅ **Better Organization** - Each provider in its own file
2. ✅ **Easier Maintenance** - Edit one provider without affecting others
3. ✅ **Reduced Git Conflicts** - Less chance of merge conflicts
4. ✅ **Clearer Structure** - Easier to navigate and understand
5. ✅ **Selective Updates** - Update AWS nodes without touching Azure/GCP

## Example Migration

** (`node_registry.yaml` format)
```yaml
providers:
  aws:
    modules: {...}
    nodes: {...}
  azure:
    modules: {...}
    nodes: {...}
```

### New Format (`aws_nodes.yaml`)
```yaml
modules: {...}
nodes: {...}
```

## Testing

After migration, verify the registry loads correctly:

```python
from src.models.node_registry import get_registry

registry = get_registry()
print(f"Loaded providers: {list(registry._registry['providers'].keys())}")
# Should output: ['aws', 'azure', 'gcp']
```

## Questions?

See `README.md` for detailed documentation on adding nodes and troubleshooting.

