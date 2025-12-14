#!/bin/bash
# EC2 setup script for Architecture Diagram Generator - Amazon Linux 2023 (EC2 Linux 3)
# Run with: sudo bash ec2-setup-amazon-linux.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info "Starting EC2 setup for Architecture Diagram Generator (Amazon Linux 2023)..."

# Detect package manager (dnf is preferred for AL2023, but yum works too)
if command -v dnf &> /dev/null; then
    PKG_MGR="dnf"
    log_info "Using dnf package manager"
else
    PKG_MGR="yum"
    log_warn "Using yum package manager (dnf preferred for AL2023)"
fi

# Update system
log_info "Updating system packages..."
sudo $PKG_MGR update -y

# Install Python 3.11+ (Amazon Linux 2023 comes with Python 3.11 by default)
log_info "Installing Python 3.11+..."
sudo $PKG_MGR install -y python3.11 python3.11-pip python3.11-devel

# Verify Python version
PYTHON_VERSION=$(python3.11 --version 2>&1 | awk '{print $2}')
log_info "Python version: $PYTHON_VERSION"

# Ensure python3 points to python3.11
if ! command -v python3 &> /dev/null || [[ "$(python3 --version 2>&1 | awk '{print $2}')" != "3.11"* ]]; then
    log_info "Creating python3 symlink to python3.11..."
    sudo alternatives --set python3 /usr/bin/python3.11 || true
fi
PYTHON_CMD=python3.11

# Install Node.js 20+ (LTS)
log_info "Installing Node.js 20 LTS..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    log_info "Node.js already installed: $NODE_VERSION"
else
    curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
    sudo $PKG_MGR install -y nodejs
fi

# Verify Node.js version
NODE_VERSION=$(node --version)
log_info "Node.js version: $NODE_VERSION"

# Install npm if not present
if ! command -v npm &> /dev/null; then
    log_info "Installing npm..."
    sudo $PKG_MGR install -y npm
fi

# Install Graphviz (required for diagrams library)
log_info "Installing Graphviz..."
sudo $PKG_MGR install -y graphviz graphviz-devel

# Install other build dependencies
log_info "Installing system dependencies..."
# Check if curl is already available (via curl-minimal or curl)
if command -v curl &> /dev/null; then
    log_info "curl is already installed, skipping..."
    sudo $PKG_MGR install -y git gcc gcc-c++ make openssl-devel libffi-devel
else
    log_info "Installing curl..."
    sudo $PKG_MGR install -y git curl gcc gcc-c++ make openssl-devel libffi-devel || {
        log_warn "curl installation failed (may conflict with curl-minimal), continuing..."
        sudo $PKG_MGR install -y git gcc gcc-c++ make openssl-devel libffi-devel
    }
fi

# Create application directory structure
log_info "Creating application directory structure..."
sudo mkdir -p /opt/diagram-generator
sudo chown -R ec2-user:ec2-user /opt/diagram-generator

# Set proper permissions
sudo chmod 755 /opt/diagram-generator

# Note: Output and logs directories will be created after repository is cloned
# They will be at /opt/diagram-generator/diagrams/output and /opt/diagram-generator/diagrams/logs

log_info "EC2 setup completed successfully!"
echo ""
log_info "Installed versions:"
echo "  Python: $($PYTHON_CMD --version)"
echo "  Node.js: $(node --version)"
echo "  npm: $(npm --version)"
echo "  Graphviz: $(dot -V 2>&1 | head -1)"
echo ""
log_info "Next steps:"
echo "  1. Clone your repository to /opt/diagram-generator"
echo "  2. Run: cd /opt/diagram-generator/diagrams/backend && $PYTHON_CMD -m venv venv"
echo "  3. Run: source venv/bin/activate && pip install -r requirements.txt"
echo "  4. Run: cd ../frontend && npm install && npm run build"
echo "  5. Configure environment variables in backend/.env"
echo "  6. Install systemd services: sudo cp deployment/systemd/*.service /etc/systemd/system/"
echo "  7. Enable and start services: sudo systemctl daemon-reload && sudo systemctl enable diagram-api diagram-frontend && sudo systemctl start diagram-api diagram-frontend"

