# How AWS Diagram MCP Server is Used - Detailed Explanation

## Overview

The AWS Diagram MCP Server integration provides **code validation and enhancement** capabilities for generated diagram code. It acts as a **post-processing step** that validates and potentially improves the Python code generated from your ArchitectureSpec.

## Current Integration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. User Request: "Create API Gateway with Lambda and DynamoDB" │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. DiagramAgent.generate_spec()                                  │
│    - Parses natural language                                      │
│    - Creates ArchitectureSpec (components, connections)         │
└───────────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────────┐
│ 3. AWS Architectural Advisor.enhance_spec()                      │
│    - Orders components by architectural layers                    │
│    - Suggests missing connections                                 │
│    - Creates clusters                                             │
└───────────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────────┐
│ 4. MCP Post-Processing (IF ENABLED)                              │
│    - Generates Python code from ArchitectureSpec                  │
│    - Validates code via MCP server                                │
│    - Enhances code via MCP server                                 │
│    - Logs results (doesn't modify spec)                           │
└───────────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────────┐
│ 5. DiagramsEngine.render()                                        │
│    - Generates Python code (again)                                │
│    - Executes code                                                │
│    - Generates diagram image                                      │
└───────────────────────────────────────────────────────────────────┘
```

## Detailed Step-by-Step: MCP Post-Processing

### Step 1: MCP Client Initialization

**When**: Application startup  
**Where**: `backend/src/agents/diagram_agent.py` line 44

```python
# In DiagramAgent.__init__()
self.mcp_client = get_mcp_client()  # Creates MCPDiagramClient instance
self.use_mcp_tools = self.mcp_client.enabled  # Checks USE_MCP_DIAGRAM_SERVER env var
```

**What happens**:
- Reads `USE_MCP_DIAGRAM_SERVER` environment variable
- If `true`, enables MCP integration
- Logs initialization status

**Logs you'll see**:
```
[MCP] MCPDiagramClient initialized
[MCP] Enabled: True
[MCP] Server command: uv tool run awslabs.aws-diagram-mcp-server
[DIAGRAM_AGENT] MCP tools enabled: True
```

### Step 2: ArchitectureSpec Generation

**When**: User makes diagram generation request  
**Where**: `backend/src/agents/diagram_agent.py` line 180-263

```python
# User input → Strands Agent → ArchitectureSpec
spec = self.agent(prompt)  # Generates ArchitectureSpec from natural language
spec = self.aws_advisor.enhance_spec(spec)  # AWS architectural enhancements
```

**Result**: ArchitectureSpec with components, connections, clusters

### Step 3: MCP Post-Processing (If Enabled)

**When**: After ArchitectureSpec is generated (for AWS diagrams only)  
**Where**: `backend/src/agents/diagram_agent.py` line 265-325

```python
if self.use_mcp_tools and final_provider == "aws":
    spec = self._post_process_with_mcp(spec)
```

**What happens**:

#### 3a. Generate Python Code
```python
# Convert ArchitectureSpec → Python code
code = engine._generate_code(spec, resolver)
```

**Example generated code**:
```python
from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.network import APIGateway

with Diagram("Serverless API", show=False, filename="serverless_api"):
    api = APIGateway("API Gateway")
    function = Lambda("Function")
    database = Dynamodb("Database")
    
    api >> function >> database
```

#### 3b. Validate Code via MCP
```python
validation_result = self.mcp_client.validate_code(code)
```

**What MCP server does** (when fully integrated):
- Scans code for security issues
- Checks for diagrams library best practices
- Validates syntax and structure
- Returns validation results

**Current status**: Simulated (returns success without actual MCP call)

#### 3c. Enhance Code via MCP
```python
enhance_result = self.mcp_client.generate_diagram(
    code,
    diagram_type="aws_architecture",
    title=spec.title
)
```

**What MCP server does** (when fully integrated):
- Optimizes code structure
- Improves diagram layout
- Applies best practices
- Returns enhanced code

**Current status**: Simulated (returns original code with success flag)

### Step 4: Logging Results

**What gets logged**:
```
[DIAGRAM_AGENT] === MCP Post-processing ===
[DIAGRAM_AGENT] Spec: 3 components, 2 connections
[DIAGRAM_AGENT] Generated code length: 245 characters
[MCP] === Calling validate_code ===
[MCP] Code validation passed
[DIAGRAM_AGENT] MCP code validation: PASSED
[MCP] === Calling generate_diagram tool ===
[MCP] Tool call simulated (MCP server integration pending)
[DIAGRAM_AGENT] MCP code enhancement: SUCCESS
```

**Note**: The ArchitectureSpec itself is **not modified** by MCP post-processing. It's only used for validation and logging.

## Current Implementation Status

### ✅ What's Working

1. **MCP Client Wrapper**: Fully implemented
   - Reads environment variables
   - Provides Python interface to MCP server
   - Comprehensive logging

2. **Integration Points**: All connected
   - DiagramAgent initializes MCP client
   - Post-processing method implemented
   - Logging throughout

3. **Code Generation**: Working
   - Generates Python code from ArchitectureSpec
   - Ready for MCP validation/enhancement

### ⏳ What's Pending

1. **Actual MCP Protocol**: Currently simulated
   - `_call_mcp_tool()` returns mock responses
   - Needs real MCP client library integration
   - See `backend/src/integrations/mcp_diagram_client.py` line 148-211

2. **MCP Server Communication**: Not yet implemented
   - Placeholder for actual MCP stdio protocol
   - Will use proper MCP Python SDK when available

## How MCP Server Would Be Used (When Fully Integrated)

### Scenario: User Requests "API Gateway with Lambda and DynamoDB"

**Step 1**: Your system generates ArchitectureSpec
```json
{
  "title": "Serverless API",
  "provider": "aws",
  "components": [
    {"id": "api", "name": "API Gateway", "type": "api_gateway"},
    {"id": "lambda", "name": "Function", "type": "lambda"},
    {"id": "db", "name": "Database", "type": "dynamodb"}
  ],
  "connections": [
    {"from_id": "api", "to_id": "lambda"},
    {"from_id": "lambda", "to_id": "db"}
  ]
}
```

**Step 2**: Your system generates Python code
```python
from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.network import APIGateway

with Diagram("Serverless API", show=False):
    api = APIGateway("API Gateway")
    function = Lambda("Function")
    database = Dynamodb("Database")
    api >> function >> database
```

**Step 3**: MCP Server validates code
- ✅ Checks for security issues (none found)
- ✅ Validates diagrams library usage (correct)
- ✅ Returns: `{"valid": true, "warnings": []}`

**Step 4**: MCP Server enhances code (optional)
- Optimizes imports
- Improves variable naming
- Adds best practices
- Returns enhanced code

**Step 5**: Your system executes code and generates diagram

## Key Components

### 1. MCPDiagramClient (`backend/src/integrations/mcp_diagram_client.py`)

**Purpose**: Python wrapper around AWS Diagram MCP Server

**Key Methods**:
- `generate_diagram(code, diagram_type, title)`: Generate/validate/enhance diagram code
- `validate_code(code)`: Validate code for security and best practices
- `_call_mcp_tool(tool_name, params)`: Internal method to call MCP server (currently simulated)

**Current Status**: 
- ✅ Structure complete
- ⏳ Actual MCP protocol pending

### 2. MCP Tools (`backend/src/agents/mcp_tools.py`)

**Purpose**: Tool functions that could be called by Strands Agents

**Functions**:
- `generate_diagram_from_code()`: Generate diagrams via MCP
- `validate_diagram_code()`: Validate code before execution
- `enhance_diagram_code()`: Enhance code with MCP optimizations

**Current Status**: 
- ✅ Functions implemented
- ⏳ Not yet registered as Strands Agent tools (for Strands doesn't support custom tools)

### 3. DiagramAgent Integration (`backend/src/agents/diagram_agent.py`)

**Purpose**: Integrates MCP into the diagram generation flow

**Key Points**:
- Initializes MCP client on startup
- Post-processes ArchitectureSpec with MCP (for AWS diagrams)
- Logs all MCP operations

**Current Status**: ✅ Fully integrated

## Benefits of MCP Integration

### 1. Code Validation
- **Security**: Scans for unsafe code patterns
- **Best Practices**: Ensures diagrams library usage follows best practices
- **Syntax**: Validates Python syntax before execution

### 2. Code Enhancement
- **Optimization**: Improves code structure and readability
- **Layout**: Better diagram layout suggestions
- **Standards**: Applies AWS diagramming standards

### 3. Future Extensibility
- **Sequence Diagrams**: MCP server supports sequence diagrams
- **Flow Charts**: MCP server supports flow charts
- **Class Diagrams**: MCP server supports class diagrams

## Current Limitations

1. **Simulated Calls**: MCP tool calls are currently simulated
   - Returns success without actual MCP server communication
   - Allows testing integration flow
   - Ready for real MCP protocol implementation

2. **AWS Only**: MCP post-processing only runs for AWS diagrams
   - Azure and GCP diagrams skip MCP step
   - Can be extended in the future

3. **No Spec Modification**: MCP doesn't modify ArchitectureSpec
   - Only validates/enhances generated code
   - Spec remains unchanged
   - Results are logged for debugging

## Next Steps for Full Integration

1. **Install MCP Server**: Follow `MCP_INSTALLATION.md`
2. **Implement MCP Protocol**: Update `_call_mcp_tool()` with real MCP client
3. **Test Integration**: Verify MCP server responds correctly
4. **Use Enhanced Code**: Optionally use MCP-enhanced code instead of original

## Example: What You'll See in Logs

When MCP is enabled and working:

```
[DIAGRAM_AGENT] MCP tools enabled: True
[MCP] MCPDiagramClient initialized
[MCP] Enabled: True
[MCP] Server command: uv tool run awslabs.aws-diagram-mcp-server

# During diagram generation:
[DIAGRAM_AGENT] === MCP Post-processing ===
[DIAGRAM_AGENT] Spec: 3 components, 2 connections
[MCP] === Calling validate_code ===
[MCP] Code length: 245 characters
[MCP] Code validation passed
[DIAGRAM_AGENT] MCP code validation: PASSED
[MCP] === Calling generate_diagram tool ===
[MCP] Diagram type: aws_architecture
[MCP] Title: Serverless API
[MCP] generate_diagram succeeded
[DIAGRAM_AGENT] MCP code enhancement: SUCCESS
```

## Summary

The AWS Diagram MCP Server integration:

1. **Validates** generated Python code for security and best practices
2. **Enhances** code with optimizations (when fully integrated)
3. **Logs** all operations for debugging and monitoring
4. **Doesn't modify** ArchitectureSpec (only validates/enhances code)
5. **Currently simulated** (ready for real MCP protocol implementation)

The integration is **non-invasive** - it doesn't change your existing flow, just adds validation/enhancement as an optional post-processing step.
