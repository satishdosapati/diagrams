# MCP Server Implementation Summary

## What Was Implemented

A **full MCP (Model Context Protocol) client** that communicates with AWS Diagram MCP Server using JSON-RPC 2.0 over stdio.

## Key Features

### 1. JSON-RPC 2.0 Protocol Implementation
- ✅ Proper MCP initialization handshake
- ✅ Tool calling via `tools/call` method
- ✅ Response parsing and error handling
- ✅ Request/response ID tracking

### 2. Connection Management
- ✅ Persistent connection to MCP server process
- ✅ Automatic reconnection on failure
- ✅ Connection health monitoring
- ✅ Graceful cleanup on shutdown

### 3. Threading & Communication
- ✅ Background thread for reading responses
- ✅ Background thread for reading stderr (server logs)
- ✅ Thread-safe request ID generation
- ✅ Queue-based response handling

### 4. Error Handling
- ✅ Automatic retries (up to 3 attempts)
- ✅ Fallback to simulated mode on failure
- ✅ Comprehensive error logging
- ✅ Process health monitoring

### 5. Tool Support
- ✅ `generate_diagram`: Generate/validate/enhance diagram code
- ✅ `validate_code`: Validate code (via generate_diagram)
- ✅ `list_tools`: List available MCP server tools

## Implementation Details

### MCP Protocol Flow

```
1. Start MCP server process (stdio)
   ↓
2. Send initialize request
   {
     "jsonrpc": "2.0",
     "method": "initialize",
     "params": {...}
   }
   ↓
3. Receive initialize response
   ↓
4. Send initialized notification
   ↓
5. Connection ready for tool calls
   ↓
6. Call tools via tools/call
   {
     "jsonrpc": "2.0",
     "method": "tools/call",
     "params": {
       "name": "generate_diagram",
       "arguments": {...}
     }
   }
```

### Code Structure

**File**: `backend/src/integrations/mcp_diagram_client.py`

**Key Classes**:
- `MCPDiagramClient`: Main client class
  - `_initialize_connection()`: Sets up MCP server process
  - `_send_initialize()`: MCP handshake
  - `_call_mcp_tool()`: Call MCP tools
  - `_read_responses()`: Background response reader
  - `_read_stderr()`: Background stderr reader
  - `generate_diagram()`: Public API for diagram generation
  - `validate_code()`: Public API for code validation

## How It Works

### Initialization

1. **On Startup**: If `USE_MCP_DIAGRAM_SERVER=true`
   - Parses server command
   - Starts MCP server as subprocess
   - Performs initialization handshake
   - Lists available tools

2. **During Runtime**: 
   - Connection is reused for all tool calls
   - Automatic reconnection if process dies
   - Retries up to 3 times on failure

### Tool Calling

1. **Request**: Build JSON-RPC request
   ```python
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "tools/call",
     "params": {
       "name": "generate_diagram",
       "arguments": {
         "code": "...",
         "diagram_type": "aws_architecture",
         "title": "..."
       }
     }
   }
   ```

2. **Send**: Write to stdin, wait for response
3. **Receive**: Parse JSON-RPC response from stdout
4. **Parse**: Extract result based on tool type

### Error Handling

- **Process dies**: Automatically reinitialize
- **Timeout**: Return error, fallback to simulated
- **Invalid response**: Log error, return simulated response
- **Connection failure**: Retry up to 3 times, then disable

## Testing

### Test 1: Verify Connection

```bash
cd /opt/diagram-generator/diagrams/backend
source venv/bin/activate
export USE_MCP_DIAGRAM_SERVER=true
export MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"

python -c "
import logging
logging.basicConfig(level=logging.INFO)
from src.integrations.mcp_diagram_client import get_mcp_client
client = get_mcp_client()
print(f'Enabled: {client.enabled}')
print(f'Initialized: {client._initialized}')
tools = client.list_tools()
print(f'Tools: {[t.get(\"name\") for t in tools]}')
"
```

### Test 2: Generate Diagram

```bash
python -c "
import logging
logging.basicConfig(level=logging.INFO)
from src.integrations.mcp_diagram_client import get_mcp_client

client = get_mcp_client()
code = '''
from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.network import APIGateway

with Diagram(\"Test\", show=False):
    api = APIGateway(\"API\")
    func = Lambda(\"Function\")
    db = Dynamodb(\"DB\")
    api >> func >> db
'''

result = client.generate_diagram(code, \"aws_architecture\", \"Test Diagram\")
print(f'Success: {result.get(\"success\")}')
print(f'Error: {result.get(\"error\")}')
"
```

## Logging

All MCP operations are logged with `[MCP]` prefix:

- `[MCP] MCPDiagramClient initialized`
- `[MCP] === Initializing MCP server connection ===`
- `[MCP] Sending initialize request`
- `[MCP] Connection initialized successfully`
- `[MCP] Available tools: generate_diagram, list_icons, get_diagram_examples`
- `[MCP] === Calling generate_diagram tool ===`
- `[MCP] Tool call succeeded`

## Configuration

### Environment Variables

```bash
# Enable MCP integration
USE_MCP_DIAGRAM_SERVER=true

# MCP server command (optional)
MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"
# Or:
MCP_DIAGRAM_SERVER_COMMAND="uvx awslabs.aws-diagram-mcp-server"
```

### .env File

```bash
USE_MCP_DIAGRAM_SERVER=true
MCP_DIAGRAM_SERVER_COMMAND="uv tool run awslabs.aws-diagram-mcp-server"
```

## Troubleshooting

### Issue: Connection fails on startup

**Check**:
1. MCP server is installed: `uv tool run awslabs.aws-diagram-mcp-server --help`
2. Command is correct in environment variable
3. Check logs for initialization errors

**Solution**:
```bash
# Test MCP server directly
uv tool run awslabs.aws-diagram-mcp-server --help

# Verify command
echo $MCP_DIAGRAM_SERVER_COMMAND
```

### Issue: Process dies immediately

**Check**:
1. MCP server dependencies installed (GraphViz, Python packages)
2. Server command is correct
3. Check stderr logs for server errors

**Solution**:
```bash
# Check MCP server stderr
# Look for [MCP] Server stderr: ... in logs

# Test server manually
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | uv tool run awslabs.aws-diagram-mcp-server
```

### Issue: No response from tool calls

**Check**:
1. Connection is initialized (check logs)
2. Tool name is correct (`generate_diagram`)
3. Parameters are correct format

**Solution**:
```bash
# List available tools
python -c "
from src.integrations.mcp_diagram_client import get_mcp_client
client = get_mcp_client()
tools = client.list_tools()
for tool in tools:
    print(f\"{tool.get('name')}: {tool.get('description', 'No description')}\")
"
```

## Performance Considerations

1. **Connection Reuse**: Single persistent connection for all calls
2. **Threading**: Non-blocking response reading
3. **Timeout**: 30s timeout per tool call
4. **Retries**: Up to 3 retries on connection failure

## Security

- ✅ Code scanning via MCP server
- ✅ Input validation before sending to MCP
- ✅ Timeout protection (30s)
- ✅ Process isolation (subprocess)
- ✅ Error messages don't expose sensitive data

## Next Steps

1. ✅ Full MCP protocol implemented
2. ⏳ Test with real MCP server installation
3. ⏳ Verify tool responses match expected format
4. ⏳ Optimize connection reuse if needed
5. ⏳ Add metrics/monitoring for MCP calls
