#!/bin/bash
# Deployment script using Git Pull method for Amazon Linux 2023
# Run this ON EC2 after initial setup
# Usage: bash deployment/deploy-git.sh [branch-name]

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

# Configuration
BRANCH=${1:-main}
APP_DIR="/opt/diagram-generator/diagrams"
BACKUP_DIR="/opt/diagram-generator-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

log_info "Starting deployment of Architecture Diagram Generator..."
log_info "Branch: $BRANCH"
log_info "Timestamp: $TIMESTAMP"

# Navigate to project directory
if [ ! -d "$APP_DIR" ]; then
    log_error "Application directory not found: $APP_DIR"
    exit 1
fi

cd "$APP_DIR"

# Create backup directory
log_info "Creating backup..."
sudo mkdir -p "$BACKUP_DIR"
sudo chown ec2-user:ec2-user "$BACKUP_DIR"

# Backup current deployment (if exists)
if [ -d "$APP_DIR/backend/venv" ]; then
    log_info "Backing up current deployment..."
    tar -czf "$BACKUP_DIR/backend-backup-$TIMESTAMP.tar.gz" backend/venv 2>/dev/null || true
fi

# Pull latest code
log_info "Pulling latest code from Git (branch: $BRANCH)..."
if ! git fetch origin "$BRANCH"; then
    log_error "Failed to fetch from Git"
    exit 1
fi

# Check if there are changes
if git diff --quiet HEAD origin/"$BRANCH"; then
    log_warn "No changes detected. Already up to date."
else
    log_info "Changes detected. Pulling updates..."
    git pull origin "$BRANCH"
fi

# Update backend
log_info "Updating backend dependencies..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    log_warn "Virtual environment not found. Creating new one..."
    python3.11 -m venv venv
fi

source venv/bin/activate

# Upgrade pip first
log_info "Upgrading pip..."
pip install --upgrade pip --quiet

# Install/update dependencies
log_info "Installing Python dependencies..."
if ! pip install -r requirements.txt --quiet; then
    log_error "Failed to install backend dependencies"
    deactivate
    exit 1
fi

deactivate
log_info "Backend dependencies updated successfully"

# Update frontend
log_info "Updating frontend dependencies..."
cd ../frontend

# Install npm dependencies
if ! npm install --silent; then
    log_error "Failed to install frontend dependencies"
    exit 1
fi

# Build frontend
log_info "Building frontend..."
if ! npm run build; then
    log_error "Frontend build failed"
    exit 1
fi

log_info "Frontend build completed successfully"

# Restart services with health checks
log_info "Restarting services..."
cd "$APP_DIR"

# Restart backend
log_info "Restarting diagram-api service..."
if sudo systemctl restart diagram-api.service; then
    sleep 3
    if sudo systemctl is-active --quiet diagram-api.service; then
        log_info "Backend service started successfully"
    else
        log_error "Backend service failed to start"
        log_error "Check logs: sudo journalctl -u diagram-api.service -n 50"
        exit 1
    fi
else
    log_error "Failed to restart backend service"
    exit 1
fi

# Restart frontend
log_info "Restarting diagram-frontend service..."
if sudo systemctl restart diagram-frontend.service; then
    sleep 3
    if sudo systemctl is-active --quiet diagram-frontend.service; then
        log_info "Frontend service started successfully"
    else
        log_error "Frontend service failed to start"
        log_error "Check logs: sudo journalctl -u diagram-frontend.service -n 50"
        exit 1
    fi
else
    log_error "Failed to restart frontend service"
    exit 1
fi

# Health check
log_info "Performing health checks..."
sleep 2

BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "000")

if [ "$BACKEND_HEALTH" = "200" ]; then
    log_info "Backend health check: OK (HTTP $BACKEND_HEALTH)"
else
    log_warn "Backend health check: FAILED (HTTP $BACKEND_HEALTH)"
fi

if [ "$FRONTEND_HEALTH" = "200" ]; then
    log_info "Frontend health check: OK (HTTP $FRONTEND_HEALTH)"
else
    log_warn "Frontend health check: FAILED (HTTP $FRONTEND_HEALTH)"
fi

log_info "Deployment completed successfully!"
echo ""
log_info "Service Status:"
sudo systemctl status diagram-api diagram-frontend --no-pager -l || true
echo ""
log_info "Useful commands:"
echo "  Check status: sudo systemctl status diagram-api diagram-frontend"
echo "  View backend logs: sudo journalctl -u diagram-api.service -f"
echo "  View frontend logs: sudo journalctl -u diagram-frontend.service -f"
echo "  Restart services: sudo systemctl restart diagram-api diagram-frontend"
echo "  View backups: ls -lh $BACKUP_DIR"

