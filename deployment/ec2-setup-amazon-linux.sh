#!/bin/bash
# EC2 setup script for Architecture Diagram Generator - Amazon Linux 2023
# Run with: sudo bash ec2-setup-amazon-linux.sh

set -e

echo "Starting EC2 setup for Architecture Diagram Generator (Amazon Linux 2023)..."

# Update system
echo "Updating system packages..."
sudo yum update -y

# Install Python 3.11 (required for strands-agents which needs >=3.10)
echo "Installing Python 3.11..."
# Check if Python 3.11 is already installed
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
    echo "Python 3.11 already installed"
else
    # Try to install Python 3.11 from Amazon Linux repositories
    if sudo yum install -y python3.11 python3.11-pip python3.11-devel 2>/dev/null; then
        PYTHON_CMD=python3.11
        echo "Python 3.11 installed successfully"
    else
        # Try Python 3.10 as fallback
        echo "Python 3.11 not available, trying Python 3.10..."
        if sudo yum install -y python3.10 python3.10-pip python3.10-devel 2>/dev/null; then
            PYTHON_CMD=python3.10
            echo "Python 3.10 installed successfully"
        else
            # Last resort: check if default python3 is 3.10+
            DEFAULT_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
            MAJOR=$(echo $DEFAULT_VERSION | cut -d. -f1)
            MINOR=$(echo $DEFAULT_VERSION | cut -d. -f2)
            if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 10 ]; then
                PYTHON_CMD=python3
                echo "Using default Python $DEFAULT_VERSION (>=3.10)"
            else
                echo "ERROR: Python 3.10+ is required but not available. Please install Python 3.10 or 3.11 manually."
                exit 1
            fi
        fi
    fi
fi

# Verify Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "Using: $PYTHON_VERSION"

# Install Node.js 20+
echo "Installing Node.js 20..."
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs

# Install Graphviz (required for diagrams library)
echo "Installing Graphviz..."
sudo yum install -y graphviz

# Install other dependencies
echo "Installing system dependencies..."
# Check if curl command exists (curl-minimal provides it on AL2023)
if ! command -v curl &> /dev/null; then
    echo "Installing curl..."
    sudo yum install -y curl || sudo yum install -y --allowerasing curl
else
    echo "curl already available (via curl-minimal)"
fi

# Install remaining dependencies
sudo yum install -y git gcc gcc-c++ make

# Create application directory
echo "Creating application directory..."
sudo mkdir -p /opt/diagram-generator
sudo mkdir -p /opt/diagram-generator/output
sudo chown -R ec2-user:ec2-user /opt/diagram-generator

echo "EC2 setup completed successfully!"
echo ""
echo "Python version: $($PYTHON_CMD --version)"
echo "Node.js version: $(node --version)"
echo "Graphviz version: $(dot -V 2>&1 | head -1)"
echo ""
echo "Next steps:"
echo "1. Deploy your application code to /opt/diagram-generator"
echo "2. Set up systemd services"
echo "3. Configure environment variables in backend/.env"
