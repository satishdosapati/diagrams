# Quick Deployment Guide - Git Pull Method

## Your EC2 Details
- **IP**: 100.31.143.57
- **User**: ec2-user
- **OS**: Amazon Linux 2023
- **SSH Key**: satishmcp.pem

## Quick Start (Copy-Paste Commands)

### 1. SSH into EC2
```bash
ssh -i satishmcp.pem ec2-user@100.31.143.57
```

### 2. Install Dependencies
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip python3-devel git curl gcc gcc-c++ make graphviz
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs
```

### 3. Clone Repository
```bash
sudo mkdir -p /opt/diagram-generator
sudo chown -R ec2-user:ec2-user /opt/diagram-generator
cd /opt/diagram-generator
git clone <your-repo-url> .
# Replace <your-repo-url> with your actual repository URL
```

### 4. Setup Backend
```bash
cd /opt/diagram-generator/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # Add your AWS credentials
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
# BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
# OUTPUT_DIR=/opt/diagram-generator/output

mkdir -p /opt/diagram-generator/output
deactivate
```

### 5. Setup Frontend
```bash
cd /opt/diagram-generator/frontend
npm install
npm run build
```

### 6. Create systemd Services
```bash
# Backend service
sudo tee /etc/systemd/system/diagram-api.service > /dev/null << 'EOF'
[Unit]
Description=Architecture Diagram Generator API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/diagram-generator/backend
Environment="PATH=/opt/diagram-generator/backend/venv/bin"
EnvironmentFile=/opt/diagram-generator/backend/.env
ExecStart=/opt/diagram-generator/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Frontend service
sudo tee /etc/systemd/system/diagram-frontend.service > /dev/null << 'EOF'
[Unit]
Description=Architecture Diagram Generator Frontend
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/diagram-generator/frontend
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/npm run preview -- --host 0.0.0.0 --port 3000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable diagram-api diagram-frontend
sudo systemctl start diagram-api diagram-frontend
```

### 7. Configure Security Group
In AWS Console → EC2 → Security Groups:
- Add inbound rule: Custom TCP, Port 3000, Source: 0.0.0.0/0
- Add inbound rule: Custom TCP, Port 8000, Source: 0.0.0.0/0

### 8. Verify
```bash
sudo systemctl status diagram-api diagram-frontend
curl http://localhost:8000/health
```

### 9. Access
- Frontend: http://100.31.143.57:3000
- Backend: http://100.31.143.57:8000/api/health

## Updating Code

```bash
# SSH into EC2
ssh -i satishmcp.pem ec2-user@100.31.143.57

# Pull latest code
cd /opt/diagram-generator
git pull origin main

# Update backend if needed
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart diagram-api

# Update frontend if needed
cd ../frontend
npm install
npm run build
sudo systemctl restart diagram-frontend
```

## Troubleshooting

```bash
# Check services
sudo systemctl status diagram-api diagram-frontend

# View logs
sudo journalctl -u diagram-api -f
sudo journalctl -u diagram-frontend -f

# Restart services
sudo systemctl restart diagram-api diagram-frontend
```
