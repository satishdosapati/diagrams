#!/bin/bash
# Rollback script for Architecture Diagram Generator
# Usage: bash deployment/rollback.sh [backup-timestamp]
# Example: bash deployment/rollback.sh 20240101_120000

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

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

BACKUP_DIR="/opt/diagram-generator-backups"
APP_DIR="/opt/diagram-generator/diagrams"

if [ -z "$1" ]; then
    log_info "Available backups:"
    ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null | awk '{print $9}' | xargs -n1 basename || log_warn "No backups found"
    echo ""
    log_error "Please specify a backup timestamp"
    echo "Usage: bash deployment/rollback.sh [backup-timestamp]"
    echo "Example: bash deployment/rollback.sh 20240101_120000"
    exit 1
fi

BACKUP_TIMESTAMP=$1
BACKUP_FILE="$BACKUP_DIR/backend-backup-$BACKUP_TIMESTAMP.tar.gz"

if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Backup file not found: $BACKUP_FILE"
    log_info "Available backups:"
    ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null | awk '{print $9}' | xargs -n1 basename || log_warn "No backups found"
    exit 1
fi

log_warn "This will restore the backend virtual environment from backup: $BACKUP_FILE"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log_info "Rollback cancelled"
    exit 0
fi

log_info "Stopping services..."
sudo systemctl stop diagram-api.service diagram-frontend.service || true

log_info "Backing up current venv..."
CURRENT_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
if [ -d "$APP_DIR/backend/venv" ]; then
    tar -czf "$BACKUP_DIR/venv-before-rollback-$CURRENT_TIMESTAMP.tar.gz" -C "$APP_DIR" backend/venv 2>/dev/null || true
fi

log_info "Restoring backup..."
cd "$APP_DIR"
rm -rf backend/venv
tar -xzf "$BACKUP_FILE" -C "$APP_DIR"

log_info "Restarting services..."
sudo systemctl start diagram-api.service diagram-frontend.service

sleep 3

# Health check
log_info "Performing health check..."
if systemctl is-active --quiet diagram-api.service; then
    log_info "Backend service started successfully"
else
    log_error "Backend service failed to start"
    log_error "Check logs: sudo journalctl -u diagram-api.service -n 50"
    exit 1
fi

log_info "Rollback completed successfully!"
log_info "Backup restored from: $BACKUP_FILE"
