# API Documentation

## Endpoints

### POST /api/generate-diagram

Generate an architecture diagram from natural language description.

**Request:**
```json
{
  "description": "Create a serverless API with API Gateway, Lambda, and DynamoDB",
  "provider": "aws"
}
```

**Response:**
```json
{
  "diagram_url": "/api/diagrams/serverless_api.png",
  "message": "Successfully generated diagram: Serverless API",
  "session_id": "uuid-string"
}
```

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

### GET /api/diagrams/{filename}

Retrieve a generated diagram file.

**Response:** Image file (PNG)

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```
