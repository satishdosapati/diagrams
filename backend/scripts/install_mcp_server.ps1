# Install AWS Diagram MCP Server locally (Windows PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Installing AWS Diagram MCP Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if uv is installed
try {
    $uvVersion = uv --version 2>&1
    Write-Host "✓ uv found: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: uv is not installed" -ForegroundColor Red
    Write-Host "Install uv from: https://astral.sh/uv" -ForegroundColor Yellow
    exit 1
}

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Warning: Python not found, will install via uv" -ForegroundColor Yellow
}

# Install Python 3.11+ if needed via uv (prefer 3.11, fallback to 3.10 or 3.12)
Write-Host ""
Write-Host "Installing Python 3.11+ via uv..." -ForegroundColor Cyan
uv python install 3.11
if ($LASTEXITCODE -ne 0) {
    uv python install 3.10
    if ($LASTEXITCODE -ne 0) {
        uv python install 3.12
    }
}

# Check GraphViz
try {
    $dotVersion = dot -V 2>&1 | Select-Object -First 1
    Write-Host "✓ GraphViz found: $dotVersion" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "Warning: GraphViz is not installed" -ForegroundColor Yellow
    Write-Host "Please install GraphViz from: https://www.graphviz.org/" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

# Create virtual environment for MCP server
$MCP_VENV_DIR = if ($env:MCP_SERVER_VENV) { $env:MCP_SERVER_VENV } else { ".\mcp_server_venv" }
Write-Host ""
Write-Host "Creating virtual environment at: $MCP_VENV_DIR" -ForegroundColor Cyan

# Use uv to create venv with Python 3.11+ (prefer 3.11, fallback to 3.10 or 3.12)
uv venv $MCP_VENV_DIR --python 3.11
if ($LASTEXITCODE -ne 0) {
    uv venv $MCP_VENV_DIR --python 3.10
    if ($LASTEXITCODE -ne 0) {
        uv venv $MCP_VENV_DIR --python 3.12
    }
}

# Activate virtual environment
$activateScript = Join-Path $MCP_VENV_DIR "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Host "Error: Could not find activation script" -ForegroundColor Red
    exit 1
}

# Install MCP server package
Write-Host ""
Write-Host "Installing AWS Diagram MCP Server..." -ForegroundColor Cyan
python -m pip install --upgrade pip
python -m pip install awslabs.aws-diagram-mcp-server

# Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Cyan
try {
    python -c "import awslabs.aws_diagram_mcp_server" 2>&1 | Out-Null
    Write-Host "✓ MCP Server installed successfully" -ForegroundColor Green
} catch {
    # Try running via uv tool
    Write-Host "Testing via uv tool run..." -ForegroundColor Yellow
    uv tool run --from awslabs.aws-diagram-mcp-server@latest awslabs.aws-diagram-mcp-server.exe --help 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ MCP Server available via uv tool" -ForegroundColor Green
    } else {
        Write-Host "✗ MCP Server installation verification failed" -ForegroundColor Red
        exit 1
    }
}

# Get installation path
$MCP_PYTHON = (Get-Command python).Source
$MCP_VENV_PATH = Split-Path $MCP_PYTHON -Parent

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Virtual Environment: $MCP_VENV_DIR"
Write-Host "Python: $MCP_PYTHON"
Write-Host ""
Write-Host "To use the local installation, set:" -ForegroundColor Yellow
Write-Host "  `$env:MCP_SERVER_VENV = `"$MCP_VENV_DIR`""
Write-Host "  `$env:MCP_DIAGRAM_SERVER_COMMAND = `"$MCP_PYTHON -m awslabs.aws_diagram_mcp_server`""
Write-Host ""
Write-Host "Or update backend/config/mcp_config.yaml:" -ForegroundColor Yellow
Write-Host "  server_command: `"$MCP_PYTHON -m awslabs.aws_diagram_mcp_server`""
Write-Host ""
