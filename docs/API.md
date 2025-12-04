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
- `outformat` (optional, default: "png"): Output format - "png", "svg", "pdf", "dot", "jpg"
- `direction` (optional): Diagram direction - "LR", "TB", "BT", "RL"
- `graphviz_attrs` (optional): Graphviz styling attributes

**Response:**
```json
{
  "diagram_url": "/api/diagrams/serverless_api.png",
  "message": "Successfully generated diagram: Serverless API",
  "session_id": "uuid-string",
  "generated_code": "from diagrams import Diagram..."
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid input
- `500`: Generation failed

### POST /api/modify-diagram

Modify an existing diagram based on chat message.

**Request:**
```json
{
  "session_id": "uuid-string",
  "modification": "Add a CDN in front"
}
```

**Response:**
```json
{
  "diagram_url": "/api/diagrams/serverless_api.png",
  "message": "Diagram updated successfully",
  "changes": ["Added: CloudFront CDN"],
  "updated_spec": { ... }
}
```

### POST /api/undo-diagram

Undo last modification (simplified implementation).

**Request:**
```json
{
  "session_id": "uuid-string"
}
```

**Response:**
```json
{
  "diagram_url": "/api/diagrams/serverless_api.png",
  "message": "Diagram restored",
  "changes": [],
  "updated_spec": { ... }
}
```

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
- `outformat` (required): Desired output format - "png", "svg", "pdf", "dot", "jpg"

**Response:**
```json
{
  "diagram_url": "/api/diagrams/serverless_api.svg",
  "message": "Diagram regenerated in SVG format",
  "session_id": "uuid-string",
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
- Image file (PNG, SVG, JPG) or DOT source code

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
- **jpg**: JPEG image (raster)
