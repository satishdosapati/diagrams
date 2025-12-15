#!/bin/bash
# Deployment script for Architecture Diagram Generator
# Run from project root
# Usage: EC2_HOST=your-ip EC2_USER=ubuntu bash deployment/deploy.sh

set -e

EC2_HOST="${EC2_HOST:-your-ec2-ip}"
EC2_USER="${EC2_USER:-ubuntu}"
DEPLOY_DIR="/opt/diagram-generator"

if [ "$EC2_HOST" = "your-ec2-ip" ]; then
    echo "Error: Please set EC2_HOST environment variable"
    echo "Usage: EC2_HOST=your-ip EC2_USER=ubuntu bash deployment/deploy.sh"
    exit 1
fi

echo "Deploying to EC2 at ${EC2_HOST}..."

# Build frontend
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Copy files to EC2
echo "Copying files to EC2..."
rsync -avz --exclude 'node_modules' --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
  backend/ ${EC2_USER}@${EC2_HOST}:${DEPLOY_DIR}/backend/
rsync -avz frontend/dist/ ${EC2_USER}@${EC2_HOST}:${DEPLOY_DIR}/frontend/dist/
rsync -avz deployment/ ${EC2_USER}@${EC2_HOST}:${DEPLOY_DIR}/deployment/

# Setup backend on EC2
echo "Setting up backend on EC2..."
ssh ${EC2_USER}@${EC2_HOST} << 'EOF'
cd /opt/diagram-generator/backend
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
EOF

# Setup systemd services
echo "Setting up systemd services..."
ssh ${EC2_USER}@${EC2_HOST} << 'EOF'
sudo cp /opt/diagram-generator/deployment/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable diagram-api.service
sudo systemctl enable diagram-frontend.service
sudo systemctl restart diagram-api.service
sudo systemctl restart diagram-frontend.service
EOF

echo "Deployment completed!"
echo ""
echo "Frontend: http://${EC2_HOST}:3000"
echo "Backend API: http://${EC2_HOST}:8000/api/health"
echo ""
echo "Check service status:"
echo "  ssh ${EC2_USER}@${EC2_HOST} 'sudo systemctl status diagram-api diagram-frontend'"

