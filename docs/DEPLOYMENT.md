# Deployment Guide

## EC2 Deployment

### Prerequisites

- AWS EC2 instance (Ubuntu 22.04 LTS)
- Public IP address
- Security group configured (ports 3000, 8000, 22)
- AWS credentials configured on EC2

### Step 1: Initial Setup

SSH into your EC2 instance and run the setup script:

```bash
sudo bash deployment/ec2-setup.sh
```

This installs:
- Python 3.11
- Node.js 20
- Graphviz
- System dependencies

### Step 2: Configure Environment

Create `.env` file in `backend/`:

```bash
cd /opt/diagram-generator/backend
cp .env.example .env
# Edit .env with your AWS credentials
```

### Step 3: Deploy Application

From your local machine:

```bash
export EC2_HOST=your-ec2-public-ip
export EC2_USER=ubuntu
bash deployment/deploy.sh
```

### Step 4: Verify Deployment

- Frontend: http://your-ec2-ip:3000
- Backend API: http://your-ec2-ip:8000/api/health

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

