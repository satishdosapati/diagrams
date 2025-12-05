# MCP Integration Troubleshooting

## Issue: MCP Log Messages Not Appearing

If you don't see these log messages when starting the backend:
```
[MCP] MCPDiagramClient initialized
[MCP] Enabled: True
[DIAGRAM_AGENT] MCP tools enabled: True
```

### Solution Steps

#### 1. Verify .env File Exists and Contains MCP Settings

```bash
cd /opt/diagram-generator/diagrams/backend

# Check if .env file exists
ls -la .env

# View .env file contents
cat .env

# Should contain:
# USE_MCP_DIAGRAM_SERVER=true
# MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"
```

#### 2. Verify Environment Variable is Set

```bash
# Check environment variable
echo $USE_MCP_DIAGRAM_SERVER

# Should output: true

# If not set, add to .env file:
nano .env
# Add: USE_MCP_DIAGRAM_SERVER=true
```

#### 3. Check Application Startup Logs

When you start the backend, you should see:

```bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

Look for these messages at startup:
```
Environment loaded. USE_MCP_DIAGRAM_SERVER=true
[MCP] MCPDiagramClient initialized
[MCP] Enabled: True
[MCP] Server command: uv tool run awslabs.aws-diagram-mcp-server
[DIAGRAM_AGENT] MCP tools enabled: True
```

#### 4. Test MCP Client Directly

```bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate

# Set environment variable
export USE_MCP_DIAGRAM_SERVER=true

# Test Python import
python -c "
from src.integrations.mcp_diagram_client import get_mcp_client
import logging
logging.basicConfig(level=logging.INFO)
client = get_mcp_client()
print(f'MCP Enabled: {client.enabled}')
print(f'MCP Server Command: {client.server_command}')
"
```

Should output:
```
[MCP] MCPDiagramClient initialized
[MCP] Enabled: True
[MCP] Server command: uvx awslabs.aws-diagram-mcp-server
MCP Enabled: True
MCP Server Command: uvx awslabs.aws-diagram-mcp-server
```

#### 5. Verify .env File is Being Loaded

The application now loads `.env` file automatically. Check startup logs for:
```
Environment loaded. USE_MCP_DIAGRAM_SERVER=true
```

If you see `USE_MCP_DIAGRAM_SERVER=not set`, the .env file is not being loaded correctly.

#### 6. Check Logging Level

If logs are not appearing, check if logging level is set correctly:

```bash
# When starting uvicorn, you can set log level:
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info

# Or check uvicorn logs:
uvicorn main:app --host 0.0.0.0 --port 8000 2>&1 | grep MCP
```

## Common Issues

### Issue: .env file not found

**Solution:**
```bash
cd /opt/diagram-generator/diagrams/backend

# Create .env file if it doesn't exist
touch .env

# Add MCP settings
echo "USE_MCP_DIAGRAM_SERVER=true" >> .env
echo 'MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"' >> .env
```

### Issue: Environment variable not being read

**Solution:**
```bash
# Verify .env file location
cd /opt/diagram-generator/diagrams/backend
pwd  # Should be: /opt/diagram-generator/diagrams/backend
ls -la .env  # Should exist

# Check file permissions
chmod 644 .env

# Restart backend service
```

### Issue: Logs appear but MCP is disabled

**Check:**
1. Value in .env file must be exactly `true` (lowercase)
2. No extra spaces: `USE_MCP_DIAGRAM_SERVER=true` (not `USE_MCP_DIAGRAM_SERVER = true`)
3. No quotes around value: `USE_MCP_DIAGRAM_SERVER=true` (not `USE_MCP_DIAGRAM_SERVER="true"`)

### Issue: MCP logs appear but post-processing doesn't run

**Check:**
1. MCP post-processing only runs for AWS provider diagrams
2. Check logs during diagram generation for: `[DIAGRAM_AGENT] === MCP Post-processing ===`
3. Verify provider is set to "aws" in the request

## Verification Commands

```bash
# 1. Check .env file
cat /opt/diagram-generator/diagrams/backend/.env | grep MCP

# 2. Test environment variable loading
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(f'USE_MCP_DIAGRAM_SERVER={os.getenv(\"USE_MCP_DIAGRAM_SERVER\")}')"

# 3. Test MCP client initialization
python -c "
import logging
logging.basicConfig(level=logging.INFO)
from src.integrations.mcp_diagram_client import get_mcp_client
client = get_mcp_client()
print(f'Enabled: {client.enabled}')
"

# 4. Check startup logs
uvicorn main:app --host 0.0.0.0 --port 8000 2>&1 | head -20
```

## Expected Behavior

When MCP is properly enabled:

1. **At startup**, you should see:
   ```
   Environment loaded. USE_MCP_DIAGRAM_SERVER=true
   [MCP] MCPDiagramClient initialized
   [MCP] Enabled: True
   [DIAGRAM_AGENT] MCP tools enabled: True
   ```

2. **During diagram generation** (for AWS diagrams), you should see:
   ```
   [DIAGRAM_AGENT] === MCP Post-processing ===
   [MCP] === Calling validate_code ===
   [MCP] === Calling generate_diagram tool ===
   [DIAGRAM_AGENT] MCP code validation: PASSED
   ```

If you don't see these logs, follow the troubleshooting steps above.
