# Local Installation of AWS Diagram MCP Server

## Overview

Installing the AWS Diagram MCP Server locally improves performance by avoiding the download overhead of `uvx` on each run. This guide covers local installation options.

## Prerequisites

1. **uv package manager** - Install from https://astral.sh/uv
2. **Python 3.10+** - Will be installed automatically via uv if needed
3. **GraphViz** - Required for diagram generation
   - macOS: `brew install graphviz`
   - Linux: `apt-get install graphviz` or `yum install graphviz`
   - Windows: Download from https://www.graphviz.org/

## Installation Methods

### Method 1: Automated Script (Recommended)

#### Linux/macOS

```bash
cd backend
chmod +x scripts/install_mcp_server.sh
./scripts/install_mcp_server.sh
```

#### Windows PowerShell

```powershell
cd backend
.\scripts\install_mcp_server.ps1
```

The script will:
- Check prerequisites
- Create a virtual environment
- Install the MCP server
- Provide configuration instructions

### Method 2: Manual Installation

#### Step 1: Create Virtual Environment

```bash
# Using uv (recommended)
uv venv .mcp_server_venv --python 3.10

# Or using standard Python
python3 -m venv .mcp_server_venv
```

#### Step 2: Activate Virtual Environment

**Linux/macOS:**
```bash
source .mcp_server_venv/bin/activate
```

**Windows:**
```powershell
.\mcp_server_venv\Scripts\Activate.ps1
```

#### Step 3: Install MCP Server

```bash
pip install --upgrade pip
pip install awslabs.aws-diagram-mcp-server
```

#### Step 4: Verify Installation

```bash
python -c "import awslabs.aws_diagram_mcp_server; print('OK')"
```

## Configuration

After installation, configure the system to use the local installation.

### Option 1: Environment Variables (Recommended)

**Linux/macOS:**
```bash
export MCP_SERVER_VENV="./backend/.mcp_server_venv"
export USE_MCP_DIAGRAM_SERVER=true
```

**Windows PowerShell:**
```powershell
$env:MCP_SERVER_VENV = ".\backend\mcp_server_venv"
$env:USE_MCP_DIAGRAM_SERVER = "true"
```

**Windows CMD:**
```cmd
set MCP_SERVER_VENV=.\backend\mcp_server_venv
set USE_MCP_DIAGRAM_SERVER=true
```

### Option 2: Direct Command Path

**Linux/macOS:**
```bash
export MCP_DIAGRAM_SERVER_COMMAND="./backend/.mcp_server_venv/bin/python -m awslabs.aws_diagram_mcp_server"
export USE_MCP_DIAGRAM_SERVER=true
```

**Windows PowerShell:**
```powershell
$env:MCP_DIAGRAM_SERVER_COMMAND = ".\backend\mcp_server_venv\Scripts\python.exe -m awslabs.aws_diagram_mcp_server"
$env:USE_MCP_DIAGRAM_SERVER = "true"
```

### Option 3: Configuration File

Edit `backend/config/mcp_config.yaml`:

```yaml
enabled: true
server_command: "./backend/.mcp_server_venv/bin/python -m awslabs.aws_diagram_mcp_server"
# Or for Windows:
# server_command: "./backend/mcp_server_venv/Scripts/python.exe -m awslabs.aws_diagram_mcp_server"
timeout: 30
fallback_on_error: true
```

**Note:** Use absolute paths or paths relative to where the application runs.

## Auto-Detection

The MCP client automatically detects local installations in this order:

1. **Environment Variable** (`MCP_SERVER_VENV`)
   - Checks specified virtual environment

2. **Project Directory**
   - Looks for `.mcp_server_venv` or `mcp_server_venv` in project root

3. **Current Python Environment**
   - Checks if MCP server is installed in current Python

4. **Fallback to uvx**
   - Uses `uvx awslabs.aws-diagram-mcp-server` if no local installation found

## Verification

### Test Local Installation

```bash
# Activate venv
source .mcp_server_venv/bin/activate  # Linux/macOS
# or
.\mcp_server_venv\Scripts\Activate.ps1  # Windows

# Test MCP server
python -m awslabs.aws_diagram_mcp_server --help
```

### Test Integration

```bash
# Set environment variables
export USE_MCP_DIAGRAM_SERVER=true
export MCP_SERVER_VENV="./backend/.mcp_server_venv"

# Run example
cd backend
python examples/mcp_integration_example.py
```

Check logs for:
```
MCP Diagram Client initialized with command: .../mcp_server_venv/bin/python -m awslabs.aws_diagram_mcp_server
```

## Performance Benefits

### Before (uvx)
- Downloads package on first run (~2-5 seconds)
- Caches for subsequent runs
- Still has startup overhead

### After (Local Installation)
- No download overhead
- Faster startup (~0.5-1 second)
- Consistent performance
- Works offline

## Troubleshooting

### Installation Fails

**Error:** `pip install awslabs.aws-diagram-mcp-server` fails

**Solution:**
1. Ensure Python 3.10+ is installed
2. Upgrade pip: `pip install --upgrade pip`
3. Try installing from source if package name differs

### MCP Server Not Found

**Error:** `ModuleNotFoundError: No module named 'awslabs.aws_diagram_mcp_server'`

**Solution:**
1. Verify virtual environment is activated
2. Check installation: `pip list | grep awslabs`
3. Reinstall: `pip install --force-reinstall awslabs.aws-diagram-mcp-server`

### Wrong Python Version

**Error:** Python version mismatch

**Solution:**
1. Create venv with specific Python version:
   ```bash
   uv venv .mcp_server_venv --python 3.10
   ```
2. Or use system Python 3.10+:
   ```bash
   python3.10 -m venv .mcp_server_venv
   ```

### Path Issues (Windows)

**Error:** Path not found or spaces in path

**Solution:**
1. Use absolute paths in configuration
2. Quote paths with spaces
3. Use forward slashes or raw strings in Python

## Updating Local Installation

To update the MCP server:

```bash
# Activate venv
source .mcp_server_venv/bin/activate  # Linux/macOS
.\mcp_server_venv\Scripts\Activate.ps1  # Windows

# Upgrade package
pip install --upgrade awslabs.aws-diagram-mcp-server
```

## Uninstallation

To remove local installation:

```bash
# Remove virtual environment
rm -rf .mcp_server_venv  # Linux/macOS
Remove-Item -Recurse -Force mcp_server_venv  # Windows PowerShell

# Clear environment variables
unset MCP_SERVER_VENV
unset MCP_DIAGRAM_SERVER_COMMAND
```

## Best Practices

1. **Use Virtual Environment**
   - Isolates MCP server dependencies
   - Prevents conflicts with other packages

2. **Version Pinning** (Optional)
   ```bash
   pip install awslabs.aws-diagram-mcp-server==<version>
   ```

3. **Add to .gitignore**
   ```
   .mcp_server_venv/
   mcp_server_venv/
   ```

4. **Document Installation**
   - Add installation steps to project README
   - Include in deployment documentation

## Integration with CI/CD

For CI/CD pipelines, install MCP server in build step:

```yaml
# Example GitHub Actions
- name: Install MCP Server
  run: |
    python3 -m venv .mcp_server_venv
    source .mcp_server_venv/bin/activate
    pip install awslabs.aws-diagram-mcp-server
    
- name: Set Environment
  run: |
    echo "MCP_SERVER_VENV=$PWD/.mcp_server_venv" >> $GITHUB_ENV
    echo "USE_MCP_DIAGRAM_SERVER=true" >> $GITHUB_ENV
```

## References

- [AWS Diagram MCP Server](https://awslabs.github.io/mcp/servers/aws-diagram-mcp-server)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
