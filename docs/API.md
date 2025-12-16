# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: `http://your-ec2-ip:8000`

## Interactive Documentation

- **Swagger UI**: `/docs` - Interactive API explorer
- **ReDoc**: `/redoc` - Alternative API documentation

## Authentication

Currently no authentication required. For production, add API keys or OAuth.

## Request Headers

All requests should include:
- `Content-Type: application/json` (for POST requests)

## Response Headers

All responses include:
- `X-Request-ID`: Unique request identifier for tracking
- `X-Process-Time`: Request processing time in seconds

## Endpoints

### POST /api/generate-diagram

Generate an architecture diagram from natural language description.

**Request:**
```json
{
  "description": "Create a serverless API with API Gateway, Lambda, and DynamoDB",
  "provider": "aws",
  "outformat": "png",
  "direction": "LR",
  "graphviz_attrs": {
    "graph_attr": {},
    "node_attr": {},
    "edge_attr": {}
  }
}
```

**Parameters:**
- `description` (required): Natural language description of the architecture
- `provider` (optional, default: "aws"): Cloud provider - "aws", "azure", or "gcp"
- `outformat` (optional, default: "png"): Output format - "png", "svg", "pdf", "dot"
- `direction` (optional, deprecated): Diagram direction - always uses "LR" (left-to-right) regardless of input
- `graphviz_attrs` (optional): Graphviz styling attributes

**Response:**
```json
{
  "diagram_url": "/api/diagrams/serverless_api.png",
  "message": "Successfully generated diagram: Serverless API",
  "session_id": "uuid-string",
  "generation_id": "uuid-string",
  "generated_code": "from diagrams import Diagram..."
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid input
- `500`: Generation failed

### POST /api/regenerate-format

Regenerate an existing diagram in a different output format.

**Request:**
```json
{
  "session_id": "uuid-string",
  "outformat": "svg"
}
```

**Parameters:**
- `session_id` (required): Session ID from previous diagram generation
- `outformat` (required): Desired output format - "png", "svg", "pdf", "dot"

**Response:**
```json
{
  "diagram_url": "/api/diagrams/serverless_api.svg",
  "message": "Diagram regenerated in SVG format",
  "session_id": "uuid-string",
  "generation_id": "uuid-string",
  "generated_code": null
}
```

**Status Codes:**
- `200`: Success
- `404`: Session not found or expired
- `500`: Regeneration failed

### POST /api/execute-code

Execute Python code directly to generate a diagram (Advanced Code Mode).

**Request:**
```json
{
  "code": "from diagrams import Diagram\nfrom diagrams.aws.compute import EC2\nwith Diagram(...): EC2('Instance')",
  "outformat": "png"
}
```

**Parameters:**
- `code` (required): Python code using Diagrams library
- `outformat` (optional, default: "png"): Output format

**Response:**
```json
{
  "diagram_url": "/api/diagrams/diagram.png",
  "message": "Code executed successfully",
  "errors": [],
  "warnings": []
}
```

**Status Codes:**
- `200`: Success
- `500`: Execution failed

### GET /api/completions/{provider}

Get code completions for a specific cloud provider.

**Parameters:**
- `provider` (path parameter): Cloud provider - "aws", "azure", or "gcp"

**Response:**
```json
{
  "classes": {
    "compute": ["EC2", "Lambda", "ECS"],
    "storage": ["S3", "EBS"]
  },
  "imports": {
    "EC2": "from diagrams.aws.compute import EC2"
  },
  "keywords": ["Diagram", "Cluster", "Edge"],
  "operators": [">>", "<<", "-"]
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid provider
- `500`: Failed to load completions

### POST /api/validate-code

Validate Python code syntax and check for common errors.

**Request:**
```json
{
  "code": "from diagrams import Diagram\nfrom diagrams.aws.compute import EC2"
}
```

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "suggestions": []
}
```

**Status Codes:**
- `200`: Success (validation completed)

### GET /api/diagrams/{filename}

Retrieve a generated diagram file.

**Parameters:**
- `filename` (path parameter): Diagram filename (e.g., "my_diagram.png")

**Response:** 
- Image file (PNG, SVG) or DOT source code

**Status Codes:**
- `200`: Success
- `400`: Invalid filename format
- `403`: Path traversal attempt detected
- `404`: Diagram file not found

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "diagram-generator-api"
}
```

**Status Codes:**
- `200`: Service is healthy

### POST /api/feedback

Submit thumbs up/down feedback for a diagram generation.

**Request:**
```json
{
  "generation_id": "uuid-string",
  "session_id": "uuid-string",
  "thumbs_up": true,
  "code_hash": "optional-sha256-hash",
  "code": "optional-python-code-string"
}
```

**Parameters:**
- `generation_id` (required): Unique ID from diagram generation response
- `session_id` (required): Session ID from diagram generation
- `thumbs_up` (required): Boolean - true for thumbs up, false for thumbs down
- `code_hash` (optional): SHA256 hash of generated code
- `code` (optional): Generated Python code for pattern extraction

**Response:**
```json
{
  "feedback_id": "uuid-string",
  "message": "Thank you for your feedback!"
}
```

**Status Codes:**
- `200`: Success
- `500`: Failed to save feedback

### GET /api/error-logs/{request_id}

Get logs for a specific request ID. Used for error reporting and debugging.

**Parameters:**
- `request_id` (path parameter): Request identifier from `X-Request-ID` header

**Response:**
```json
{
  "request_id": "uuid-string",
  "logs": ["log line 1", "log line 2", ...],
  "last_50_lines": false
}
```

**Status Codes:**
- `200`: Success (returns logs for request_id, or last 50 logs if not found)

### GET /api/feedback/stats

Get feedback statistics for the system.

**Parameters:**
- `days` (query parameter, optional, default: 30): Number of days to look back

**Response:**
```json
{
  "total_feedback": 100,
  "thumbs_up": 85,
  "thumbs_down": 15,
  "success_rate": 0.85,
  "period_days": 30
}
```

**Status Codes:**
- `200`: Success
- `500`: Failed to get stats

## Session Management

- Sessions expire after 1 hour of inactivity
- Session cleanup runs automatically every 5 minutes
- Expired sessions return `404` with message "Session not found or expired"

## Output Formats

Supported output formats:
- **png**: PNG image (default, raster)
- **svg**: Scalable Vector Graphics (vector, editable)
- **pdf**: PDF document (vector)
- **dot**: Graphviz DOT source code (text, editable)

## Quick Reference

### Common Graphviz Attributes

**Graph Attributes:**
```json
{
  "rankdir": "LR",           // Layout direction: LR, TB, BT, RL
  "bgcolor": "#ffffff",      // Background color
  "fontname": "Helvetica",   // Font family
  "nodesep": "0.8",         // Node spacing
  "ranksep": "1.0",         // Rank spacing
  "splines": "polyline"     // Edge routing: polyline, ortho, curved
}
```

**Node Attributes:**
```json
{
  "shape": "box",            // box, ellipse, circle, diamond
  "style": "filled,rounded", // filled, rounded, dashed, dotted
  "fillcolor": "#e8f4f8",    // Fill color
  "fontcolor": "#2c3e50",    // Text color
  "penwidth": "1.5"         // Border width
}
```

**Edge Attributes:**
```json
{
  "color": "#333333",        // Edge color
  "style": "bold",          // solid, dashed, dotted, bold
  "arrowsize": "0.8",      // Arrow size
  "penwidth": "1.5",        // Edge width
  "label": "HTTP"           // Edge label
}
```

### Common Patterns

**Serverless API:**
```json
{
  "description": "API Gateway, Lambda, DynamoDB",
  "provider": "aws",
  "direction": "LR"
}
```

**Microservices with Clusters:**
```json
{
  "description": "Microservices architecture",
  "provider": "aws",
  "clusters": [
    {"id": "services", "name": "Services", "component_ids": ["svc1", "svc2"]},
    {"id": "data", "name": "Data Layer", "component_ids": ["db"]}
  ]
}
```

### Troubleshooting

- **Diagram not generating?** Check backend logs: `sudo journalctl -u diagram-api.service -f`
- **Messy edges?** Use `"splines": "polyline"` in graph_attr, increase `nodesep` and `ranksep`
- **Session expired?** Sessions expire after 1 hour of inactivity - generate a new diagram
