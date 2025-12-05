# Install AWS Diagram MCP Server Locally

## Quick Install

### Option 1: Automated Script (Recommended)

**Linux/macOS:**
```bash
cd backend
chmod +x scripts/install_mcp_server.sh
./scripts/install_mcp_server.sh
```

**Windows PowerShell:**
```powershell
cd backend
.\scripts\install_mcp_server.ps1
```

### Option 2: Manual Installation

```bash
# Create virtual environment (using Python 3.11)
uv venv .mcp_server_venv --python 3.11

# Activate (Linux/macOS)
source .mcp_server_venv/bin/activate

# Activate (Windows)
.\mcp_server_venv\Scripts\Activate.ps1

# Install MCP server
pip install --upgrade pip
pip install awslabs.aws-diagram-mcp-server

# Verify
python -c "import awslabs.aws_diagram_mcp_server; print('OK')"
```

## Enable Local Installation

The MCP client **automatically detects** local installations! Just set:

```bash
export USE_MCP_DIAGRAM_SERVER=true
```

The client will check in this order:
1. `MCP_SERVER_VENV` environment variable
2. `.mcp_server_venv` or `mcp_server_venv` in project root
3. Current Python environment
4. uv tool installation
5. Fallback to `uvx` (on-demand)

## Verify Installation

```bash
# Set environment variable
export USE_MCP_DIAGRAM_SERVER=true

# Run example
cd backend
python examples/mcp_integration_example.py

# Check logs for:
# "Found local MCP server venv: ..."
```

## Benefits

- ✅ **Faster** - No download overhead (~0.5s vs ~2-5s)
- ✅ **Offline** - Works without internet
- ✅ **Consistent** - No caching delays
- ✅ **Auto-detected** - No manual configuration needed

## Troubleshooting

See [docs/MCP_LOCAL_INSTALLATION.md](./docs/MCP_LOCAL_INSTALLATION.md) for detailed troubleshooting.

## Next Steps

1. Install MCP server using script above
2. Set `USE_MCP_DIAGRAM_SERVER=true`
3. Test with example script
4. Check logs to verify local installation is being used
