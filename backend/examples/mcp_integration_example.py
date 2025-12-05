"""
Example: Using MCP Diagram Server Integration

This example demonstrates how to use the MCP tools for diagram generation.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.spec import ArchitectureSpec, Component, Connection
from src.agents.mcp_tools import (
    generate_diagram_from_code,
    validate_diagram_code,
    generate_code_from_spec
)
from src.converters.spec_to_mcp import get_converter


def example_validate_code():
    """Example: Validate diagram code before execution."""
    print("=" * 60)
    print("Example 1: Validate Diagram Code")
    print("=" * 60)
    
    # Sample diagram code
    code = """
from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.network import APIGateway

with Diagram("Serverless Application", show=False):
    api = APIGateway("API Gateway")
    function = Lambda("Function")
    database = Dynamodb("DynamoDB")
    
    api >> function >> database
"""
    
    # Validate code
    result = validate_diagram_code(code)
    
    print(f"Valid: {result['valid']}")
    print(f"Message: {result['message']}")
    if result['errors']:
        print(f"Errors: {result['errors']}")
    if result['warnings']:
        print(f"Warnings: {result['warnings']}")
    print()


def example_generate_from_code():
    """Example: Generate diagram from Python code."""
    print("=" * 60)
    print("Example 2: Generate Diagram from Code")
    print("=" * 60)
    
    # Sample diagram code
    code = """
from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.network import APIGateway

with Diagram("Serverless API", show=False, filename="serverless_api"):
    api = APIGateway("API Gateway")
    function = Lambda("Function")
    database = Dynamodb("DynamoDB")
    
    api >> function >> database
"""
    
    # Generate diagram
    result = generate_diagram_from_code(
        code=code,
        title="Serverless API",
        diagram_type="aws_architecture",
        outformat="png"
    )
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['output_path']:
        print(f"Output: {result['output_path']}")
    if result['errors']:
        print(f"Errors: {result['errors']}")
    print()


def example_generate_from_spec():
    """Example: Generate code from ArchitectureSpec."""
    print("=" * 60)
    print("Example 3: Generate Code from ArchitectureSpec")
    print("=" * 60)
    
    # Create a simple ArchitectureSpec
    spec = ArchitectureSpec(
        title="Simple Serverless Architecture",
        provider="aws",
        components=[
            Component(id="api", name="API Gateway", type="api_gateway"),
            Component(id="lambda", name="Function", type="lambda"),
            Component(id="db", name="Database", type="dynamodb")
        ],
        connections=[
            Connection(from_id="api", to_id="lambda"),
            Connection(from_id="lambda", to_id="db")
        ]
    )
    
    # Generate code from spec
    result = generate_code_from_spec(spec)
    
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['code']:
        print("\nGenerated Code:")
        print("-" * 60)
        print(result['code'][:500] + "..." if len(result['code']) > 500 else result['code'])
        print("-" * 60)
    if result['errors']:
        print(f"Errors: {result['errors']}")
    print()


def example_full_workflow():
    """Example: Full workflow with spec → code → validate → generate."""
    print("=" * 60)
    print("Example 4: Full Workflow")
    print("=" * 60)
    
    # Step 1: Create ArchitectureSpec
    spec = ArchitectureSpec(
        title="Microservices Architecture",
        provider="aws",
        components=[
            Component(id="api", name="API Gateway", type="api_gateway"),
            Component(id="lambda1", name="Service 1", type="lambda"),
            Component(id="lambda2", name="Service 2", type="lambda"),
            Component(id="db", name="Database", type="dynamodb")
        ],
        connections=[
            Connection(from_id="api", to_id="lambda1"),
            Connection(from_id="api", to_id="lambda2"),
            Connection(from_id="lambda1", to_id="db"),
            Connection(from_id="lambda2", to_id="db")
        ]
    )
    
    print("Step 1: Created ArchitectureSpec")
    print(f"  - Title: {spec.title}")
    print(f"  - Components: {len(spec.components)}")
    print(f"  - Connections: {len(spec.connections)}")
    
    # Step 2: Convert to code
    result = generate_code_from_spec(spec)
    if not result['success']:
        print(f"Error generating code: {result['errors']}")
        return
    
    code = result['code']
    print("\nStep 2: Generated Python code")
    print(f"  - Code length: {len(code)} characters")
    
    # Step 3: Validate code
    validation = validate_diagram_code(code)
    print("\nStep 3: Validated code")
    print(f"  - Valid: {validation['valid']}")
    if validation['warnings']:
        print(f"  - Warnings: {len(validation['warnings'])}")
    
    # Step 4: Generate diagram (if validation passed)
    if validation['valid']:
        diagram_result = generate_diagram_from_code(
            code=code,
            title=spec.title,
            diagram_type="aws_architecture"
        )
        print("\nStep 4: Generated diagram")
        print(f"  - Success: {diagram_result['success']}")
        if diagram_result['output_path']:
            print(f"  - Output: {diagram_result['output_path']}")
    else:
        print("\nStep 4: Skipped (validation failed)")
    
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("MCP Diagram Server Integration Examples")
    print("=" * 60)
    print("\nNote: Ensure USE_MCP_DIAGRAM_SERVER=true is set to enable MCP tools")
    print()
    
    # Check if MCP is enabled
    mcp_enabled = os.getenv("USE_MCP_DIAGRAM_SERVER", "false").lower() == "true"
    if not mcp_enabled:
        print("WARNING: MCP Diagram Server is not enabled.")
        print("Set USE_MCP_DIAGRAM_SERVER=true to enable MCP tools.")
        print("\nExamples will still run but will show MCP not enabled messages.")
        print()
    
    try:
        example_validate_code()
        example_generate_from_code()
        example_generate_from_spec()
        example_full_workflow()
        
        print("=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
