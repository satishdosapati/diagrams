# Deployment Guide - Git Pull Method

## EC2 Deployment

### Prerequisites

- AWS EC2 instance (Amazon Linux 2023)
- Public IP address
- Security group configured (ports 3000, 8000, 22)
- AWS credentials configured on EC2
- Git repository with your code

### Step 1: Initial Setup

SSH into your EC2 instance:

```bash
ssh -i satishmcp.pem ec2-user@100.31.143.57
```

Install system dependencies:

```bash
sudo yum update -y
sudo yum install -y python3 python3-pip python3-devel git curl gcc gcc-c++ make graphviz
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs
```

### Step 2: Clone Repository

```bash
sudo mkdir -p /opt/diagram-generator
sudo chown -R ec2-user:ec2-user /opt/diagram-generator
cd /opt/diagram-generator
git clone <your-repo-url> .
```

### Step 3: Configure Environment

Create `.env` file in `backend/`:

```bash
cd /opt/diagram-generator/backend
cp .env.example .env
nano .env
# Add your AWS credentials:
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
# BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
# OUTPUT_DIR=/opt/diagram-generator/output
```

### Step 4: Setup Backend

```bash
cd /opt/diagram-generator/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
mkdir -p /opt/diagram-generator/output
deactivate
```

### Step 5: Setup Frontend

```bash
cd /opt/diagram-generator/frontend
npm install
npm run build
```

### Step 6: Create systemd Services

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

### Step 7: Verify Deployment

- Frontend: http://your-ec2-ip:3000
- Backend API: http://your-ec2-ip:8000/api/health

### Step 8: Updating Deployment

When you make code changes:

```bash
# SSH into EC2
ssh -i satishmcp.pem ec2-user@100.31.143.57

# Pull latest code
cd /opt/diagram-generator
git pull origin main

# Update backend (if needed)
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart diagram-api

# Update frontend (if needed)
cd ../frontend
npm install
npm run build
sudo systemctl restart diagram-frontend
```

Or use the deployment script:

```bash
cd /opt/diagram-generator
bash deployment/deploy-git.sh
```

### Troubleshooting

Check service status:
```bash
sudo systemctl status diagram-api.service
sudo systemctl status diagram-frontend.service
```

View logs:
```bash
sudo journalctl -u diagram-api.service -f
sudo journalctl -u diagram-frontend.service -f
```

## See Also

- [Detailed Deployment Instructions](../DEPLOYMENT_INSTRUCTIONS.md)
- [Quick Deploy Guide](../QUICK_DEPLOY.md)
