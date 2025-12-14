#!/bin/bash
# Install systemd services for Architecture Diagram Generator
# Run with: sudo bash deployment/install-services.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (use sudo)"
    exit 1
fi

APP_DIR="/opt/diagram-generator/diagrams"
SERVICE_DIR="$APP_DIR/deployment/systemd"
SYSTEMD_DIR="/etc/systemd/system"

log_info "Installing systemd services..."

# Check if service files exist
if [ ! -f "$SERVICE_DIR/diagram-api-amazon-linux.service" ] || [ ! -f "$SERVICE_DIR/diagram-frontend-amazon-linux.service" ]; then
    log_error "Service files not found in $SERVICE_DIR"
    exit 1
fi

# Copy service files
log_info "Copying service files..."
cp "$SERVICE_DIR/diagram-api-amazon-linux.service" "$SYSTEMD_DIR/diagram-api.service"
cp "$SERVICE_DIR/diagram-frontend-amazon-linux.service" "$SYSTEMD_DIR/diagram-frontend.service"

# Reload systemd
log_info "Reloading systemd daemon..."
systemctl daemon-reload

# Enable services
log_info "Enabling services..."
systemctl enable diagram-api.service
systemctl enable diagram-frontend.service

log_info "Services installed successfully!"
echo ""
log_info "Next steps:"
echo "  1. Ensure backend/.env file exists with required configuration"
echo "  2. Start services: sudo systemctl start diagram-api diagram-frontend"
echo "  3. Check status: sudo systemctl status diagram-api diagram-frontend"
echo "  4. View logs: sudo journalctl -u diagram-api.service -f"
