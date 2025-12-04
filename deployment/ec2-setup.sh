#!/bin/bash
# EC2 setup script for Architecture Diagram Generator
# Run with: sudo bash ec2-setup.sh

set -e

echo "Starting EC2 setup for Architecture Diagram Generator..."

# Update system
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install Python 3.11+
echo "Installing Python 3.11..."
apt-get install -y python3.11 python3.11-venv python3-pip

# Install Node.js 20+
echo "Installing Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Install Graphviz (required for diagrams library)
echo "Installing Graphviz..."
apt-get install -y graphviz

# Install other dependencies
echo "Installing system dependencies..."
apt-get install -y git curl build-essential

# Create application directory
echo "Creating application directory..."
mkdir -p /opt/diagram-generator
mkdir -p /opt/diagram-generator/output
chown -R $SUDO_USER:$SUDO_USER /opt/diagram-generator

# Create system user for backend (optional, for production)
# useradd -r -s /bin/false diagram-api || true

echo "EC2 setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Deploy your application code to /opt/diagram-generator"
echo "2. Set up systemd services"
echo "3. Configure environment variables"

