#!/bin/bash
# EC2 setup script for Architecture Diagram Generator - Amazon Linux 2023
# Run with: sudo bash ec2-setup-amazon-linux.sh

set -e

echo "Starting EC2 setup for Architecture Diagram Generator (Amazon Linux 2023)..."

# Update system
echo "Updating system packages..."
sudo yum update -y

# Install Python 3.11 (or use python3 if 3.11 not available)
echo "Installing Python..."
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
else
    # Install Python 3.11 from source or use available version
    sudo yum install -y python3 python3-pip python3-devel
    PYTHON_CMD=python3
fi

# Install Node.js 20+
echo "Installing Node.js 20..."
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs

# Install Graphviz (required for diagrams library)
echo "Installing Graphviz..."
sudo yum install -y graphviz

# Install other dependencies
echo "Installing system dependencies..."
sudo yum install -y git curl gcc gcc-c++ make

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

