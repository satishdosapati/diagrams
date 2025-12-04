# Architecture Advisor Consultation Flow

## Overview

The Architecture Advisor is now consulted **at multiple stages** during every modification to ensure architectural best practices are followed.

## Consultation Flow

### Stage 1: Pre-Modification Consultation (BEFORE Agent)

**When:** Before the LLM agent generates the modification

**What happens:**
1. Advisor analyzes the modification request
2. Provides specific guidance based on what's being added/modified
3. Guidance is included in the prompt to the LLM agent

**Example:**
```
User: "Add an EC2 instance"

Advisor Guidance:
- NOTE: If adding EC2 instances, ensure VPC and Subnet exist
- EC2 instances should be connected: VPC → Subnet → EC2
```

### Stage 2: Post-Modification Enhancement (AFTER Agent)

**When:** After the LLM agent generates the modification

**What happens:**
1. Advisor receives the updated spec
2. Enhances the spec with:
   - Component ordering (by architectural layers)
   - Missing connections (based on patterns)
   - Missing components (based on dependencies)
3. Logs advisor contributions

**Example:**
```
Agent generates: [EC2, VPC] (unordered, missing subnet)

Advisor enhances:
- Components: [VPC, Subnet, EC2] (ordered, subnet added)
- Connections: [VPC → Subnet, Subnet → EC2] (suggested)
```

## Implementation Details

### Pre-Modification Guidance (`_get_advisor_guidance`)

```python
def _get_advisor_guidance(self, spec: ArchitectureSpec, modification: str) -> str:
    """Get architectural guidance BEFORE modification."""
    # Analyzes modification request
    # Provides specific guidance based on components being added
    # Returns guidance string for LLM prompt
```

**Guidance Types:**
- **EC2 Addition**: Suggests VPC and Subnet dependencies
- **Lambda Addition**: Suggests API Gateway or EventBridge connections
- **RDS Addition**: Suggests VPC and Subnet dependencies
- **Connection Changes**: Suggests following AWS patterns

### Post-Modification Enhancement (`_enhance_with_advisor`)

```python
def _enhance_with_advisor(self, spec: ArchitectureSpec) -> ArchitectureSpec:
    """Enhance spec AFTER modification."""
    # Sorts components by architectural layers
    # Validates and suggests connections
    # Suggests missing components
    # Returns enhanced spec
```

**Enhancements:**
- Component ordering (left to right by layer)
- Connection validation and suggestions
- Missing component detection
- Pattern recognition

## Complete Flow Diagram

```
User Modification Request
    ↓
[STEP 1: Pre-Consultation]
Advisor analyzes request
→ Provides guidance for LLM
    ↓
LLM Agent generates modification
    ↓
[STEP 2: Post-Enhancement]
Advisor enhances spec:
→ Orders components
→ Adds missing connections
→ Suggests missing components
    ↓
Enhanced Spec returned
```

## Logging

The advisor consultation is logged at each stage:

```python
logger.info("Architecture advisor consulted for modification: ...")
logger.info("Consulting AWS Architectural Advisor for enhancement")
logger.info("Architecture advisor enhancements applied")
```

## Benefits

✅ **Proactive Guidance**: Advisor guides LLM BEFORE modification
✅ **Automatic Enhancement**: Advisor enhances AFTER modification
✅ **Consistent Architecture**: All modifications follow best practices
✅ **Complete Diagrams**: Missing components and connections are added
✅ **Proper Ordering**: Components are always logically ordered

## Example: Complete Flow

**User Request:** "Add a Lambda function"

**Step 1 - Pre-Consultation:**
```
Advisor Guidance:
- NOTE: Lambda functions commonly connect to API Gateway or EventBridge
- Consider adding these connections if they exist
```

**Step 2 - LLM Modification:**
```
LLM adds: Lambda component
```

**Step 3 - Post-Enhancement:**
```
Advisor enhances:
- Orders Lambda in compute layer
- Checks for API Gateway → Lambda connection
- Checks for Lambda → DynamoDB connection (if DynamoDB exists)
- Adds suggested connections
```

**Result:**
- Lambda added in correct position
- Connections follow AWS patterns
- Architecture remains consistent

## Provider Support

Currently implemented:
- ✅ **AWS**: Full advisor support

Future:
- ⏳ **Azure**: Advisor support (TODO)
- ⏳ **GCP**: Advisor support (TODO)

## Configuration

The advisor is always active for AWS modifications. No configuration needed.

For future MCP integration:
```bash
export USE_AWS_MCP=true  # Enables AWS Documentation MCP queries
```

