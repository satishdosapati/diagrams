# Deployment Guide - EC2 Linux 3 (Amazon Linux 2023)

Complete guide for deploying the Architecture Diagram Generator on Amazon EC2 Linux 3 (Amazon Linux 2023).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Service Management](#service-management)
- [Monitoring & Health Checks](#monitoring--health-checks)
- [Rollback](#rollback)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### EC2 Instance Requirements

- **Instance Type**: t3.medium or larger (minimum 2 vCPU, 4GB RAM)
- **OS**: Amazon Linux 2023 (EC2 Linux 3)
- **Storage**: Minimum 20GB free space
- **Security Group**: Open ports:
  - `22` (SSH)
  - `8000` (Backend API)
  - `3000` (Frontend)

### AWS Credentials

Ensure your EC2 instance has IAM role or credentials configured for:
- AWS Bedrock access (for Strands Agents)
- S3 access (if using S3 for storage)

## Initial Setup

### Step 1: Connect to EC2 Instance

```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

### Step 2: Run Setup Script

The setup script installs all required dependencies:

```bash
# Download or clone the repository first
cd /opt
sudo git clone https://github.com/your-org/diagram-generator.git diagram-generator
cd diagram-generator/diagrams

# Run setup script
sudo bash deployment/ec2-setup-amazon-linux.sh
```

This script will:
- Update system packages
- Install Python 3.11+
- Install Node.js 20 LTS
- Install Graphviz and build dependencies
- Create application directories with proper permissions

### Step 3: Set Up Backend

```bash
cd /opt/diagram-generator/diagrams/backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Deactivate
deactivate
```

### Step 4: Set Up Frontend

```bash
cd /opt/diagram-generator/diagrams/frontend

# Install dependencies
npm install

# Build for production
npm run build
```

### Step 5: Configure Environment Variables

Create `.env` file in the backend directory:

```bash
cd /opt/diagram-generator/diagrams/backend
nano .env
```

Required environment variables:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Optional: MCP Diagram Server
USE_MCP_DIAGRAM_SERVER=false
MCP_DIAGRAM_SERVER_URL=http://localhost:8080

# Application Settings
LOG_LEVEL=INFO
OUTPUT_DIR=/opt/diagrams/output
SESSION_TTL=3600
```

Set proper permissions:

```bash
chmod 600 .env
```

### Step 6: Install Systemd Services

```bash
cd /opt/diagram-generator/diagrams
sudo bash deployment/install-services.sh
```

This will:
- Copy systemd service files to `/etc/systemd/system/`
- Enable services to start on boot
- Reload systemd daemon

### Step 7: Start Services

```bash
sudo systemctl start diagram-api diagram-frontend
```

Verify services are running:

```bash
sudo systemctl status diagram-api diagram-frontend
```

## Configuration

### Backend Configuration

The backend uses environment variables from `backend/.env`. Key settings:

- **AWS_REGION**: AWS region for Bedrock access
- **BEDROCK_MODEL_ID**: Anthropic Claude model ID
- **OUTPUT_DIR**: Directory for generated diagrams
- **SESSION_TTL**: Session expiration time in seconds (default: 3600)

### Frontend Configuration

The frontend is built as static files in `frontend/dist/`. The API endpoint is configured in `frontend/src/services/api.ts`.

### Systemd Service Configuration

Service files are located in `deployment/systemd/`:

- `diagram-api-amazon-linux.service`: Backend API service
- `diagram-frontend-amazon-linux.service`: Frontend service

Both services:
- Run as `ec2-user`
- Auto-restart on failure
- Include security hardening
- Have resource limits configured

## Deployment

### Quick Deploy (Git Pull Method)

For regular updates after initial setup:

```bash
cd /opt/diagram-generator/diagrams
bash deployment/deploy-git.sh [branch-name]
```

This script will:
1. Pull latest code from Git
2. Update backend dependencies
3. Rebuild frontend
4. Restart services
5. Perform health checks

### Manual Deployment

If you prefer manual control:

```bash
cd /opt/diagram-generator/diagrams

# Pull latest code
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Update frontend
cd ../frontend
npm install
npm run build

# Restart services
sudo systemctl restart diagram-api diagram-frontend
```

## Service Management

### Start Services

```bash
sudo systemctl start diagram-api diagram-frontend
```

### Stop Services

```bash
sudo systemctl stop diagram-api diagram-frontend
```

### Restart Services

```bash
sudo systemctl restart diagram-api diagram-frontend
```

### Check Status

```bash
sudo systemctl status diagram-api diagram-frontend
```

### View Logs

**Backend logs:**
```bash
# Follow logs
sudo journalctl -u diagram-api.service -f

# Last 100 lines
sudo journalctl -u diagram-api.service -n 100

# Logs since today
sudo journalctl -u diagram-api.service --since today
```

**Frontend logs:**
```bash
sudo journalctl -u diagram-frontend.service -f
```

### Enable Auto-Start on Boot

Services are automatically enabled during installation. To verify:

```bash
sudo systemctl is-enabled diagram-api diagram-frontend
```

## Monitoring & Health Checks

### Automated Health Check

Run the health check script:

```bash
bash deployment/health-check.sh
```

This checks:
- Service status
- HTTP endpoints (backend `/health`, frontend)
- Disk and memory usage
- Dependencies and builds

### Manual Health Checks

**Backend health endpoint:**
```bash
curl http://localhost:8000/health
```

**Frontend:**
```bash
curl http://localhost:3000
```

**Service status:**
```bash
sudo systemctl status diagram-api diagram-frontend
```

### Monitoring Recommendations

1. **Set up CloudWatch alarms** for:
   - CPU utilization > 80%
   - Memory utilization > 85%
   - Disk usage > 80%

2. **Monitor application logs**:
   ```bash
   # Set up log rotation
   sudo logrotate -d /etc/logrotate.d/diagrams
   ```

3. **Set up alerts** for service failures:
   ```bash
   # Example: Email alert on service failure
   # Configure in systemd service or use CloudWatch alarms
   ```

## Rollback

If a deployment causes issues, rollback to a previous version:

### List Available Backups

```bash
ls -lh /opt/diagram-generator-backups/
```

### Rollback to Previous Version

```bash
bash deployment/rollback.sh [backup-timestamp]
```

Example:
```bash
bash deployment/rollback.sh 20240101_120000
```

The rollback script will:
1. Stop services
2. Backup current state
3. Restore previous virtual environment
4. Restart services
5. Verify health

## Troubleshooting

### Service Won't Start

1. **Check service status:**
   ```bash
   sudo systemctl status diagram-api.service
   ```

2. **Check logs:**
   ```bash
   sudo journalctl -u diagram-api.service -n 50
   ```

3. **Common issues:**
   - Missing `.env` file: Create `backend/.env` with required variables
   - Port already in use: Check if another process is using port 8000/3000
   - Permission issues: Ensure `ec2-user` owns `/opt/diagram-generator`

### Backend Errors

**ModuleNotFoundError: No module named 'strands'**
```bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
pip install git+https://github.com/strands-agents/sdk-python.git
deactivate
sudo systemctl restart diagram-api
```

**Dependency conflicts:**
```bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --upgrade
deactivate
```

**Python version issues:**
```bash
# Verify Python version
python3.11 --version

# Recreate virtual environment if needed
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Errors

**Build fails:**
```bash
cd /opt/diagram-generator/diagrams/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Port 3000 already in use:**
```bash
# Find process using port 3000
sudo lsof -i :3000

# Kill process or change port in systemd service
```

### Performance Issues

**High memory usage:**
- Check service limits in systemd files
- Consider upgrading instance type
- Review diagram generation logs for memory leaks

**Slow response times:**
- Check AWS Bedrock API latency
- Review backend logs for slow queries
- Consider increasing uvicorn workers (edit systemd service)

### Network Issues

**Can't access from browser:**
1. Check security group rules (ports 8000, 3000)
2. Verify services are running: `sudo systemctl status diagram-api diagram-frontend`
3. Check firewall: `sudo firewall-cmd --list-all`

**CORS errors:**
- Verify CORS settings in `backend/main.py`
- Check frontend API endpoint configuration

### Logs Location

- **Systemd logs**: `journalctl -u diagram-api.service`
- **Application logs**: Check `backend/` directory for log files
- **Output files**: `/opt/diagram-generator/diagrams/output/`

## Security Best Practices

1. **Environment Variables**: Never commit `.env` files to Git
2. **File Permissions**: Keep `.env` files with `600` permissions
3. **Firewall**: Only open necessary ports in security groups
4. **Updates**: Regularly update system packages and dependencies
5. **Monitoring**: Set up CloudWatch alarms for suspicious activity
6. **Backups**: Regular backups of configuration and data

## Maintenance

### Regular Tasks

**Weekly:**
- Review logs for errors
- Check disk space
- Verify backups

**Monthly:**
- Update system packages: `sudo dnf update -y`
- Update application dependencies
- Review and rotate logs
- Test rollback procedure

**Quarterly:**
- Security audit
- Performance review
- Dependency vulnerability scan

### Backup Strategy

1. **Configuration backups**: Back up `.env` files securely
2. **Code backups**: Git repository serves as code backup
3. **Virtual environment backups**: Created automatically during deployment
4. **Output backups**: Consider backing up `/opt/diagram-generator/diagrams/output/` to S3

## Support

For issues or questions:
1. Check logs first: `sudo journalctl -u diagram-api.service -f`
2. Run health check: `bash deployment/health-check.sh`
3. Review this documentation
4. Check GitHub issues
