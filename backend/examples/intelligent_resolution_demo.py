#!/usr/bin/env python3
"""
Demonstration of Intelligent Node Resolution

This script shows how generic terms are intelligently resolved to specific node types.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.resolvers.component_resolver import ComponentResolver
from src.models.spec import Component


def print_resolution(component: Component, resolver: ComponentResolver):
    """Resolve and print component resolution."""
    try:
        node_class = resolver.resolve_component_class(component)
        print(f"  ✓ '{component.type}' + '{component.name}' → {node_class.__name__}")
        return True
    except Exception as e:
        print(f"  ✗ '{component.type}' + '{component.name}' → ERROR: {e}")
        return False


def main():
    print("=" * 70)
    print("Intelligent Node Resolution - Examples")
    print("=" * 70)
    print()
    
    resolver = ComponentResolver("aws")
    
    # Example 1: Subnet Resolution
    print("Example 1: Subnet Resolution (Context-Aware)")
    print("-" * 70)
    
    examples = [
        Component(id="sub1", name="Public Subnet", type="subnet"),
        Component(id="sub2", name="Private Subnet", type="subnet"),
        Component(id="sub3", name="External Subnet", type="subnet"),
        Component(id="sub4", name="Internal Subnet", type="subnet"),
        Component(id="sub5", name="App Subnet", type="subnet"),
        Component(id="sub6", name="Subnet", type="subnet"),  # No context
    ]
    
    for comp in examples:
        print_resolution(comp, resolver)
    print()
    
    # Example 2: Plural/Variation Handling
    print("Example 2: Plural and Variation Handling (Fuzzy Matching)")
    print("-" * 70)
    
    examples = [
        Component(id="subs", name="Subnets", type="subnets"),  # Plural
        Component(id="vpc1", name="VPCs", type="vpcs"),  # Plural
        Component(id="api1", name="API Gateway", type="api-gateway"),  # Hyphen
        Component(id="api2", name="API Gateway", type="api_gateway"),  # Underscore
    ]
    
    for comp in examples:
        print_resolution(comp, resolver)
    print()
    
    # Example 3: Database Resolution
    print("Example 3: Database Resolution (Context-Aware)")
    print("-" * 70)
    
    examples = [
        Component(id="db1", name="Relational Database", type="database"),
        Component(id="db2", name="NoSQL Database", type="database"),
        Component(id="db3", name="Document Database", type="database"),
        Component(id="db4", name="DynamoDB Database", type="database"),
    ]
    
    for comp in examples:
        print_resolution(comp, resolver)
    print()
    
    # Example 4: Function Resolution
    print("Example 4: Function Resolution (Context-Aware)")
    print("-" * 70)
    
    examples = [
        Component(id="func1", name="Serverless Function", type="function"),
        Component(id="func2", name="Container Function", type="function"),
        Component(id="func3", name="Kubernetes Function", type="function"),
    ]
    
    for comp in examples:
        print_resolution(comp, resolver)
    print()
    
    # Example 5: Exact Matches (No Resolution Needed)
    print("Example 5: Exact Matches (No Resolution Needed)")
    print("-" * 70)
    
    examples = [
        Component(id="lambda1", name="Lambda Function", type="lambda"),
        Component(id="s31", name="S3 Bucket", type="s3"),
        Component(id="rds1", name="RDS Instance", type="rds"),
    ]
    
    for comp in examples:
        print_resolution(comp, resolver)
    print()
    
    # Example 6: Real Architecture Scenario
    print("Example 6: Real Architecture Scenario")
    print("-" * 70)
    print("User describes: 'A VPC with public and private subnets, API Gateway,")
    print("                 Lambda functions, and DynamoDB'")
    print()
    
    architecture = [
        Component(id="vpc", name="VPC", type="vpc"),
        Component(id="pub_sub", name="Public Subnet", type="subnet"),
        Component(id="priv_sub", name="Private Subnet", type="subnet"),
        Component(id="api", name="API Gateway", type="api_gateway"),
        Component(id="lambda", name="Lambda Function", type="function"),
        Component(id="db", name="DynamoDB", type="database"),
    ]
    
    print("Resolved components:")
    for comp in architecture:
        print_resolution(comp, resolver)
    print()
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()

