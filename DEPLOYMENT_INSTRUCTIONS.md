# EC2 Deployment Instructions - Git Pull Method

## Prerequisites

- AWS EC2 instance running (Amazon Linux 2023)
- Public IP address (your IP: 100.31.143.57)
- SSH access with PEM key
- Git repository with your code (GitHub, GitLab, etc.)
- Security group configured:
  - Port 22 (SSH)
  - Port 3000 (Frontend)
  - Port 8000 (Backend API)
- AWS credentials configured on EC2 (for Bedrock access)

## Step-by-Step Deployment

### Step 1: SSH into EC2 Instance

```bash
ssh -i satishmcp.pem ec2-user@100.31.143.57
```

### Step 2: Install System Dependencies

```bash
# Update system
sudo yum update -y

# Install Python 3 (or python3.11 if available)
sudo yum install -y python3 python3-pip python3-devel

# Install Node.js 20+
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs

# Install Graphviz (required for diagrams library)
sudo yum install -y graphviz

# Install Git and build tools
#sudo yum install -y git curl gcc gcc-c++ make
sudo dnf install git -y

# Verify installations
python3 --version
node --version
git --version
dot -V  # Graphviz
```

### Step 3: Clone Repository

```bash
# Create application directory
sudo mkdir -p /opt/diagram-generator
sudo chown -R ec2-user:ec2-user /opt/diagram-generator

# Clone your repository
cd /opt/diagram-generator
git clone <your-repo-url> .

# Or if repository already exists, pull latest:
# cd /opt/diagram-generator
# git pull origin main
```

**Note:** Replace `<your-repo-url>` with your actual Git repository URL.

### Step 4: Setup Backend

```bash
cd /opt/diagram-generator/diagrams/backend

sudo dnf install python3.11-pip -y

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your AWS credentials
nano .env
# Add:
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
# BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
# API_HOST=0.0.0.0
# API_PORT=8000
# OUTPUT_DIR=/opt/diagram-generator/output

# Create output directory
mkdir -p /opt/diagram-generator/output

# Deactivate virtual environment
deactivate
```

### Step 5: Setup Frontend

```bash
cd /opt/diagram-generator/diagrams/frontend

# Install dependencies
npm install

# Build frontend for production
npm run build

# Verify build was created
ls -la dist/
```

### Step 6: Create systemd Service Files

```bash
# Create backend service
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
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create frontend service
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
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable diagram-api.service
sudo systemctl enable diagram-frontend.service

# Start services
sudo systemctl start diagram-api.service
sudo systemctl start diagram-frontend.service
```

### Step 7: Configure Security Group

In AWS Console:
1. Go to EC2 → Security Groups
2. Select your instance's security group
3. Add inbound rules:
   - **Type**: Custom TCP, **Port**: 3000, **Source**: 0.0.0.0/0 (or your specific IP)
   - **Type**: Custom TCP, **Port**: 8000, **Source**: 0.0.0.0/0 (or your specific IP)
   - **Type**: SSH, **Port**: 22, **Source**: Your IP

### Step 8: Verify Deployment

```bash
# Check service status
sudo systemctl status diagram-api.service
sudo systemctl status diagram-frontend.service

# Check if services are running
sudo systemctl is-active diagram-api diagram-frontend

# Test backend locally
curl http://localhost:8000/health

# Test frontend locally
curl http://localhost:3000

# View logs
sudo journalctl -u diagram-api.service -n 50
sudo journalctl -u diagram-frontend.service -n 50
```

### Step 9: Access Application

From your browser:
- **Frontend**: http://100.31.143.57:3000
- **Backend API**: http://100.31.143.57:8000/api/health
- **API Docs**: http://100.31.143.57:8000/docs

## Updating Deployment (Git Pull Method)

When you make changes to the code:

```bash
# SSH into EC2
ssh -i satishmcp.pem ec2-user@100.31.143.57

# Navigate to project directory
cd /opt/diagram-generator

# Pull latest changes
git pull origin main  # or your branch name

# Restart backend (if backend code changed)
cd backend
source venv/bin/activate
pip install -r requirements.txt  # Update dependencies if needed
deactivate
sudo systemctl restart diagram-api.service

# Rebuild and restart frontend (if frontend code changed)
cd ../frontend
npm install  # Update dependencies if needed
npm run build
sudo systemctl restart diagram-frontend.service

# Check status
sudo systemctl status diagram-api diagram-frontend
```

## Troubleshooting

### Service Not Starting

```bash
# Check service status
sudo systemctl status diagram-api.service

# View recent logs
sudo journalctl -u diagram-api.service -n 100 --no-pager

# Check for errors
sudo journalctl -u diagram-api.service -p err
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R ec2-user:ec2-user /opt/diagram-generator

# Check permissions
ls -la /opt/diagram-generator/backend/
ls -la /opt/diagram-generator/frontend/
```

### Port Already in Use

```bash
# Check what's using the ports
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3000

# Kill process if needed (replace PID)
sudo kill -9 <PID>
```

### AWS Credentials Issues

```bash
# Test AWS credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1

# Verify .env file
cat /opt/diagram-generator/backend/.env
```

### Frontend Build Errors

```bash
cd /opt/diagram-generator/frontend

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Try building again
npm run build
```

### Backend Import Errors

```bash
cd /opt/diagram-generator/backend
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Test imports
python -c "from src.api.routes import router; print('OK')"
```

## Quick Reference Commands

```bash
# Restart services
sudo systemctl restart diagram-api.service
sudo systemctl restart diagram-frontend.service

# Stop services
sudo systemctl stop diagram-api.service
sudo systemctl stop diagram-frontend.service

# Start services
sudo systemctl start diagram-api.service
sudo systemctl start diagram-frontend.service

# View live logs
sudo journalctl -u diagram-api.service -f
sudo journalctl -u diagram-frontend.service -f

# Check service status
sudo systemctl status diagram-api diagram-frontend

# Enable/disable services
sudo systemctl enable diagram-api diagram-frontend
sudo systemctl disable diagram-api diagram-frontend
```

## Post-Deployment Checklist

- [ ] Git repository cloned successfully
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed and built
- [ ] Backend .env file configured with AWS credentials
- [ ] Backend service is running
- [ ] Frontend service is running
- [ ] Security group allows ports 3000 and 8000
- [ ] Can access frontend from browser
- [ ] Can access backend API from browser
- [ ] Frontend can communicate with backend
- [ ] Test diagram generation works

## Environment Variables

Make sure `/opt/diagram-generator/backend/.env` contains:

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
API_HOST=0.0.0.0
API_PORT=8000
OUTPUT_DIR=/opt/diagram-generator/output
```

## Notes

- Your EC2 instance uses **Amazon Linux 2023**
- User is **ec2-user**
- Package manager is **yum**
- All building happens **on EC2** (no local build required)
- Code is pulled from **Git repository**
