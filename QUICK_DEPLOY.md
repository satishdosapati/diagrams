# Quick Deployment Guide - Amazon Linux 2023

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

### 2. Run Setup Script
```bash
# Copy setup script to EC2 first, then:
sudo bash /opt/diagram-generator/deployment/ec2-setup-amazon-linux.sh
```

### 3. Deploy Code from Local Machine

**Option A: Using SCP (Windows)**

```powershell
# From project root on Windows
cd C:\Users\usdoss02\Satish-Playground\diagrams

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Copy backend
scp -i satishmcp.pem -r backend/* ec2-user@100.31.143.57:/opt/diagram-generator/backend/

# Copy frontend dist
scp -i satishmcp.pem -r frontend/dist/* ec2-user@100.31.143.57:/opt/diagram-generator/frontend/dist/

# Copy deployment files
scp -i satishmcp.pem -r deployment/* ec2-user@100.31.143.57:/opt/diagram-generator/deployment/
```

**Option B: Using Git (if repo is on GitHub)**
```bash
# On EC2
cd /opt/diagram-generator
git clone your-repo-url .
```

### 4. Setup Backend on EC2
```bash
cd /opt/diagram-generator/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
nano .env
# Add your AWS credentials (see backend/.env.example)
```

### 5. Setup Frontend on EC2
```bash
cd /opt/diagram-generator/frontend
npm install
```

### 6. Create systemd Services
```bash
# Copy service files
sudo cp /opt/diagram-generator/deployment/systemd/diagram-api-amazon-linux.service /etc/systemd/system/diagram-api.service
sudo cp /opt/diagram-generator/deployment/systemd/diagram-frontend-amazon-linux.service /etc/systemd/system/diagram-frontend.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable diagram-api diagram-frontend
sudo systemctl start diagram-api diagram-frontend
```

### 7. Configure Security Group
In AWS Console → EC2 → Security Groups:
- Add inbound rule: Custom TCP, Port 3000, Source: 0.0.0.0/0
- Add inbound rule: Custom TCP, Port 8000, Source: 0.0.0.0/0

### 8. Access Application
- Frontend: http://100.31.143.57:3000
- Backend: http://100.31.143.57:8000/api/health

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

