# AWS Architectural Advisor

## Overview

The AWS Architectural Advisor provides intelligent component ordering, connection validation, and architectural pattern recognition for AWS diagrams. It ensures diagrams follow AWS best practices and logical architectural layers.

## Features

### 1. **Component Layer Ordering**

Components are automatically sorted by architectural layers (left to right):

```
Internet/Edge (Layer 0-1)
  ↓
Network (Layer 2-3)
  ↓
Application/API (Layer 4)
  ↓
Compute (Layer 5)
  ↓
Integration (Layer 6)
  ↓
Data (Layer 7)
  ↓
Analytics (Layer 8)
  ↓
Security/Management (Layer 9)
```

**Example:**
- Input: `[EC2, VPC, API Gateway, Lambda]`
- Output: `[VPC, API Gateway, Lambda, EC2]` (ordered by layer)

### 2. **Connection Validation**

Automatically suggests missing connections based on AWS patterns:

- **VPC Patterns**: VPC → Subnet, Subnet → EC2
- **Serverless Pattern**: API Gateway → Lambda → DynamoDB
- **Three-Tier Pattern**: ALB → EC2 → RDS
- **Data Pipeline**: S3 → Glue → Athena → QuickSight

### 3. **Missing Component Suggestions**

Identifies missing dependencies:

- EC2 → suggests VPC and Subnet
- RDS → suggests VPC and Subnet
- Lambda → can work standalone (uses default VPC)

### 4. **Architectural Patterns**

Recognizes and enforces common AWS patterns:

- **Serverless**: API Gateway → Lambda → DynamoDB
- **Three-Tier**: ALB → EC2 → RDS
- **Microservices**: ALB → ECS → RDS
- **Data Pipeline**: S3 → Glue → Athena → QuickSight
- **VPC Network**: VPC → Internet Gateway → Subnet → NAT Gateway

## Usage

### In DiagramAgent

The advisor is automatically integrated:

```python
# When generating a diagram for AWS provider
spec = agent.generate_spec("VPC with EC2 instance", provider="aws")

# Spec is automatically enhanced with:
# - Component ordering
# - Missing connections (VPC → Subnet → EC2)
# - Missing components (Subnet if missing)
```

### In ModificationAgent

The advisor enhances modifications:

```python
# When modifying an AWS diagram
updated_spec, changes = modification_agent.modify(
    session_id,
    current_spec,
    "Add a Lambda function"
)

# Enhancement ensures:
# - Lambda is positioned correctly
# - Connections follow patterns (API Gateway → Lambda if API Gateway exists)
```

## Configuration

### Enable MCP Integration

Set environment variable to enable AWS Diagram MCP Server:

```bash
export USE_MCP_DIAGRAM_SERVER=true
```

The AWS Diagram MCP Server integration validates and enhances generated diagram code. See `MCP_INTEGRATION.md` for details.

## Examples

### Example 1: VPC Network

**Input:**
```
"VPC with EC2 instance"
```

**Before Enhancement:**
- Components: `[VPC, EC2]` (unordered)
- Connections: `[]` (none)

**After Enhancement:**
- Components: `[VPC, Subnet, EC2]` (ordered, subnet added)
- Connections: `[VPC → Subnet, Subnet → EC2]` (suggested)

### Example 2: Serverless API

**Input:**
```
"API Gateway with Lambda and DynamoDB"
```

**Before Enhancement:**
- Components: `[Lambda, DynamoDB, API Gateway]` (unordered)
- Connections: `[]` (none)

**After Enhancement:**
- Components: `[API Gateway, Lambda, DynamoDB]` (ordered)
- Connections: `[API Gateway → Lambda, Lambda → DynamoDB]` (suggested)

### Example 3: Three-Tier Architecture

**Input:**
```
"Load balancer, EC2, and RDS database"
```

**Before Enhancement:**
- Components: `[EC2, RDS, ALB]` (unordered)
- Connections: `[]` (none)

**After Enhancement:**
- Components: `[ALB, EC2, RDS]` (ordered)
- Connections: `[ALB → EC2, EC2 → RDS]` (suggested)
- Missing: `[VPC, Subnet]` (suggested)

## Implementation Details

### Component Layer Mapping

```python
LAYER_ORDER = {
    "route53": 0,           # Internet/Edge
    "cloudfront": 1,
    "vpc": 2,               # Network
    "subnet": 3,
    "api_gateway": 4,       # Application
    "lambda": 5,            # Compute
    "dynamodb": 7,          # Data
    # ... etc
}
```

### Dependency Rules

```python
DEPENDENCIES = {
    "ec2": ["vpc", "subnet"],
    "rds": ["vpc", "subnet"],
    "lambda": [],  # Can use default VPC
}
```

### Pattern Templates

```python
PATTERNS = {
    "serverless": {
        "components": ["api_gateway", "lambda", "dynamodb"],
        "connections": [
            ("api_gateway", "lambda"),
            ("lambda", "dynamodb")
        ]
    }
}
```

## Future Enhancements

1. **MCP Integration**: Query AWS Documentation MCP tools for real-time guidance
2. **Pattern Detection**: Automatically detect architecture patterns from descriptions
3. **Best Practice Validation**: Validate against AWS Well-Architected Framework
4. **Multi-Cloud Support**: Extend to Azure and GCP advisors
5. **Custom Patterns**: Allow users to define custom architectural patterns

## Benefits

✅ **Better Diagrams**: Components are logically ordered
✅ **Complete Connections**: Missing connections are automatically suggested
✅ **AWS Best Practices**: Follows AWS architectural patterns
✅ **Intelligent Suggestions**: Identifies missing components
✅ **Consistent Layout**: Diagrams follow standard AWS conventions

