#!/bin/bash
# Health check script for Architecture Diagram Generator
# Usage: bash deployment/health-check.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

EXIT_CODE=0

echo "=== Health Check for Architecture Diagram Generator ==="
echo ""

# Check systemd services
echo "Checking systemd services..."
if systemctl is-active --quiet diagram-api.service; then
    log_info "Backend service (diagram-api) is running"
else
    log_error "Backend service (diagram-api) is not running"
    EXIT_CODE=1
fi

if systemctl is-active --quiet diagram-frontend.service; then
    log_info "Frontend service (diagram-frontend) is running"
else
    log_error "Frontend service (diagram-frontend) is not running"
    EXIT_CODE=1
fi

echo ""

# Check HTTP endpoints
echo "Checking HTTP endpoints..."

# Backend health check
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost:8000/health 2>/dev/null || echo "000")
if [ "$BACKEND_STATUS" = "200" ]; then
    log_info "Backend health endpoint: OK (HTTP $BACKEND_STATUS)"
else
    log_error "Backend health endpoint: FAILED (HTTP $BACKEND_STATUS)"
    EXIT_CODE=1
fi

# Frontend check
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost:3000 2>/dev/null || echo "000")
if [ "$FRONTEND_STATUS" = "200" ]; then
    log_info "Frontend endpoint: OK (HTTP $FRONTEND_STATUS)"
else
    log_error "Frontend endpoint: FAILED (HTTP $FRONTEND_STATUS)"
    EXIT_CODE=1
fi

echo ""

# Check disk space
echo "Checking disk space..."
DISK_USAGE=$(df -h /opt | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    log_info "Disk usage: ${DISK_USAGE}% (OK)"
else
    log_warn "Disk usage: ${DISK_USAGE}% (High)"
fi

# Check memory
echo "Checking memory..."
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
if [ "$MEMORY_USAGE" -lt 85 ]; then
    log_info "Memory usage: ${MEMORY_USAGE}% (OK)"
else
    log_warn "Memory usage: ${MEMORY_USAGE}% (High)"
fi

echo ""

# Check Python virtual environment
echo "Checking backend dependencies..."
if [ -d "/opt/diagram-generator/diagrams/backend/venv" ]; then
    if [ -f "/opt/diagram-generator/diagrams/backend/venv/bin/uvicorn" ]; then
        log_info "Backend virtual environment: OK"
    else
        log_error "Backend virtual environment: Missing uvicorn"
        EXIT_CODE=1
    fi
else
    log_error "Backend virtual environment: Not found"
    EXIT_CODE=1
fi

# Check frontend build
echo "Checking frontend build..."
if [ -d "/opt/diagram-generator/diagrams/frontend/dist" ]; then
    log_info "Frontend build: OK"
else
    log_error "Frontend build: Not found (run npm run build)"
    EXIT_CODE=1
fi

echo ""
echo "=== Health Check Complete ==="

if [ $EXIT_CODE -eq 0 ]; then
    log_info "All checks passed!"
else
    log_error "Some checks failed. Review the output above."
fi

exit $EXIT_CODE
