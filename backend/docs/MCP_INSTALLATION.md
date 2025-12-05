# Installing AWS Diagram MCP Server Locally

This guide explains how to install the AWS Diagram MCP Server locally for improved performance and reliability.

## Why Install Locally?

- **Faster Response Times**: No download delay on first use
- **Better Reliability**: No dependency on network for server startup
- **Production Ready**: More suitable for production deployments
- **Offline Support**: Works without internet connection after installation

## Prerequisites

1. **Python 3.10+** installed (Python 3.11 recommended and already in your venv)
2. **GraphViz** installed (required for diagram generation)
3. **uv** package manager (recommended) or **pip**

## Installation Methods

### Method 1: Using uv (Recommended)

#### Linux/macOS

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run installation script
cd backend
chmod +x scripts/install_mcp_server.sh
./scripts/install_mcp_server.sh
```

#### Windows

```powershell
# Install uv if not already installed
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Run installation script
cd backend
powershell -ExecutionPolicy Bypass -File scripts/install_mcp_server.ps1
```

#### Manual Installation with uv

```bash
# Install Python 3.10+ if needed
uv python install 3.10

# Install MCP server
uv tool install awslabs.aws-diagram-mcp-server

# Verify installation
uv tool run awslabs.aws-diagram-mcp-server --help
```

### Method 2: Using pip (Alternative)

If `uv` is not available, you can try installing via pip:

```bash
# Install from GitHub (if package is available)
pip install git+https://github.com/awslabs/aws-diagram-mcp-server.git

# Or install from PyPI (if published)
pip install awslabs-aws-diagram-mcp-server
```

**Note**: The MCP server may not be available via pip. Using `uv` is recommended.

## Configuration After Installation

### Option 1: Use uv tool run (Recommended)

Update your environment or config:

**Linux/macOS:**
```bash
export MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"
```

**Windows:**
```powershell
$env:MCP_DIAGRAM_SERVER_COMMAND="uv tool run --from awslabs.aws-diagram-mcp-server@latest awslabs.aws-diagram-mcp-server.exe"
```

### Option 2: Use Direct Path

Find the installed location and use direct path:

**Linux/macOS:**
```bash
# Find installation path
uv tool list

# Use direct path (example)
export MCP_DIAGRAM_SERVER_COMMAND="/home/user/.local/bin/awslabs.aws-diagram-mcp-server"
```

**Windows:**
```powershell
# Find installation path
uv tool list

# Use direct path (example)
$env:MCP_DIAGRAM_SERVER_COMMAND="C:\Users\YourUser\.local\bin\awslabs.aws-diagram-mcp-server.exe"
```

### Option 3: Update Config File

Edit `backend/config/mcp_config.yaml`:

```yaml
enabled: true
server_command: "uv tool run awslabs.aws-diagram-mcp-server"  # or direct path
timeout: 30
```

## Verify Installation

### Test MCP Server

```bash
# Test with uv
uv tool run awslabs.aws-diagram-mcp-server --help

# Or test direct command
$MCP_DIAGRAM_SERVER_COMMAND --help
```

### Test Integration

```bash
# Enable MCP
export USE_MCP_DIAGRAM_SERVER=true

# Run example
cd backend
python examples/mcp_integration_example.py
```

### Check Logs

When running the application, look for:
```
[MCP] MCP Diagram Client initialized with command: ...
[MCP] MCP Diagram Client created successfully
```

## Installation Locations

### uv Installation

- **Linux/macOS**: `~/.local/bin/` or `~/.cargo/bin/`
- **Windows**: `%USERPROFILE%\.local\bin\` or `%USERPROFILE%\.cargo\bin\`

### pip Installation

- **Linux/macOS**: `~/.local/bin/` or virtual environment `bin/`
- **Windows**: `%USERPROFILE%\AppData\Local\Programs\Python\Scripts\` or virtual environment `Scripts\`

## Troubleshooting

### MCP Server Not Found

**Problem**: `Command not found` error

**Solutions**:
1. Add installation directory to PATH:
   ```bash
   # Linux/macOS
   export PATH="$HOME/.local/bin:$PATH"
   
   # Windows
   $env:Path += ";$env:USERPROFILE\.local\bin"
   ```

2. Use full path in configuration

3. Verify installation:
   ```bash
   uv tool list
   # or
   pip show awslabs-aws-diagram-mcp-server
   ```

### GraphViz Not Found

**Problem**: Diagram generation fails

**Solutions**:

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install graphviz

# CentOS/RHEL/Amazon Linux
sudo yum install graphviz
# or
sudo dnf install graphviz
```

**macOS:**
```bash
brew install graphviz
```

**Windows:**
- Download from: https://www.graphviz.org/download/
- Or use Chocolatey: `choco install graphviz`

### Permission Errors

**Problem**: Permission denied when running MCP server

**Solutions**:
1. Make script executable:
   ```bash
   chmod +x scripts/install_mcp_server.sh
   ```

2. Use user installation (not system-wide):
   ```bash
   uv tool install --user awslabs.aws-diagram-mcp-server
   ```

### Python Version Issues

**Problem**: Python version incompatible

**Solutions**:
1. Install Python 3.10+:
   ```bash
   uv python install 3.10
   ```

2. Use specific Python version:
   ```bash
   uv tool install --python 3.10 awslabs.aws-diagram-mcp-server
   ```

## Updating MCP Server

### Using uv

```bash
# Update to latest version
uv tool install --force awslabs.aws-diagram-mcp-server

# Or install specific version
uv tool install awslabs.aws-diagram-mcp-server@latest
```

### Using pip

```bash
pip install --upgrade git+https://github.com/awslabs/aws-diagram-mcp-server.git
```

## Production Deployment

For production environments:

1. **Install during deployment**:
   ```bash
   # Add to deployment script
   ./scripts/install_mcp_server.sh
   ```

2. **Use absolute paths** in configuration:
   ```yaml
   server_command: "/opt/diagram-generator/.local/bin/awslabs.aws-diagram-mcp-server"
   ```

3. **Set up systemd service** (if running as service):
   ```ini
   [Service]
   Environment="PATH=/opt/diagram-generator/.local/bin:/usr/bin:/bin"
   ```

4. **Verify in CI/CD**:
   ```bash
   # Add to CI/CD pipeline
   uv tool run awslabs.aws-diagram-mcp-server --help
   ```

## Performance Comparison

### Before (uvx - on-demand download)
- First call: ~5-10 seconds (download + startup)
- Subsequent calls: ~1-2 seconds (startup only)

### After (local installation)
- First call: ~0.5-1 second (startup only)
- Subsequent calls: ~0.5-1 second (startup only)

**Improvement**: ~5-10x faster on first call, ~2x faster on subsequent calls

## Next Steps

1. ✅ Install MCP server locally
2. ✅ Configure environment variables
3. ✅ Test installation
4. ✅ Enable MCP integration (`USE_MCP_DIAGRAM_SERVER=true`)
5. ✅ Monitor performance improvements

## References

- [AWS Diagram MCP Server](https://awslabs.github.io/mcp/servers/aws-diagram-mcp-server)
- [uv Documentation](https://github.com/astral-sh/uv)
- [GraphViz Installation](https://www.graphviz.org/download/)
