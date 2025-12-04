# EC2 Deployment Instructions

## Prerequisites

- AWS EC2 instance running (you have: Amazon Linux 2023)
- Public IP address (your IP: 100.31.143.57)
- SSH access with PEM key
- Security group configured:
  - Port 22 (SSH)
  - Port 3000 (Frontend)
  - Port 8000 (Backend API)
- AWS credentials configured on EC2 (for Bedrock access)

## Step-by-Step Deployment

### Step 1: Prepare EC2 Instance

SSH into your EC2 instance:

```bash
ssh -i satishmcp.pem ec2-user@100.31.143.57
```

### Step 2: Install Dependencies on EC2

**For Amazon Linux 2023** (your instance):

```bash
# Update system
sudo yum update -y

# Install Python 3.11
sudo yum install -y python3.11 python3.11-pip python3.11-devel

# Install Node.js 20
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs

# Install Graphviz (required for diagrams library)
sudo yum install -y graphviz

# Install other dependencies
sudo yum install -y git curl gcc gcc-c++ make

# Create application directory
sudo mkdir -p /opt/diagram-generator
sudo mkdir -p /opt/diagram-generator/output
sudo chown -R ec2-user:ec2-user /opt/diagram-generator
```

### Step 3: Configure AWS Credentials

On EC2, configure AWS credentials for Bedrock access:

```bash
# Option 1: Using AWS CLI
aws configure

# Option 2: Set environment variables (in .env file)
# We'll create this in Step 5
```

### Step 4: Deploy Application from Local Machine

From your **local machine** (Windows PowerShell), run:

```powershell
# Set environment variables
$env:EC2_HOST="100.31.143.57"
$env:EC2_USER="ec2-user"

# Navigate to project root
cd C:\Users\usdoss02\Satish-Playground\diagrams

# Build frontend first
cd frontend
npm install
npm run build
cd ..

# Copy files to EC2 (you'll need rsync or use SCP)
# If you don't have rsync on Windows, use the manual method below
```

**Alternative: Manual Deployment (if rsync not available)**

If you don't have rsync on Windows, use SCP or manually copy files:

```powershell
# Copy backend
scp -i satishmcp.pem -r backend/* ec2-user@100.31.143.57:/opt/diagram-generator/backend/

# Copy frontend build
scp -i satishmcp.pem -r frontend/dist/* ec2-user@100.31.143.57:/opt/diagram-generator/frontend/dist/

# Copy deployment scripts
scp -i satishmcp.pem -r deployment/* ec2-user@100.31.143.57:/opt/diagram-generator/deployment/
```

### Step 5: Setup Backend on EC2

SSH back into EC2 and run:

```bash
# Navigate to backend directory
cd /opt/diagram-generator/backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
API_HOST=0.0.0.0
API_PORT=8000
OUTPUT_DIR=/opt/diagram-generator/output
EOF

# Edit .env with your actual AWS credentials
nano .env  # or use vi

# Deactivate virtual environment
deactivate
```

### Step 6: Setup Frontend on EC2

```bash
cd /opt/diagram-generator/frontend

# Install dependencies
npm install

# Note: Frontend is already built, but if you need to rebuild:
# npm run build
```

### Step 7: Create systemd Service Files

Create the service files manually (since we need to adjust for ec2-user):

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

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable diagram-api.service
sudo systemctl enable diagram-frontend.service

# Start services
sudo systemctl start diagram-api.service
sudo systemctl start diagram-frontend.service
```

### Step 8: Configure Security Group

In AWS Console:
1. Go to EC2 → Security Groups
2. Select your instance's security group
3. Add inbound rules:
   - Type: Custom TCP, Port: 3000, Source: 0.0.0.0/0 (or your IP)
   - Type: Custom TCP, Port: 8000, Source: 0.0.0.0/0 (or your IP)
   - Type: SSH, Port: 22, Source: Your IP

### Step 9: Verify Deployment

```bash
# Check service status
sudo systemctl status diagram-api.service
sudo systemctl status diagram-frontend.service

# Check logs
sudo journalctl -u diagram-api.service -f
sudo journalctl -u diagram-frontend.service -f

# Test backend
curl http://localhost:8000/health

# Test frontend (from EC2)
curl http://localhost:3000
```

### Step 10: Access Application

From your browser:
- **Frontend**: http://100.31.143.57:3000
- **Backend API**: http://100.31.143.57:8000/api/health

## Troubleshooting

### Service Not Starting

```bash
# Check service status
sudo systemctl status diagram-api.service

# Check logs
sudo journalctl -u diagram-api.service -n 50

# Check if port is in use
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :3000
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R ec2-user:ec2-user /opt/diagram-generator

# Check file permissions
ls -la /opt/diagram-generator/backend/
```

### AWS Credentials Issues

```bash
# Test AWS credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

### Frontend Can't Connect to Backend

Update frontend API URL:

```bash
# On EC2, edit frontend dist files or rebuild with correct API URL
# Or set environment variable
export VITE_API_URL=http://100.31.143.57:8000
```

## Quick Reference Commands

```bash
# Restart services
sudo systemctl restart diagram-api.service
sudo systemctl restart diagram-frontend.service

# Stop services
sudo systemctl stop diagram-api.service
sudo systemctl stop diagram-frontend.service

# View logs
sudo journalctl -u diagram-api.service -f
sudo journalctl -u diagram-frontend.service -f

# Check if services are running
sudo systemctl is-active diagram-api diagram-frontend
```

## Post-Deployment Checklist

- [ ] Backend service is running
- [ ] Frontend service is running
- [ ] Security group allows ports 3000 and 8000
- [ ] AWS credentials configured
- [ ] Bedrock model access enabled
- [ ] Can access frontend from browser
- [ ] Can access backend API from browser
- [ ] Frontend can communicate with backend

## Notes

- Your EC2 instance uses **Amazon Linux 2023** (not Ubuntu)
- User is **ec2-user** (not ubuntu)
- Package manager is **yum** (not apt-get)
- Python 3.11 may need to be installed from source or use python3.9+ if available

