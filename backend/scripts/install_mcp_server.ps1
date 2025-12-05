# Install AWS Diagram MCP Server locally for Windows
# Run with: powershell -ExecutionPolicy Bypass -File install_mcp_server.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Installing AWS Diagram MCP Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if uv is installed
$uvInstalled = Get-Command uv -ErrorAction SilentlyContinue
if ($uvInstalled) {
    Write-Host "✓ uv is installed" -ForegroundColor Green
    $useUv = $true
} else {
    Write-Host "⚠ uv not found, will attempt pip installation" -ForegroundColor Yellow
    $useUv = $false
}

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion"

# Check if GraphViz is installed
$graphvizInstalled = Get-Command dot -ErrorAction SilentlyContinue
if ($graphvizInstalled) {
    Write-Host "✓ GraphViz is installed" -ForegroundColor Green
    dot -V
} else {
    Write-Host "⚠ GraphViz not found. Please install from:" -ForegroundColor Yellow
    Write-Host "  https://www.graphviz.org/download/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or use Chocolatey:" -ForegroundColor Yellow
    Write-Host "  choco install graphviz" -ForegroundColor Yellow
}

# Install MCP Server
if ($useUv) {
    Write-Host ""
    Write-Host "Installing MCP server using uv..." -ForegroundColor Cyan
    
    # Install Python 3.10+ if not available
    $pythonList = uv python list 2>&1
    if ($pythonList -notmatch "3\.(10|11|12)") {
        Write-Host "Installing Python 3.10..."
        uv python install 3.10
    }
    
    # Install MCP server using uv tool
    Write-Host "Installing awslabs.aws-diagram-mcp-server..."
    uv tool install awslabs.aws-diagram-mcp-server
    
    # Verify installation
    $testResult = uv tool run awslabs.aws-diagram-mcp-server --help 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ MCP server installed successfully with uv" -ForegroundColor Green
        Write-Host ""
        Write-Host "To use the installed version, set:" -ForegroundColor Yellow
        Write-Host '  $env:MCP_DIAGRAM_SERVER_COMMAND="uv tool run --from awslabs.aws-diagram-mcp-server@latest awslabs.aws-diagram-mcp-server.exe"' -ForegroundColor Yellow
    } else {
        Write-Host "⚠ Installation verification failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "Installing MCP server using pip..." -ForegroundColor Cyan
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Try installing from GitHub
    Write-Host "Attempting to install from GitHub..."
    python -m pip install git+https://github.com/awslabs/aws-diagram-mcp-server.git
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ MCP server installed via pip" -ForegroundColor Green
    } else {
        Write-Host "⚠ Could not install via pip. Please install uv:" -ForegroundColor Red
        Write-Host "  powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Set USE_MCP_DIAGRAM_SERVER=true"
Write-Host "2. Update MCP_DIAGRAM_SERVER_COMMAND if needed"
Write-Host "3. Test with: python examples/mcp_integration_example.py"
