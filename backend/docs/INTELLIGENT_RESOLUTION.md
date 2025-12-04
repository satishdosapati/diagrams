# Intelligent Node Resolution - How It Works

## Overview

The intelligent node resolution system automatically maps generic or user-friendly terms (like "subnet", "database", "function") to specific node types in the registry based on context, fuzzy matching, and semantic understanding.

## Resolution Flow

When a component needs to be resolved, the system follows this priority order:

```
1. Context-Aware Matching (if component name/context available)
   ↓ (if no match)
2. Exact Match
   ↓ (if no match)
3. Normalized Match (ignores underscores, hyphens, case)
   ↓ (if no match)
4. Fuzzy Matching (string similarity ≥ 60%)
   ↓ (if no match)
5. Keyword Matching (description/keyword overlap)
   ↓ (if no match)
6. Error with Suggestions
```

## Example 1: Context-Aware Subnet Resolution

### Scenario
User describes: "A VPC with a public subnet and a private subnet"

The agent generates:
```json
{
  "components": [
    {"id": "vpc1", "name": "VPC", "type": "vpc"},
    {"id": "subnet1", "name": "Public Subnet", "type": "subnet"},
    {"id": "subnet2", "name": "Private Subnet", "type": "subnet"}
  ]
}
```

### Resolution Process

**Component 1: `subnet1`**
- Input: `type="subnet"`, `name="Public Subnet"`
- Step 1: Check if ambiguous term → Yes (`subnet` is ambiguous)
- Step 2: Try context-aware matching:
  - Pattern: `"subnet"` detected
  - Component name contains: `"public"`
  - Context pattern match: `"public"` → `public_subnet`
- **Result**: `public_subnet` → `PublicSubnet` class

**Component 2: `subnet2`**
- Input: `type="subnet"`, `name="Private Subnet"`
- Step 1: Check if ambiguous term → Yes
- Step 2: Try context-aware matching:
  - Pattern: `"subnet"` detected
  - Component name contains: `"private"`
  - Context pattern match: `"private"` → `private_subnet`
- **Result**: `private_subnet` → `PrivateSubnet` class

**Component 3: `subnet3` (no context)**
- Input: `type="subnet"`, `name="Subnet"`
- Step 1: Check if ambiguous term → Yes
- Step 2: Try context-aware matching:
  - No clear indicator in name
  - Default: `private_subnet` (most common use case)
- **Result**: `private_subnet` → `PrivateSubnet` class

## Example 2: Fuzzy Matching (Plurals/Variations)

### Scenario
User says: "Create a VPC with multiple subnets"

The agent might generate:
```json
{
  "components": [
    {"id": "subnets", "name": "Subnets", "type": "subnets"}
  ]
}
```

### Resolution Process

**Component: `subnets`**
- Input: `type="subnets"` (plural form)
- Step 1: Exact match → No (`subnets` not in registry)
- Step 2: Normalized match → No
- Step 3: Fuzzy matching:
  - Compare `"subnets"` with all registry nodes
  - Similarity scores:
    - `subnet`: 0.92 (92% similar)
    - `private_subnet`: 0.75
    - `public_subnet`: 0.75
  - Best match: `subnet` with 92% similarity
  - Threshold check: 92% ≥ 60% → **Match!**
- **Result**: `subnet` → `PrivateSubnet` class (default)

## Example 3: Keyword Matching

### Scenario
User says: "Add a relational database"

The agent generates:
```json
{
  "components": [
    {"id": "db", "name": "Relational Database", "type": "database"}
  ]
}
```

### Resolution Process

**Component: `database`**
- Input: `type="database"`, `name="Relational Database"`
- Step 1: Context-aware matching:
  - Pattern: `"database"` detected
  - Component name contains: `"relational"`
  - Context pattern: `"relational"` → `rds`
- **Result**: `rds` → `RDS` class

**Alternative: NoSQL Database**
- Input: `type="database"`, `name="NoSQL Database"`
- Context pattern: `"nosql"` → `dynamodb`
- **Result**: `dynamodb` → `Dynamodb` class

## Example 4: Function Resolution

### Scenario
User says: "Create a serverless function"

The agent generates:
```json
{
  "components": [
    {"id": "func1", "name": "Serverless Function", "type": "function"}
  ]
}
```

### Resolution Process

**Component: `function`**
- Input: `type="function"`, `name="Serverless Function"`
- Step 1: Context-aware matching:
  - Pattern: `"function"` detected
  - Component name contains: `"serverless"`
  - Context pattern: `"serverless"` → `lambda`
- **Result**: `lambda` → `Lambda` class

**Alternative: Container Function**
- Input: `type="function"`, `name="Container Function"`
- Context pattern: `"container"` → `ecs`
- **Result**: `ecs` → `ECS` class

## Example 5: Normalized Matching

### Scenario
User says: "Add an API gateway"

The agent might generate:
```json
{
  "components": [
    {"id": "api", "name": "API Gateway", "type": "api-gateway"}
  ]
}
```

### Resolution Process

**Component: `api-gateway`**
- Input: `type="api-gateway"` (with hyphen)
- Step 1: Exact match → No (`api-gateway` not in registry)
- Step 2: Normalized match:
  - Normalize input: `"apigateway"` (remove hyphen)
  - Compare with registry: `api_gateway` → normalized: `"apigateway"`
  - Match found!
- **Result**: `api_gateway` → `APIGateway` class

## Example 6: No Match Found (With Suggestions)

### Scenario
User says: "Add a custom service XYZ"

The agent generates:
```json
{
  "components": [
    {"id": "xyz", "name": "Custom Service", "type": "xyz_service"}
  ]
}
```

### Resolution Process

**Component: `xyz_service`**
- Input: `type="xyz_service"`
- Step 1: Exact match → No
- Step 2: Normalized match → No
- Step 3: Fuzzy matching:
  - Best match: `api_gateway` with 45% similarity
  - Below 60% threshold → No match
- Step 4: Keyword matching → No
- Step 5: Generate suggestions:
  - Top 5 similar nodes with similarity scores
- **Result**: Error with helpful message:
  ```
  Node type 'xyz_service' not supported for provider 'aws'.
  Available nodes: api_gateway, lambda, ec2...
  Did you mean: 'api_gateway' (45%), 'lambda' (30%), 'ecs' (25%)?
  ```

## Example 7: Real-World Architecture

### Scenario
User describes: "A serverless API with API Gateway, Lambda functions, and a DynamoDB database"

The agent generates:
```json
{
  "components": [
    {"id": "api", "name": "API Gateway", "type": "api_gateway"},
    {"id": "func", "name": "Lambda Function", "type": "function"},
    {"id": "db", "name": "DynamoDB Database", "type": "database"}
  ]
}
```

### Resolution Process

**Component 1: `api_gateway`**
- Exact match → `api_gateway` exists → **APIGateway** class ✓

**Component 2: `function`**
- Context-aware: `"Lambda Function"` → `lambda` → **Lambda** class ✓

**Component 3: `database`**
- Context-aware: `"DynamoDB Database"` → Contains `"dynamodb"` → `dynamodb` → **Dynamodb** class ✓

## Context Patterns

The system recognizes these common patterns:

### Network Patterns
```python
"subnet" + "public" → "public_subnet"
"subnet" + "private" → "private_subnet"
"subnet" + "external" → "public_subnet"
"subnet" + "internal" → "private_subnet"
"subnet" + "app" → "private_subnet" (default)
```

### Database Patterns
```python
"database" + "relational" → "rds"
"database" + "nosql" → "dynamodb"
"database" + "document" → "dynamodb"
"database" + "key-value" → "dynamodb"
"db" + "sql" → "rds"
```

### Compute Patterns
```python
"function" + "serverless" → "lambda"
"function" + "container" → "ecs"
"function" + "kubernetes" → "eks"
"compute" + "virtual machine" → "ec2"
```

## Code Flow Example

Here's what happens internally:

```python
# 1. Component created by agent
component = Component(
    id="subnet1",
    name="Public Subnet",
    type="subnet"  # Generic term
)

# 2. ComponentResolver.resolve_component_class() called
resolver = ComponentResolver("aws")

# 3. Check if ambiguous term
node_id = "subnet"
is_ambiguous = node_id in {"subnet", "database", "function", ...}
# → True

# 4. Try intelligent resolution
if is_ambiguous:
    resolved_id = intelligent_resolver.resolve(
        node_id="subnet",
        component_name="Public Subnet",
        context={"provider": "aws"}
    )
    # → "public_subnet"

# 5. Look up resolved node in registry
node_mapping = registry.get_node_mapping("aws", "public_subnet")
# → ("network", "PublicSubnet")

# 6. Import and return class
module = importlib.import_module("diagrams.aws.network")
node_class = getattr(module, "PublicSubnet")
# → <class 'diagrams.aws.network.PublicSubnet'>

# 7. Use in diagram generation
with Diagram():
    subnet1 = PublicSubnet("Public Subnet")
```

## Benefits

1. **User-Friendly**: Accepts natural language terms
2. **Intelligent**: Uses context to disambiguate
3. **Flexible**: Handles variations, plurals, synonyms
4. **Maintainable**: No hardcoded aliases to maintain
5. **Helpful**: Provides suggestions when no match found

## Debugging

To see resolution in action, check logs:

```
INFO: Intelligently resolved 'subnet' to 'public_subnet' for component 'Public Subnet'
DEBUG: Context hint 'public' found, mapping 'subnet' -> 'public_subnet'
INFO: Resolved aws.public_subnet -> diagrams.aws.network.PublicSubnet
```

## Adding New Patterns

To add new context patterns, edit `backend/src/resolvers/intelligent_resolver.py`:

```python
context_patterns = {
    "your_pattern": {
        "hint1": "mapped_node1",
        "hint2": "mapped_node2",
    },
}
```

The resolver will automatically use these patterns when matching.

