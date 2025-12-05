# AWS Diagram MCP Server - Verified Tools

## Configuration

The AWS Diagram MCP Server is configured in Cursor's MCP settings (`~/.cursor/mcp.json`):

```json
{
  "aws-diagram-mcp-server": {
    "command": "uvx",
    "args": ["awslabs.aws-diagram-mcp-server"],
    "env": {
      "FASTMCP_LOG_LEVEL": "ERROR"
    },
    "autoApprove": [],
    "disabled": false
  }
}
```

## Available Tools (Verified)

### 1. ✅ `generate_diagram`

**Purpose**: Generate PNG diagrams from Python code using the diagrams package DSL.

**Parameters**:
- `code` (required, string): Python code using diagrams package DSL
- `filename` (optional, string): Name of the output PNG file
- `timeout` (optional, integer): Maximum time in seconds (default: 90)
- `workspace_dir` (optional, string): Directory where diagrams will be saved

**Returns**: Path to generated PNG file

**Status**: ✅ Fully implemented in our code

---

### 2. ✅ `list_icons`

**Purpose**: List available icons from the diagrams package.

**Parameters**:
- `provider_filter` (optional, string): Filter by provider (e.g., "aws", "azure", "gcp")
- `service_filter` (optional, string): Filter by service name

**Returns**: Dictionary with providers and their services/icons

**Example Response**:
```json
{
  "providers": {
    "aws": {},
    "azure": {},
    "gcp": {},
    "k8s": {},
    "onprem": {},
    ...
  },
  "filtered": false,
  "filter_info": null
}
```

**Status**: ⏳ Available but not yet used in our code

**Potential Use Cases**:
- Validate icon names before code generation
- Discover available icons for a provider
- Auto-suggest icons based on service names

---

### 3. ✅ `get_diagram_examples`

**Purpose**: Get ready-to-use code examples for various diagram types.

**Parameters**:
- `diagram_type` (optional, string): Type of diagram example
  - `aws` - AWS architecture examples
  - `sequence` - Sequence diagrams
  - `flow` - Flow charts
  - `class` - Class diagrams
  - `k8s` - Kubernetes diagrams
  - `onprem` - On-premises diagrams
  - `custom` - Custom diagrams

**Returns**: Dictionary with example code snippets

**Example Response** (for `diagram_type="aws"`):
```json
{
  "examples": {
    "aws_basic": "with Diagram(\"Web Service Architecture\", show=False):\n    ELB(\"lb\") >> EC2(\"web\") >> RDS(\"userdb\")\n",
    "aws_grouped_workers": "...",
    "aws_clustered_web_services": "...",
    "aws_event_processing": "...",
    "aws_bedrock": "..."
  }
}
```

**Status**: ⏳ Available but not yet used in our code

**Potential Use Cases**:
- Learning diagram syntax
- Template generation
- Best practices examples

---

## Tools NOT Available

### ❌ `validate_code`

**Status**: Does NOT exist in AWS Diagram MCP Server.

**Why**: Code validation happens automatically during `generate_diagram` execution. Invalid code causes `generate_diagram` to return an error.

**Our Implementation**: We correctly use `generate_diagram` with a temporary filename to validate code.

---

## Current Implementation Status

### ✅ Fully Implemented

1. **`generate_diagram`**: 
   - ✅ Correct API parameters (`code`, `filename`, `timeout`, `workspace_dir`)
   - ✅ Integrated into `MCPDiagramClient`
   - ✅ Used for both validation and generation
   - ✅ Proper error handling

### ⏳ Available But Not Used

1. **`list_icons`**: 
   - ✅ Tool exists and works
   - ⏳ Not yet integrated into our codebase
   - 💡 Could be useful for icon validation/discovery

2. **`get_diagram_examples`**: 
   - ✅ Tool exists and works
   - ⏳ Not yet integrated into our codebase
   - 💡 Could be useful for templates/examples

---

## What We Need

Based on the verified tools, here's what we need:

### ✅ Already Have

1. **`generate_diagram`** - Fully implemented and working
   - Used for code validation (temporary file)
   - Used for diagram generation (real file)

### 💡 Could Add (Optional Enhancements)

1. **`list_icons`** - For icon discovery/validation
   - Could validate icon names before code generation
   - Could help with auto-completion/suggestions
   - Could verify provider-specific icons exist

2. **`get_diagram_examples`** - For templates/examples
   - Could provide example templates to users
   - Could help with learning diagram syntax
   - Could be used for quick starts

---

## Summary

**Available Tools**: 3
- ✅ `generate_diagram` (implemented)
- ✅ `list_icons` (available, not used)
- ✅ `get_diagram_examples` (available, not used)

**Not Available**: 
- ❌ `validate_code` (validation happens in `generate_diagram`)

**Current Status**: 
- ✅ Core functionality (`generate_diagram`) is fully implemented
- ⏳ Optional tools (`list_icons`, `get_diagram_examples`) are available but not integrated

**Recommendation**: 
- Current implementation is correct and complete for core use case
- Optional tools can be added later if needed for enhanced features
