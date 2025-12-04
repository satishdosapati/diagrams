# Intelligent Node Resolution - Quick Reference

## How It Works

The system automatically resolves generic terms to specific node types using **context clues** from component names and descriptions.

## Key Examples

### 1. Subnet Resolution

| Input Type | Component Name | Resolved To | Class |
|------------|---------------|-------------|-------|
| `subnet` | "Public Subnet" | `public_subnet` | `PublicSubnet` |
| `subnet` | "Private Subnet" | `private_subnet` | `PrivateSubnet` |
| `subnet` | "External Subnet" | `public_subnet` | `PublicSubnet` |
| `subnet` | "Internal Subnet" | `private_subnet` | `PrivateSubnet` |
| `subnet` | "App Subnet" | `private_subnet` | `PrivateSubnet` |
| `subnet` | "Subnet" | `private_subnet` | `PrivateSubnet` (default) |

**How it works:**
- Detects `"subnet"` as ambiguous term
- Checks component name for keywords: `"public"`, `"private"`, `"external"`, `"internal"`
- Maps to specific subnet type based on context
- Defaults to `private_subnet` if no indicator found

### 2. Database Resolution

| Input Type | Component Name | Resolved To | Class |
|------------|---------------|-------------|-------|
| `database` | "Relational Database" | `rds` | `RDS` |
| `database` | "NoSQL Database" | `dynamodb` | `Dynamodb` |
| `database` | "Document Database" | `dynamodb` | `Dynamodb` |
| `database` | "DynamoDB Database" | `dynamodb` | `Dynamodb` |

**How it works:**
- Detects `"database"` as ambiguous term
- Checks for keywords: `"relational"` → RDS, `"nosql"`/`"document"` → DynamoDB
- Uses service name if mentioned (e.g., "DynamoDB")

### 3. Function Resolution

| Input Type | Component Name | Resolved To | Class |
|------------|---------------|-------------|-------|
| `function` | "Lambda Function" | `lambda` | `Lambda` |
| `function` | "Serverless Function" | `lambda` | `Lambda` |
| `function` | "Container Function" | `ecs` | `ECS` |
| `function` | "Kubernetes Function" | `eks` | `EKS` |

**How it works:**
- Detects `"function"` as ambiguous term
- Checks for keywords: `"lambda"`/`"serverless"` → Lambda, `"container"` → ECS, `"kubernetes"` → EKS
- Defaults to `lambda` (most common)

### 4. Plural/Variation Handling

| Input Type | Resolved To | Method |
|------------|-------------|--------|
| `subnets` | `subnet` | Fuzzy matching (92% similarity) |
| `vpcs` | `vpc` | Fuzzy matching |
| `api-gateway` | `api_gateway` | Normalized matching |
| `api_gateway` | `api_gateway` | Exact match |

**How it works:**
- Normalizes input (removes hyphens, underscores, case)
- Compares with registry using string similarity
- Matches if similarity ≥ 60%

## Resolution Priority

```
1. Context-Aware Matching (if component name available)
   ↓
2. Exact Match
   ↓
3. Normalized Match (ignores formatting)
   ↓
4. Fuzzy Matching (≥60% similarity)
   ↓
5. Keyword Matching (description overlap)
   ↓
6. Error with Suggestions
```

## Real-World Example

**User Input:**
> "Create a VPC with a public subnet for web servers and a private subnet for databases"

**Agent Generates:**
```json
{
  "components": [
    {"id": "vpc1", "name": "VPC", "type": "vpc"},
    {"id": "sub1", "name": "Public Subnet", "type": "subnet"},
    {"id": "sub2", "name": "Private Subnet", "type": "subnet"}
  ]
}
```

**Resolution Process:**

1. **VPC**: Exact match → `VPC` class ✓
2. **Subnet 1**: 
   - Type: `subnet` (ambiguous)
   - Name: "Public Subnet"
   - Context check: Contains "public" → `public_subnet` → `PublicSubnet` class ✓
3. **Subnet 2**:
   - Type: `subnet` (ambiguous)
   - Name: "Private Subnet"
   - Context check: Contains "private" → `private_subnet` → `PrivateSubnet` class ✓

## Context Keywords

### Subnets
- **Public**: `public`, `external`, `dmz`, `internet`
- **Private**: `private`, `internal`, `app`, `data`

### Databases
- **RDS**: `relational`, `sql`, `postgres`, `mysql`
- **DynamoDB**: `nosql`, `document`, `key-value`, `dynamodb`

### Functions
- **Lambda**: `lambda`, `serverless`, `aws lambda`
- **ECS**: `container`, `docker`, `fargate`
- **EKS**: `kubernetes`, `k8s`, `eks`
- **Step Functions**: `step`, `workflow`

## Try It Yourself

Run the demo script:
```bash
cd backend
python examples/intelligent_resolution_demo.py
```

This will show all resolution examples in action!

