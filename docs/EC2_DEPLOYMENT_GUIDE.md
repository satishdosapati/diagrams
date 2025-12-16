# EC2 Linux 3 Deployment Guide

Complete step-by-step guide for deploying the Architecture Diagram Generator on Amazon Linux 2023 (EC2 Linux 3).

## Prerequisites

- EC2 instance running Amazon Linux 2023
- Security group configured with ports:
  - **22** (SSH)
  - **8000** (Backend API)
  - **3000** (Frontend)
- **IAM Role attached to EC2 instance** with Bedrock access permissions
- SSH access to the instance

### Setting Up IAM Role for EC2 Instance

**Before starting deployment, ensure your EC2 instance has an IAM role with the following permissions:**

1. **Create IAM Role** (if not already created):
   - Go to IAM Console → Roles → Create Role
   - Select "AWS service" → "EC2"
   - Attach policies:
     - `AmazonBedrockFullAccess` (or custom policy with Bedrock invoke permissions)
     - Or create custom policy with minimum required permissions:
       ```json
       {
         "Version": "2012-10-17",
         "Statement": [
           {
             "Effect": "Allow",
             "Action": [
               "bedrock:InvokeModel",
               "bedrock:InvokeModelWithResponseStream"
             ],
             "Resource": "arn:aws:bedrock:*::foundation-model/*"
           }
         ]
       }
       ```

2. **Attach Role to EC2 Instance**:
   - Go to EC2 Console → Select your instance → Actions → Security → Modify IAM role
   - Select the IAM role you created
   - Click "Update IAM role"

3. **Verify Role Attachment**:
   ```bash
   # On EC2 instance, verify role is attached
   curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
   ```
   This should return your role name.

---

## Step 1: Connect to EC2 Instance

```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

---

## Step 2: Initial System Setup

Run the automated setup script to install all required dependencies:

```bash
# Download the setup script
cd /tmp
curl -O https://raw.githubusercontent.com/satishdosapati/diagrams/main/deployment/ec2-setup-amazon-linux.sh

# Make it executable
chmod +x ec2-setup-amazon-linux.sh

# Run the setup script
sudo bash ec2-setup-amazon-linux.sh
```

**What this script does:**
- Updates system packages
- Installs Python 3.12 (or falls back to 3.10)
- Installs Node.js 20+
- Installs Graphviz (required for diagrams library)
- Installs build tools (git, gcc, gcc-c++, make)
- Creates application directory at `/opt/diagram-generator`

**Expected output:**
```
Python version: Python 3.12.x
Node.js version: v20.x.x
Graphviz version: dot - graphviz version x.x.x
```

---

## Step 3: Clone the Repository

```bash
# Navigate to application directory
cd /opt/diagram-generator

# Clone the repository
git clone https://github.com/satishdosapati/diagrams.git .

# Verify files are cloned
ls -la
```

---

## Step 4: Backend Setup

### Option A: Use Automated Script

```bash
cd /opt/diagram-generator
bash deployment/setup-backend.sh
```

### Option B: Manual Setup

```bash
cd /opt/diagram-generator/backend

# Remove existing venv if present
rm -rf venv

# Create virtual environment with Python 3.12
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify Python version (should show 3.12.x)
python --version

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Deactivate
deactivate
```

**Expected output:**
```
Python version in venv: Python 3.12.x
Successfully installed [packages...]
```

---

## Step 5: Configure Backend Environment Variables

Create the `.env` file with your configuration. **Note: AWS credentials are not needed as we're using EC2 instance role.**

```bash
cd /opt/diagram-generator/backend
nano .env
```

**Add the following configuration:**

```bash
# AWS Configuration
# Note: AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) are NOT needed
# The application will use the EC2 instance IAM role automatically
AWS_REGION=us-east-1

# Bedrock Model Configuration
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# Output Configuration
OUTPUT_DIR=./output

# Optional: EC2 Public IP (for CORS)
EC2_PUBLIC_IP=your-ec2-public-ip

# Optional: Frontend URL (if using custom domain)
# FRONTEND_URL=http://your-domain.com:3000

# Optional: Environment
ENVIRONMENT=production

# Optional: Debug mode (set to false for production)
DEBUG=false

# Optional: Use MCP Diagram Server
USE_MCP_DIAGRAM_SERVER=false
```

**Save and exit:**
- Press `Ctrl+X`
- Press `Y` to confirm
- Press `Enter` to save

**Set proper permissions:**
```bash
chmod 600 .env
```

**Verify IAM Role:**
```bash
# Test that the instance can access AWS services using the role
aws sts get-caller-identity

# If AWS CLI is not installed, you can verify role attachment:
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

**Important:** The application will automatically use the EC2 instance IAM role for AWS API calls. No AWS credentials need to be stored in the `.env` file.

---

## Step 6: Frontend Setup

```bash
cd /opt/diagram-generator/frontend

# Install dependencies
npm install

# Build for production
npm run build
```

**Expected output:**
```
> diagrams@x.x.x build
> vite build

✓ built in XXs
```

---

## Step 7: Create Systemd Services

### Backend Service

```bash
sudo nano /etc/systemd/system/diagram-api.service
```

**Paste the following:**

```ini
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
```

**Save and exit** (Ctrl+X, Y, Enter)

### Frontend Service

```bash
sudo nano /etc/systemd/system/diagram-frontend.service
```

**Paste the following:**

```ini
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
```

**Save and exit** (Ctrl+X, Y, Enter)

---

## Step 8: Start Services

```bash
# Reload systemd to recognize new services
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable diagram-api.service
sudo systemctl enable diagram-frontend.service

# Start services
sudo systemctl start diagram-api.service
sudo systemctl start diagram-frontend.service

# Check status
sudo systemctl status diagram-api.service
sudo systemctl status diagram-frontend.service
```

**Expected output:**
```
● diagram-api.service - Architecture Diagram Generator API
   Loaded: loaded (/etc/systemd/system/diagram-api.service; enabled)
   Active: active (running) since [timestamp]
```

---

## Step 9: Verify Deployment

### Check Service Status

```bash
# Check both services
sudo systemctl status diagram-api diagram-frontend

# View logs
sudo journalctl -u diagram-api.service -f
sudo journalctl -u diagram-frontend.service -f
```

### Test Endpoints

From your local machine or browser:

- **Frontend:** `http://your-ec2-ip:3000`
- **Backend API:** `http://your-ec2-ip:8000`
- **API Documentation:** `http://your-ec2-ip:8000/docs`
- **Health Check:** `http://your-ec2-ip:8000/health`

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## Step 10: Firewall Configuration (if needed)

If using `firewalld`, configure ports:

```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

---

## Troubleshooting

### Service Not Starting

```bash
# Check service status
sudo systemctl status diagram-api.service

# View detailed logs
sudo journalctl -u diagram-api.service -n 50

# Check if port is in use
sudo netstat -tulpn | grep -E '8000|3000'
```

### Backend Errors

**ModuleNotFoundError:**
```bash
cd /opt/diagram-generator/backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart diagram-api.service
```

**AWS Credentials Error:**
- Verify IAM role is attached to EC2 instance:
  ```bash
  curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
  ```
- Ensure IAM role has Bedrock permissions
- Verify AWS region is set correctly in `.env` file
- Test AWS access:
  ```bash
  aws sts get-caller-identity
  ```

**Python Version Error:**
```bash
# Verify Python version
python3.12 --version

# Recreate venv if needed
cd /opt/diagram-generator/backend
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### Frontend Errors

**Build Failures:**
```bash
# Check Node.js version (should be 20+)
node --version

# Reinstall dependencies
cd /opt/diagram-generator/frontend
rm -rf node_modules
npm install
npm run build
```

**Port Conflicts:**
```bash
# Check what's using port 3000
sudo lsof -i :3000

# Kill process if needed
sudo kill -9 <PID>
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R ec2-user:ec2-user /opt/diagram-generator

# Fix permissions
chmod 600 /opt/diagram-generator/backend/.env
```

---

## Updating the Application

### Quick Update (using deploy script)

```bash
cd /opt/diagram-generator
git pull origin main
bash deployment/deploy-git.sh
```

### Manual Update

```bash
cd /opt/diagram-generator

# Pull latest code
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart diagram-api.service

# Update frontend
cd ../frontend
npm install
npm run build
sudo systemctl restart diagram-frontend.service
```

---

## Useful Commands

### Service Management

```bash
# View logs
sudo journalctl -u diagram-api.service -f
sudo journalctl -u diagram-frontend.service -f

# Restart services
sudo systemctl restart diagram-api diagram-frontend

# Stop services
sudo systemctl stop diagram-api diagram-frontend

# Start services
sudo systemctl start diagram-api diagram-frontend

# Check status
sudo systemctl status diagram-api diagram-frontend

# Disable auto-start on boot
sudo systemctl disable diagram-api diagram-frontend
```

### Monitoring

```bash
# Check service status
sudo systemctl status diagram-api diagram-frontend

# View recent logs
sudo journalctl -u diagram-api.service --since "10 minutes ago"
sudo journalctl -u diagram-frontend.service --since "10 minutes ago"

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep -E 'uvicorn|node'
```

---

## Security Recommendations

1. **✅ Use IAM Roles** - Already configured! No AWS credentials stored in `.env` file
2. **Restrict Security Group** to specific IPs if possible
3. **Set up HTTPS** with reverse proxy (nginx/Apache) for production
4. **Enable AWS CloudWatch** for logging and monitoring
5. **Set DEBUG=false** in production `.env` file
6. **Regularly update dependencies** and system packages
7. **Use least privilege IAM policies** - Only grant necessary Bedrock permissions
8. **Rotate IAM role credentials** - AWS automatically rotates instance role credentials

---

## Access URLs

After successful deployment:

- **Frontend:** `http://your-ec2-public-ip:3000`
- **Backend API:** `http://your-ec2-public-ip:8000`
- **API Documentation:** `http://your-ec2-public-ip:8000/docs`
- **ReDoc:** `http://your-ec2-public-ip:8000/redoc`

---

## Next Steps

1. Configure custom domain (optional)
2. Set up SSL/TLS certificates
3. Configure reverse proxy (nginx/Apache)
4. Set up monitoring and alerting
5. Configure automated backups
6. Set up CI/CD pipeline for deployments

---

## Support

For issues or questions:
- Check logs: `sudo journalctl -u diagram-api.service -f`
- Review API docs: `http://your-ec2-ip:8000/docs`
- Check GitHub issues: https://github.com/satishdosapati/diagrams/issues
