# MCP Diagram Server Integration Guide

## Overview

This document describes the integration of the AWS Diagram MCP Server with the diagram generation system using Approach 4: Direct MCP Tool Integration.

## Architecture

The integration provides direct access to MCP tools within Strands Agents, allowing the agent to:

1. Generate diagrams from Python code (with validation)
2. Validate diagram code before execution
3. Convert ArchitectureSpec to Python code
4. Iteratively refine diagrams based on feedback

## Components

### 1. MCP Client (`src/integrations/mcp_client.py`)

Wrapper for communicating with the AWS Diagram MCP Server via MCP protocol.

**Key Features:**
- Communicates with MCP server via stdio protocol
- Handles timeouts and error recovery
- Provides `generate_diagram()` and `validate_code()` methods

**Usage:**
```python
from src.integrations.mcp_client import get_mcp_client

client = get_mcp_client()
if client:
    result = client.generate_diagram(code="...", title="My Diagram")
```

### 2. MCP Tools (`src/agents/mcp_tools.py`)

Tool functions that can be registered with Strands Agents.

**Available Tools:**

- `generate_diagram_from_code(code, title, diagram_type, outformat)`
  - Generate diagram from Python code
  - Validates code for security and correctness
  - Returns diagram file path

- `validate_diagram_code(code)`
  - Validate Python code before execution
  - Checks for security issues and syntax errors
  - Returns validation results

- `generate_code_from_spec(spec)`
  - Convert ArchitectureSpec to Python code
  - Helper for agent workflow

### 3. Spec Converter (`src/converters/spec_to_mcp.py`)

Converts ArchitectureSpec objects to MCP server input format.

**Usage:**
```python
from src.converters.spec_to_mcp import get_converter

converter = get_converter()
mcp_input = converter.convert_to_mcp_input(spec)
code = converter.convert_to_code(spec)
```

### 4. Updated DiagramAgent (`src/agents/diagram_agent.py`)

Enhanced agent with MCP tool integration.

**Changes:**
- Checks for MCP availability on initialization
- Includes MCP tool instructions in system prompt
- Can register MCP tools with Strands Agent (if supported)

## Configuration

### Environment Variables

```bash
# Enable MCP Diagram Server integration
export USE_MCP_DIAGRAM_SERVER=true

# MCP server command (optional, defaults to uvx)
export MCP_DIAGRAM_SERVER_COMMAND="uvx awslabs.aws-diagram-mcp-server"

# MCP server timeout (optional, default: 30 seconds)
export MCP_SERVER_TIMEOUT=30

# MCP log level (optional, default: ERROR)
export FASTMCP_LOG_LEVEL=ERROR
```

### Configuration File

Edit `backend/config/mcp_config.yaml`:

```yaml
enabled: true
server_command: "uvx awslabs.aws-diagram-mcp-server"
timeout: 30
fallback_on_error: true
```

## Installation

### Prerequisites

1. Install `uv` package manager:
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Install Python 3.10+:
   ```bash
   uv python install 3.10
   ```

3. Install GraphViz:
   - macOS: `brew install graphviz`
   - Linux: `apt-get install graphviz` or `yum install graphviz`
   - Windows: Download from https://www.graphviz.org/

### MCP Server Setup

The MCP server is automatically installed when called via `uvx`. No manual installation needed.

For Windows, you may need to use:
```bash
uv tool run --from awslabs.aws-diagram-mcp-server@latest awslabs.aws-diagram-mcp-server.exe
```

## Usage

### Basic Usage

1. Enable MCP integration:
   ```bash
   export USE_MCP_DIAGRAM_SERVER=true
   ```

2. Run the application:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

3. Generate diagrams normally - MCP tools will be used automatically when enabled.

### Agent Workflow with MCP Tools

When MCP is enabled, the agent can use tools during reasoning:

1. **Parse Description** → Create ArchitectureSpec
2. **Generate Code** → Use `generate_code_from_spec()` to convert spec to code
3. **Validate Code** → Use `validate_diagram_code()` to check code
4. **Generate Diagram** → Use `generate_diagram_from_code()` to create diagram
5. **Return Spec** → Return ArchitectureSpec (diagram already generated)

### Example: Using MCP Tools Programmatically

```python
from src.agents.mcp_tools import generate_diagram_from_code, validate_diagram_code
from src.converters.spec_to_mcp import get_converter

# Convert spec to code
converter = get_converter()
code = converter.convert_to_code(spec)

# Validate code
validation = validate_diagram_code(code)
if not validation["valid"]:
    print(f"Validation errors: {validation['errors']}")

# Generate diagram
result = generate_diagram_from_code(
    code=code,
    title=spec.title,
    diagram_type="aws_architecture"
)
print(f"Diagram generated: {result['output_path']}")
```

## Benefits

### 1. Enhanced Security
- Code scanning prevents security vulnerabilities
- Validates code before execution
- Prevents code injection attacks

### 2. Better Code Quality
- MCP server uses tested code generation patterns
- Handles edge cases automatically
- Produces cleaner, more maintainable code

### 3. Iterative Refinement
- Agent can generate, validate, and refine diagrams
- Multiple diagram variants can be generated
- Better error handling and feedback

### 4. Multi-Diagram Support
- Supports AWS architecture diagrams
- Supports sequence diagrams
- Supports flow charts
- Supports class diagrams

## Troubleshooting

### MCP Server Not Found

**Error:** `MCP server command not found`

**Solution:**
1. Ensure `uv` is installed and in PATH
2. Test MCP server manually:
   ```bash
   uvx awslabs.aws-diagram-mcp-server --help
   ```

### MCP Server Timeout

**Error:** `MCP server timeout`

**Solution:**
1. Increase timeout in config:
   ```yaml
   timeout: 60  # Increase from 30
   ```
2. Check MCP server logs (set `FASTMCP_LOG_LEVEL=DEBUG`)

### MCP Tools Not Available

**Error:** `MCP tools not registered`

**Solution:**
1. Check if MCP is enabled: `USE_MCP_DIAGRAM_SERVER=true`
2. Verify MCP client creation in logs
3. Check Strands SDK version (tool support may vary)

### Fallback Behavior

If MCP fails, the system automatically falls back to the existing `DiagramsEngine`. This ensures backward compatibility and reliability.

## Future Enhancements

1. **Full MCP Protocol Support**
   - Integrate with proper MCP client library (mcp-python)
   - Support full JSON-RPC protocol
   - Better error handling and retries

2. **Tool Registration**
   - Register tools directly with Strands Agent (when SDK supports it)
   - Dynamic tool discovery
   - Tool usage analytics

3. **Advanced Features**
   - Diagram comparison and diff
   - Batch diagram generation
   - Diagram templates and patterns

## References

- [AWS Diagram MCP Server Documentation](https://awslabs.github.io/mcp/servers/aws-diagram-mcp-server)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [Strands Agents Documentation](https://github.com/strands-agents/sdk-python)
