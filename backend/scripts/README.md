# Installation Scripts

Scripts for installing and managing the AWS Diagram MCP Server locally.

## Available Scripts

### install_mcp_server.sh (Linux/macOS)

Automated installation script for Unix-like systems.

**Usage:**
```bash
chmod +x scripts/install_mcp_server.sh
./scripts/install_mcp_server.sh
```

**What it does:**
- Checks for prerequisites (uv, Python, GraphViz)
- Creates virtual environment `.mcp_server_venv`
- Installs AWS Diagram MCP Server
- Provides configuration instructions

### install_mcp_server.ps1 (Windows)

PowerShell script for Windows installation.

**Usage:**
```powershell
.\scripts\install_mcp_server.ps1
```

**What it does:**
- Checks for prerequisites (uv, Python, GraphViz)
- Creates virtual environment `mcp_server_venv`
- Installs AWS Diagram MCP Server
- Provides configuration instructions

## Manual Installation

If scripts don't work, see [MCP_LOCAL_INSTALLATION.md](../docs/MCP_LOCAL_INSTALLATION.md) for manual steps.

## After Installation

1. Set environment variables:
   ```bash
   export MCP_SERVER_VENV="./backend/.mcp_server_venv"
   export USE_MCP_DIAGRAM_SERVER=true
   ```

2. Or update `backend/config/mcp_config.yaml`:
   ```yaml
   enabled: true
   server_command: "./backend/.mcp_server_venv/bin/python -m awslabs.aws_diagram_mcp_server"
   ```

3. Test installation:
   ```bash
   cd backend
   python examples/mcp_integration_example.py
   ```

## Troubleshooting

See [MCP_LOCAL_INSTALLATION.md](../docs/MCP_LOCAL_INSTALLATION.md) for troubleshooting guide.
