#!/bin/bash
# Install AWS Diagram MCP Server locally

set -e

echo "=========================================="
echo "Installing AWS Diagram MCP Server"
echo "=========================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed"
    echo "Install uv from: https://astral.sh/uv"
    exit 1
fi

echo "✓ uv found: $(uv --version)"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python found: $(python3 --version)"

# Install Python 3.10+ if needed via uv
echo ""
echo "Installing Python 3.10+ via uv..."
uv python install 3.10 || uv python install 3.11 || uv python install 3.12

# Install GraphViz (check if installed)
if ! command -v dot &> /dev/null; then
    echo ""
    echo "Warning: GraphViz is not installed"
    echo "Please install GraphViz:"
    echo "  macOS: brew install graphviz"
    echo "  Linux: apt-get install graphviz or yum install graphviz"
    echo "  Windows: Download from https://www.graphviz.org/"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ GraphViz found: $(dot -V 2>&1 | head -n1)"
fi

# Create virtual environment for MCP server
MCP_VENV_DIR="${MCP_VENV_DIR:-./.mcp_server_venv}"
echo ""
echo "Creating virtual environment at: $MCP_VENV_DIR"

# Use uv to create venv with Python 3.10+
uv venv "$MCP_VENV_DIR" --python 3.10 || uv venv "$MCP_VENV_DIR" --python 3.11 || uv venv "$MCP_VENV_DIR"

# Activate virtual environment
source "$MCP_VENV_DIR/bin/activate"

# Install MCP server package
echo ""
echo "Installing AWS Diagram MCP Server..."
pip install --upgrade pip
pip install awslabs.aws-diagram-mcp-server

# Verify installation
echo ""
echo "Verifying installation..."
if python -c "import awslabs.aws_diagram_mcp_server" 2>/dev/null; then
    echo "✓ MCP Server installed successfully"
else
    # Try running via uv tool
    echo "Testing via uv tool run..."
    uv tool run --from awslabs.aws-diagram-mcp-server@latest awslabs.aws-diagram-mcp-server --help > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ MCP Server available via uv tool"
    else
        echo "✗ MCP Server installation verification failed"
        exit 1
    fi
fi

# Get installation path
MCP_PYTHON=$(which python)
MCP_VENV_PATH=$(dirname "$MCP_PYTHON")

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Virtual Environment: $MCP_VENV_DIR"
echo "Python: $MCP_PYTHON"
echo ""
echo "To use the local installation, set:"
echo "  export MCP_SERVER_VENV=\"$MCP_VENV_DIR\""
echo "  export MCP_DIAGRAM_SERVER_COMMAND=\"$MCP_PYTHON -m awslabs.aws_diagram_mcp_server\""
echo ""
echo "Or update backend/config/mcp_config.yaml:"
echo "  server_command: \"$MCP_PYTHON -m awslabs.aws_diagram_mcp_server\""
echo ""
