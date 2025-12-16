# EC2 Deployment Quick Reference

Quick command reference for deploying on EC2 Linux 3.

## Initial Setup (One-Time)

```bash
# 1. Connect to EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# 2. Run setup script
cd /tmp
curl -O https://raw.githubusercontent.com/satishdosapati/diagrams/main/deployment/ec2-setup-amazon-linux.sh
chmod +x ec2-setup-amazon-linux.sh
sudo bash ec2-setup-amazon-linux.sh

# 3. Clone repository
cd /opt/diagram-generator
git clone https://github.com/satishdosapati/diagrams.git .

# 4. Setup backend
bash deployment/setup-backend.sh

# 5. Configure .env (no AWS credentials needed - using IAM role)
cd backend
nano .env  # Add config (AWS_REGION, BEDROCK_MODEL_ID, etc.)
chmod 600 .env

# 6. Setup frontend
cd ../frontend
npm install
npm run build

# 7. Create systemd services
sudo cp deployment/systemd/diagram-api-amazon-linux.service /etc/systemd/system/diagram-api.service
sudo cp deployment/systemd/diagram-frontend-amazon-linux.service /etc/systemd/system/diagram-frontend.service

# 8. Start services
sudo systemctl daemon-reload
sudo systemctl enable diagram-api diagram-frontend
sudo systemctl start diagram-api diagram-frontend
```

## Daily Operations

```bash
# Check status
sudo systemctl status diagram-api diagram-frontend

# View logs
sudo journalctl -u diagram-api.service -f
sudo journalctl -u diagram-frontend.service -f

# Restart services
sudo systemctl restart diagram-api diagram-frontend

# Stop services
sudo systemctl stop diagram-api diagram-frontend

# Start services
sudo systemctl start diagram-api diagram-frontend
```

## Updates

```bash
cd /opt/diagram-generator
git pull origin main
bash deployment/deploy-git.sh
```

## Verify IAM Role

```bash
# Check if IAM role is attached
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Test AWS access (if AWS CLI installed)
aws sts get-caller-identity
```

## Troubleshooting

```bash
# Check Python version
python3.12 --version

# Recreate backend venv
cd /opt/diagram-generator/backend
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart diagram-api.service

# Rebuild frontend
cd /opt/diagram-generator/frontend
rm -rf node_modules dist
npm install
npm run build
sudo systemctl restart diagram-frontend.service

# Check ports
sudo netstat -tulpn | grep -E '8000|3000'

# Fix permissions
sudo chown -R ec2-user:ec2-user /opt/diagram-generator

# Verify IAM role (if AWS access issues)
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
aws sts get-caller-identity
```

## Environment Variables (.env)

**Note: AWS credentials are NOT needed - using EC2 instance IAM role**

```bash
# AWS Configuration (no credentials needed)
AWS_REGION=us-east-1

# Bedrock Model Configuration
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# Output Configuration
OUTPUT_DIR=./output

# Optional
EC2_PUBLIC_IP=your-ec2-ip
ENVIRONMENT=production
DEBUG=false
```

## IAM Role Setup

Before deployment, ensure EC2 instance has IAM role with Bedrock permissions:
- IAM Console → Roles → Create Role → EC2
- Attach policy: `AmazonBedrockFullAccess` (or custom policy)
- Attach role to EC2 instance: EC2 Console → Instance → Actions → Security → Modify IAM role

## Access URLs

- Frontend: `http://your-ec2-ip:3000`
- Backend: `http://your-ec2-ip:8000`
- API Docs: `http://your-ec2-ip:8000/docs`
