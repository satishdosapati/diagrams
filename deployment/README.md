# Deployment Scripts

This directory contains all scripts and configuration files for deploying the Architecture Diagram Generator on EC2 Linux 3 (Amazon Linux 2023).

## Scripts Overview

### Setup Scripts

- **`ec2-setup-amazon-linux.sh`**: Initial EC2 instance setup
  - Installs Python 3.11+, Node.js 20+, Graphviz, and dependencies
  - Creates application directories
  - Run once per EC2 instance: `sudo bash ec2-setup-amazon-linux.sh`

- **`install-services.sh`**: Install systemd services
  - Copies service files to `/etc/systemd/system/`
  - Enables services for auto-start
  - Run once after initial setup: `sudo bash install-services.sh`

### Deployment Scripts

- **`deploy-git.sh`**: Automated deployment via Git pull
  - Pulls latest code from Git
  - Updates dependencies
  - Rebuilds frontend
  - Restarts services with health checks
  - Run for regular updates: `bash deploy-git.sh [branch-name]`

### Maintenance Scripts

- **`health-check.sh`**: Comprehensive health check
  - Checks service status
  - Verifies HTTP endpoints
  - Monitors disk/memory usage
  - Validates dependencies
  - Run anytime: `bash health-check.sh`

- **`rollback.sh`**: Rollback to previous deployment
  - Lists available backups
  - Restores previous virtual environment
  - Restarts services
  - Run when needed: `bash rollback.sh [backup-timestamp]`

## Systemd Services

### Service Files

Located in `systemd/` directory:

- **`diagram-api-amazon-linux.service`**: Backend API service
  - Runs FastAPI application on port 8000
  - Auto-restarts on failure
  - Includes security hardening

- **`diagram-frontend-amazon-linux.service`**: Frontend service
  - Serves built React application on port 3000
  - Auto-restarts on failure
  - Includes security hardening

### Service Management

```bash
# Start services
sudo systemctl start diagram-api diagram-frontend

# Stop services
sudo systemctl stop diagram-api diagram-frontend

# Restart services
sudo systemctl restart diagram-api diagram-frontend

# Check status
sudo systemctl status diagram-api diagram-frontend

# View logs
sudo journalctl -u diagram-api.service -f
sudo journalctl -u diagram-frontend.service -f
```

## Quick Reference

### First-Time Setup

```bash
# 1. Run setup script
sudo bash ec2-setup-amazon-linux.sh

# 2. Clone repository
cd /opt
sudo git clone <your-repo-url> diagram-generator
cd diagram-generator/diagrams

# 3. Setup backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# 4. Setup frontend
cd ../frontend
npm install
npm run build

# 5. Configure environment
cd ../backend
nano .env  # Add AWS credentials

# 6. Install services
cd ..
sudo bash install-services.sh

# 7. Start services
sudo systemctl start diagram-api diagram-frontend
```

### Regular Updates

```bash
cd /opt/diagram-generator/diagrams
bash deploy-git.sh
```

### Health Check

```bash
bash health-check.sh
```

### Rollback

```bash
# List backups
ls -lh /opt/diagram-generator-backups/

# Rollback
bash rollback.sh 20240101_120000
```

## File Permissions

Make scripts executable on Linux:

```bash
chmod +x deployment/*.sh
```

## Troubleshooting

See [Deployment Guide](../docs/DEPLOYMENT.md) for detailed troubleshooting steps.

Common issues:
- **Services won't start**: Check logs with `sudo journalctl -u diagram-api.service -n 50`
- **Permission errors**: Ensure `ec2-user` owns `/opt/diagram-generator`
- **Port conflicts**: Check if ports 8000/3000 are in use
- **Missing dependencies**: Re-run setup script or install manually

## Backup Locations

- **Backend backups**: `/opt/diagram-generator-backups/backend-backup-*.tar.gz`
- **Configuration**: Back up `backend/.env` files securely
- **Output files**: `/opt/diagram-generator/diagrams/output/`
