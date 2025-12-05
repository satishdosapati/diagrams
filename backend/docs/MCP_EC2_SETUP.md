# Enabling AWS Diagram MCP Server on EC2 Amazon Linux 2023

This guide provides step-by-step instructions to enable AWS Diagram MCP Server on your EC2 instance running Amazon Linux 2023.

## Prerequisites

- EC2 instance running Amazon Linux 2023
- Application already deployed to `/opt/diagram-generator/diagrams`
- Python 3.11 virtual environment already set up
- SSH access to EC2 instance

## Step-by-Step Instructions

### Step 1: SSH into EC2 Instance

```bash
# Replace <YOUR_EC2_PUBLIC_IP> with your actual EC2 public IP
ssh -i satishmcp.pem ec2-user@<YOUR_EC2_PUBLIC_IP>
```

### Step 2: Navigate to Application Directory

```bash
cd /opt/diagram-generator/diagrams/backend
```

### Step 3: Install uv Package Manager (if not already installed)

```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for current session
export PATH="$HOME/.cargo/bin:$PATH"

# Verify uv installation
uv --version

# Add to ~/.bashrc for persistence (optional)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Note**: If you prefer not to install uv globally, you can use `uvx` (on-demand) instead, which doesn't require installation.

### Step 4: Verify Prerequisites

```bash
# Check Python version (should be 3.11)
python3.11 --version

# Check GraphViz (required for diagrams)
dot -V

# If GraphViz is not installed:
sudo dnf install -y graphviz
```

### Step 5: Install AWS Diagram MCP Server

#### Option A: Using uv (Recommended - Faster)

```bash
# Make sure uv is in PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Install MCP server using uv
uv tool install awslabs.aws-diagram-mcp-server

# Verify installation
uv tool run awslabs.aws-diagram-mcp-server --help
```

#### Option B: Using Installation Script

```bash
# Navigate to backend directory
cd /opt/diagram-generator/diagrams/backend

# Make script executable
chmod +x scripts/install_mcp_server.sh

# Run installation script
./scripts/install_mcp_server.sh
```

#### Option C: Using uvx (On-Demand - No Installation Required)

If you don't want to install uv globally, you can use `uvx` which downloads on-demand:

```bash
# Test uvx (will download on first use)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
uvx awslabs.aws-diagram-mcp-server --help
```

### Step 6: Configure Environment Variables

#### Option A: Add to Backend .env File (Recommended)

```bash
cd /opt/diagram-generator/diagrams/backend

# Edit .env file
nano .env

# Add these lines:
USE_MCP_DIAGRAM_SERVER=true
MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"

# Or if using uvx:
# MCP_DIAGRAM_SERVER_COMMAND="uvx awslabs.aws-diagram-mcp-server"

# Save and exit (Ctrl+X, then Y, then Enter)
```

**Note**: The `.env` file is automatically loaded by the application when you start it.

#### Option B: Export Before Starting Service (For Manual Start)

If you're starting the service manually, export environment variables before starting:

```bash
cd /opt/diagram-generator/diagrams/backend

# Activate virtual environment
source venv/bin/activate

# Export environment variables
export USE_MCP_DIAGRAM_SERVER=true
export MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"
export PATH="$HOME/.cargo/bin:$PATH"

# Or if using uvx:
# export MCP_DIAGRAM_SERVER_COMMAND="uvx awslabs.aws-diagram-mcp-server"

# Start backend service
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Option C: Create Startup Script (Recommended for Manual Services)

Create a startup script that sets environment variables:

```bash
cd /opt/diagram-generator/diagrams/backend

# Create startup script
cat > start_backend.sh << 'EOF'
#!/bin/bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
export PATH="$HOME/.cargo/bin:$PATH"
export USE_MCP_DIAGRAM_SERVER=true
export MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"
uvicorn main:app --host 0.0.0.0 --port 8000
EOF

# Make executable
chmod +x start_backend.sh

# Run it
./start_backend.sh
```

### Step 8: Verify MCP Server Installation

```bash
# Test MCP server directly
uv tool run awslabs.aws-diagram-mcp-server --help

# Or if using uvx:
uvx awslabs.aws-diagram-mcp-server --help

# Should see help output without errors
```

### Step 9: Test Integration

#### Test 1: Check Logs for MCP Initialization

When you start the backend service, watch the console output for:

```bash
# Start backend (if not already running)
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
export PATH="$HOME/.cargo/bin:$PATH"
export USE_MCP_DIAGRAM_SERVER=true
export MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"
uvicorn main:app --host 0.0.0.0 --port 8000

# Look for these log messages in the console:
# [MCP] MCPDiagramClient initialized
# [MCP] Enabled: True
# [MCP] Server command: uv tool run awslabs.aws-diagram-mcp-server
# [DIAGRAM_AGENT] MCP tools enabled: True
```

#### Test 2: Generate a Test Diagram

```bash
# Activate virtual environment
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate

# Set environment variables
export USE_MCP_DIAGRAM_SERVER=true
export MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"

# Test Python import
python -c "from src.integrations.mcp_diagram_client import get_mcp_client; client = get_mcp_client(); print(f'MCP Enabled: {client.enabled}')"

# Should output: MCP Enabled: True
```

#### Test 3: Make API Request

```bash
# From your local machine or EC2
curl -X POST http://<EC2_IP>:8000/generate-diagram \
  -H "Content-Type: application/json" \
  -d '{
    "description": "API Gateway with Lambda and DynamoDB",
    "provider": "aws"
  }'

# Check logs for MCP activity:
# [DIAGRAM_AGENT] === MCP Post-processing ===
# [MCP] === Calling validate_code ===
# [MCP] === Calling generate_diagram tool ===
```

### Step 10: Restart Application Service

Since you're running services manually, restart by:

```bash
# Stop the current backend process (Ctrl+C if running in foreground)
# Or find and kill the process:
ps aux | grep uvicorn
kill <process_id>

# Restart with MCP enabled
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
export PATH="$HOME/.cargo/bin:$PATH"
export USE_MCP_DIAGRAM_SERVER=true
export MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"

# Start backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Or use the startup script if you created one:
./start_backend.sh
```

**Note**: If running in background, use `nohup` or `screen`/`tmux`:

```bash
# Using nohup
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

# Using screen (install first: sudo dnf install screen)
screen -S backend
# Then start uvicorn, press Ctrl+A then D to detach
# Reattach: screen -r backend

# Using tmux (install first: sudo dnf install tmux)
tmux new -s backend
# Then start uvicorn, press Ctrl+B then D to detach
# Reattach: tmux attach -t backend
```

## Verification Checklist

After completing the steps above, verify:

- [ ] `uv --version` shows uv is installed
- [ ] `uv tool run awslabs.aws-diagram-mcp-server --help` works
- [ ] `USE_MCP_DIAGRAM_SERVER=true` is set in environment
- [ ] `MCP_DIAGRAM_SERVER_COMMAND` is set correctly
- [ ] Application logs show `[MCP] MCPDiagramClient initialized`
- [ ] Application logs show `[MCP] Enabled: True`
- [ ] Diagram generation includes MCP post-processing logs

## Troubleshooting

### Issue: uv command not found

**Solution:**
```bash
# Add uv to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Or use full path
~/.cargo/bin/uv tool run awslabs.aws-diagram-mcp-server --help
```

### Issue: MCP server not found when starting service

**Solution:**
```bash
# Ensure PATH includes uv location before starting service
export PATH="$HOME/.cargo/bin:$PATH"

# Verify uv is accessible
which uv
uv --version

# Then start your service with PATH exported
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
export PATH="$HOME/.cargo/bin:$PATH"
export USE_MCP_DIAGRAM_SERVER=true
export MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Issue: Permission denied when running uv

**Solution:**
```bash
# Install uv for user (not system-wide)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure ~/.cargo/bin is in PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

### Issue: MCP enabled but no logs

**Check:**
1. Environment variable is set: `echo $USE_MCP_DIAGRAM_SERVER`
2. Application is reading .env file correctly
3. Logs are at correct level (check logging configuration)

### Issue: GraphViz not found

**Solution:**
```bash
sudo dnf install -y graphviz
dot -V  # Verify installation
```

## Quick Reference Commands

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Install MCP server
uv tool install awslabs.aws-diagram-mcp-server

# Enable MCP
export USE_MCP_DIAGRAM_SERVER=true
export MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"

# Test MCP server
uv tool run awslabs.aws-diagram-mcp-server --help

# Check logs
sudo journalctl -u diagram-api.service -f | grep MCP
```

## Next Steps

After enabling MCP:

1. Monitor logs for MCP activity during diagram generation
2. Test with various diagram types (AWS, Azure, GCP)
3. Verify MCP post-processing is working (check logs)
4. Consider performance improvements from MCP validation/enhancement

## Notes

- **uvx vs uv tool**: `uvx` downloads on-demand (slower first call), `uv tool install` installs locally (faster)
- **PATH**: Ensure uv location (`~/.cargo/bin`) is in PATH when starting services manually
- **Environment Variables**: Add to `.env` file for automatic loading, or export before starting service
- **Python Version**: MCP server requires Python 3.10+, you have 3.11 which is perfect
- **GraphViz**: Required for diagram generation, ensure it's installed
- **Running in Background**: Use `nohup`, `screen`, or `tmux` to keep services running after SSH disconnect

