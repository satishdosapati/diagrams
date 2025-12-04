# Intelligent Node Resolution

The system uses intelligent node resolution to map generic or user-friendly terms to specific node types without requiring hardcoded aliases.

## How It Works

### Resolution Strategy (in order)

1. **Context-Aware Matching** (highest priority)
   - Uses component name and context to infer the specific node type
   - Example: `subnet` + `"Public Subnet"` → `public_subnet`
   - Example: `subnet` + `"Private Subnet"` → `private_subnet`

2. **Exact Match**
   - Direct lookup in registry

3. **Normalized Match**
   - Matches after normalizing (removing underscores, hyphens, case)

4. **Fuzzy Matching**
   - Uses string similarity (60% threshold)
   - Example: `subnets` → `subnet`

5. **Keyword Matching**
   - Matches based on keyword overlap from descriptions
   - Example: `database` → `rds` or `dynamodb` based on context

## Examples

### Network Components

```python
# Generic term with context
resolve("subnet", "Public Subnet") → "public_subnet"
resolve("subnet", "Private Subnet") → "private_subnet"
resolve("subnet", "App Subnet") → "private_subnet" (defaults to private)

# Plural forms
resolve("subnets") → "subnet"
resolve("vpcs") → "vpc"
```

### Database Components

```python
# Generic terms
resolve("database", "Relational DB") → "rds"
resolve("database", "NoSQL DB") → "dynamodb"
resolve("db") → None (too ambiguous, needs context)
```

### Compute Components

```python
# Context-based
resolve("function", "Serverless Function") → "lambda"
resolve("function", "Container Function") → "ecs"
resolve("function", "Kubernetes Function") → "eks"
```

## Context Patterns

The resolver recognizes common patterns:

- **Subnets**: `public`, `external`, `dmz` → `public_subnet`
- **Subnets**: `private`, `internal`, `app`, `data` → `private_subnet`
- **Databases**: `relational`, `sql` → `rds`
- **Databases**: `nosql`, `document`, `key-value` → `dynamodb`
- **Functions**: `serverless` → `lambda`
- **Functions**: `container` → `ecs`
- **Functions**: `kubernetes` → `eks`

## Benefits

1. **No Hardcoded Aliases** - Dynamic resolution based on context
2. **User-Friendly** - Accepts natural language terms
3. **Intelligent** - Uses component names and descriptions for context
4. **Flexible** - Handles plurals, variations, and synonyms
5. **Helpful Errors** - Suggests similar nodes when no match found

## Implementation

The `IntelligentNodeResolver` is integrated into `ComponentResolver`:

```python
# ComponentResolver automatically uses intelligent resolution
resolver = ComponentResolver("aws")
component = Component(id="subnet1", name="Public Subnet", type="subnet")
node_class = resolver.resolve_component_class(component)
# Automatically resolves "subnet" → "public_subnet" based on name
```

## Adding New Patterns

To add new context patterns, edit `intelligent_resolver.py`:

```python
context_patterns = {
    "your_pattern": {
        "hint1": "mapped_node1",
        "hint2": "mapped_node2",
    },
}
```

The resolver will automatically use these patterns when matching.

