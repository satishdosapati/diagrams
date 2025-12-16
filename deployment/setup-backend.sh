#!/bin/bash
# Backend setup script - ensures Python 3.12 (or 3.10) is used
# Run this after cloning the repository

set -e

echo "Setting up backend with correct Python version..."

cd /opt/diagram-generator/backend

# Find Python 3.12 or 3.10 (skipping 3.11)
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD=python3.12
    echo "Using Python 3.12"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD=python3.10
    echo "Using Python 3.10"
else
    # Check default python3 version
    DEFAULT_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    MAJOR=$(echo $DEFAULT_VERSION | cut -d. -f1)
    MINOR=$(echo $DEFAULT_VERSION | cut -d. -f2)
    if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 10 ]; then
        PYTHON_CMD=python3
        echo "Using default Python $DEFAULT_VERSION"
    else
        echo "ERROR: Python 3.10+ is required. Current version: $DEFAULT_VERSION"
        echo "Please install Python 3.12 or 3.10 first:"
        echo "  sudo yum install -y python3.12 python3.12-pip python3.12-devel"
        exit 1
    fi
fi

# Remove existing venv if it was created with wrong Python version
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment with correct Python version
echo "Creating virtual environment with $PYTHON_CMD..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Verify Python version in venv
echo "Python version in venv: $(python --version)"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Deactivate
deactivate

echo ""
echo "Backend setup completed successfully!"
echo "Python version: $($PYTHON_CMD --version)"
echo ""
echo "Next steps:"
echo "1. Create .env file in backend/ directory (AWS_REGION, BEDROCK_MODEL_ID, etc.)"
echo "   Note: AWS credentials NOT needed - using EC2 instance IAM role"
echo "2. Set up systemd services"
echo "3. Start the services"
