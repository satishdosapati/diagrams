#!/bin/bash
# Install AWS Diagram MCP Server locally for improved performance
# This script installs the MCP server using uv or pip

set -e

echo "=========================================="
echo "Installing AWS Diagram MCP Server"
echo "=========================================="

# Check if uv is installed
if command -v uv &> /dev/null; then
    echo "✓ uv is installed"
    USE_UV=true
else
    echo "⚠ uv not found, will use pip instead"
    USE_UV=false
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "Python version: $PYTHON_VERSION"

# Check if GraphViz is installed
if command -v dot &> /dev/null; then
    echo "✓ GraphViz is installed"
    dot -V
else
    echo "⚠ GraphViz not found. Installing..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y graphviz
        elif command -v yum &> /dev/null; then
            sudo yum install -y graphviz
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y graphviz
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install graphviz
    fi
fi

# Install MCP Server
if [ "$USE_UV" = true ]; then
    echo ""
    echo "Installing MCP server using uv..."
    
    # Install Python 3.10+ if not available
    if ! uv python list | grep -q "3.10\|3.11\|3.12"; then
        echo "Installing Python 3.10..."
        uv python install 3.10
    fi
    
    # Install MCP server globally using uv
    echo "Installing awslabs.aws-diagram-mcp-server..."
    uv tool install awslabs.aws-diagram-mcp-server
    
    # Verify installation
    if uv tool run awslabs.aws-diagram-mcp-server --help &> /dev/null; then
        echo "✓ MCP server installed successfully with uv"
        echo ""
        echo "To use the installed version, set:"
        echo "  export MCP_DIAGRAM_SERVER_COMMAND=\"uv tool run awslabs.aws-diagram-mcp-server\""
    else
        echo "⚠ Installation verification failed"
        exit 1
    fi
else
    echo ""
    echo "Installing MCP server using pip..."
    
    # Try installing via pip (if package is available)
    pip install --upgrade pip
    
    # Install from GitHub if available
    if pip install git+https://github.com/awslabs/aws-diagram-mcp-server.git &> /dev/null; then
        echo "✓ MCP server installed via pip from GitHub"
    else
        echo "⚠ Could not install via pip. Please install uv:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Set USE_MCP_DIAGRAM_SERVER=true"
echo "2. Update MCP_DIAGRAM_SERVER_COMMAND if needed"
echo "3. Test with: python examples/mcp_integration_example.py"
