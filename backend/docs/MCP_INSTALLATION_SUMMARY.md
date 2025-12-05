# MCP Server Local Installation - Quick Summary

## Quick Install

### Linux/macOS
```bash
cd backend
chmod +x scripts/install_mcp_server.sh
./scripts/install_mcp_server.sh
```

### Windows PowerShell
```powershell
cd backend
.\scripts\install_mcp_server.ps1
```

## After Installation

Set environment variable:
```bash
export MCP_SERVER_VENV="./backend/.mcp_server_venv"
export USE_MCP_DIAGRAM_SERVER=true
```

The MCP client will automatically detect and use the local installation!

## Benefits

- ✅ **Faster startup** - No download overhead
- ✅ **Offline support** - Works without internet
- ✅ **Consistent performance** - No caching delays
- ✅ **Auto-detected** - No manual configuration needed

## Verification

```bash
# Test installation
cd backend
python examples/mcp_integration_example.py

# Check logs for:
# "Found local MCP server venv: ..."
```

## Full Documentation

See [MCP_LOCAL_INSTALLATION.md](./MCP_LOCAL_INSTALLATION.md) for detailed instructions.
