# MCP Integration Guide

## Current Status

The AWS Architectural Advisor is **prepared for MCP integration** but MCP tools are **not directly invoked** in the Python code. This is because:

1. **MCP tools are invoked through the MCP protocol/server**, not as direct Python function calls
2. **MCP tools are available at the agent level** where the MCP server is connected
3. **The advisor logs MCP queries** but actual invocation happens when the agent uses MCP tools

## How MCP Works

MCP (Model Context Protocol) tools are invoked through:
- The MCP server connection
- Agent-level tool calls
- Not direct Python function calls

## Current Implementation

### Logging

The advisor now logs MCP usage at multiple points:

```python
logger.info("[MCP] Querying AWS Documentation: {query}")
logger.info("[MCP] Query prepared: {query}")
logger.info("[ADVISOR] Enhancing spec...")
```

### MCP Query Preparation

The advisor prepares queries that would be sent to MCP:

```python
# In enhance_spec()
mcp_query = f"AWS architecture best practices for {components}"
logger.info(f"[MCP] Query prepared: {mcp_query}")
```

## Enabling MCP

To enable MCP (when fully integrated):

```bash
export USE_AWS_MCP=true
```

## What You'll See in Logs

When MCP is enabled, you'll see:

```
[MCP] Requesting architectural guidance for: ...
[MCP] Search query prepared: AWS architecture patterns...
[MCP] Querying AWS Documentation: ...
[ADVISOR] Enhancing spec: 3 components, 2 connections
[ADVISOR] Suggested 2 additional connections
```

## Full MCP Integration (Future)

For full MCP integration, the agent would need to:

1. **Have MCP tools available** in its tool list
2. **Call MCP tools directly** in prompts or tool calls
3. **Process MCP responses** to enhance guidance

Example (conceptual):
```python
# In agent prompt or tool call
result = mcp_AWS_Documentation_search_documentation(
    search_phrase="AWS architecture patterns",
    limit=5
)
# Process result and use in guidance
```

## Current Behavior

- ✅ **Logging**: All MCP queries are logged
- ✅ **Query Preparation**: Queries are prepared and logged
- ⏳ **Actual Invocation**: MCP tools invoked at agent level (when MCP server connected)
- ✅ **Fallback**: Uses enhanced static guidance when MCP not available

## Troubleshooting

If you don't see MCP logs:

1. **Check environment variable**: `USE_AWS_MCP=true`
2. **Check logs**: Look for `[MCP]` prefix in logs
3. **Check advisor calls**: Ensure advisor is being called
4. **Check provider**: MCP only active for AWS provider

## Next Steps

To fully integrate MCP:

1. Ensure MCP server is running and connected
2. Make MCP tools available to the agent
3. Update agent to call MCP tools directly
4. Process MCP responses in advisor

