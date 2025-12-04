#!/bin/bash
# Deployment script using Git Pull method
# Run this ON EC2 after initial setup

set -e

echo "Deploying Architecture Diagram Generator..."

# Navigate to project directory
cd /opt/diagram-generator

# Pull latest code
echo "Pulling latest code from Git..."
git pull origin main  # Change 'main' to your branch name if different

# Update backend
echo "Updating backend..."
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Update frontend
echo "Updating frontend..."
cd ../frontend
npm install
npm run build

# Restart services
echo "Restarting services..."
sudo systemctl restart diagram-api.service
sudo systemctl restart diagram-frontend.service

echo "Deployment completed!"
echo ""
echo "Check status:"
echo "  sudo systemctl status diagram-api diagram-frontend"
echo ""
echo "View logs:"
echo "  sudo journalctl -u diagram-api -f"
echo "  sudo journalctl -u diagram-frontend -f"

