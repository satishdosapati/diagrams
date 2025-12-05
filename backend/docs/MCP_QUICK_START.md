# MCP Diagram Server - Quick Start Guide

## Enable MCP Integration

### Step 1: Install MCP Server Locally (Recommended)

For improved performance, install the MCP server locally:

**Linux/macOS:**
```bash
cd backend
chmod +x scripts/install_mcp_server.sh
./scripts/install_mcp_server.sh
```

**Windows:**
```powershell
cd backend
powershell -ExecutionPolicy Bypass -File scripts/install_mcp_server.ps1
```

**Manual Installation:**
```bash
# Install using uv (recommended)
uv tool install awslabs.aws-diagram-mcp-server

# Verify installation
uv tool run awslabs.aws-diagram-mcp-server --help
```

### Step 2: Set Environment Variable

```bash
export USE_MCP_DIAGRAM_SERVER=true
```

### Step 3: Verify Prerequisites

Ensure you have:
- `uv` package manager installed
- Python 3.11+ available (or 3.10/3.12)
- GraphViz installed

Test MCP server:
```bash
# If installed locally
uv tool run awslabs.aws-diagram-mcp-server --help

# Or using uvx (on-demand)
uvx awslabs.aws-diagram-mcp-server --help
```

### Step 4: Run Application

```bash
cd backend
uvicorn main:app --reload
```

## Usage

Once enabled, MCP tools are automatically available to the Strands Agent. The agent can:

1. **Generate diagrams** with enhanced security validation
2. **Validate code** before execution
3. **Convert specs** to Python code

## Example: Test MCP Integration

Run the example script:

```bash
cd backend
python examples/mcp_integration_example.py
```

## Configuration

Edit `backend/config/mcp_config.yaml`:

```yaml
enabled: true
server_command: "uvx awslabs.aws-diagram-mcp-server"
timeout: 30
```

## Troubleshooting

### MCP Not Enabled

**Check:** `USE_MCP_DIAGRAM_SERVER` environment variable

**Solution:**
```bash
export USE_MCP_DIAGRAM_SERVER=true
```

### MCP Server Not Found

**Check:** `uv` is installed and in PATH

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Test MCP server
uvx awslabs.aws-diagram-mcp-server --help
```

### Fallback Behavior

If MCP fails, the system automatically uses the existing `DiagramsEngine`. No action needed.

## Next Steps

- Read [MCP_DIAGRAM_INTEGRATION.md](./MCP_DIAGRAM_INTEGRATION.md) for detailed documentation
- Check logs for MCP activity: `[MCP]` prefix in logs
- Test with example script: `python examples/mcp_integration_example.py`
