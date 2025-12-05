"""
MCP Tools for Strands Agents.

These tools can be registered with Strands Agents to enable direct diagram generation
and validation through the AWS Diagram MCP Server.
"""
import logging
from typing import Dict, Any, Optional

from ..integrations.mcp_client import get_mcp_client
from ..models.spec import ArchitectureSpec
from ..generators.diagrams_engine import DiagramsEngine
from ..resolvers.component_resolver import ComponentResolver
from ..converters.spec_to_mcp import get_converter

logger = logging.getLogger(__name__)


def generate_diagram_from_code(
    code: str,
    title: str = "Diagram",
    diagram_type: str = "aws_architecture",
    outformat: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tool function for Strands Agent to generate diagrams from Python code.
    
    This tool validates and generates diagrams using the AWS Diagram MCP Server.
    The agent can call this tool during reasoning to generate diagrams iteratively.
    
    Args:
        code: Python code using diagrams library DSL
        title: Diagram title
        diagram_type: Type of diagram (aws_architecture, sequence, flow, class)
        outformat: Output format (png, svg, pdf, etc.)
        
    Returns:
        Dict with:
            - success: Boolean indicating success
            - output_path: Path to generated diagram file
            - code: Validated/enhanced code
            - errors: List of errors (if any)
            - message: Human-readable message
    """
    mcp_client = get_mcp_client()
    
    if not mcp_client:
        return {
            "success": False,
            "output_path": None,
            "code": code,
            "errors": ["MCP Diagram Server is not enabled"],
            "message": "MCP Diagram Server is not enabled. Set USE_MCP_DIAGRAM_SERVER=true to enable."
        }
    
    try:
        logger.info(f"Agent calling generate_diagram_from_code for: {title}")
        
        # Call MCP server to generate diagram
        result = mcp_client.generate_diagram(
            code=code,
            diagram_type=diagram_type,
            title=title,
            outformat=outformat
        )
        
        if result.get("errors"):
            return {
                "success": False,
                "output_path": result.get("output_path"),
                "code": result.get("code", code),
                "errors": result["errors"],
                "message": f"Diagram generation failed: {', '.join(result['errors'])}"
            }
        
        return {
            "success": True,
            "output_path": result.get("output_path"),
            "code": result.get("code", code),
            "errors": [],
            "message": f"Diagram generated successfully: {result.get('output_path', 'N/A')}"
        }
        
    except Exception as e:
        logger.error(f"Error in generate_diagram_from_code tool: {e}", exc_info=True)
        return {
            "success": False,
            "output_path": None,
            "code": code,
            "errors": [str(e)],
            "message": f"Error generating diagram: {str(e)}"
        }


def validate_diagram_code(code: str) -> Dict[str, Any]:
    """
    Tool function for Strands Agent to validate diagram code before execution.
    
    This tool uses MCP server's code scanning to check for security issues,
    syntax errors, and best practices.
    
    Args:
        code: Python code to validate
        
    Returns:
        Dict with:
            - valid: Boolean indicating if code is valid
            - errors: List of validation errors
            - warnings: List of warnings
            - message: Human-readable validation result
    """
    mcp_client = get_mcp_client()
    
    if not mcp_client:
        return {
            "valid": True,  # Assume valid if MCP not enabled
            "errors": [],
            "warnings": [],
            "message": "MCP validation skipped (MCP not enabled)"
        }
    
    try:
        logger.info("Agent calling validate_diagram_code")
        
        result = mcp_client.validate_code(code)
        
        if result["valid"]:
            message = "Code validation passed"
            if result.get("warnings"):
                message += f" with {len(result['warnings'])} warning(s)"
        else:
            message = f"Code validation failed: {', '.join(result.get('errors', []))}"
        
        return {
            "valid": result["valid"],
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", []),
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Error in validate_diagram_code tool: {e}", exc_info=True)
        return {
            "valid": False,
            "errors": [str(e)],
            "warnings": [],
            "message": f"Error validating code: {str(e)}"
        }


def generate_code_from_spec(spec: ArchitectureSpec) -> Dict[str, Any]:
    """
    Tool function to convert ArchitectureSpec to Python code.
    
    This helper tool allows the agent to generate Python code from an ArchitectureSpec,
    which can then be validated and executed using other MCP tools.
    
    Args:
        spec: ArchitectureSpec object (can be passed as dict or ArchitectureSpec)
        
    Returns:
        Dict with:
            - code: Generated Python code
            - success: Boolean indicating success
            - errors: List of errors (if any)
            - message: Human-readable message
    """
    try:
        # Handle dict input (if agent passes dict instead of object)
        if isinstance(spec, dict):
            spec = ArchitectureSpec(**spec)
        
        logger.info(f"Agent calling generate_code_from_spec for: {spec.title}")
        
        # Use converter for consistent code generation
        converter = get_converter()
        code = converter.convert_to_code(spec)
        
        return {
            "code": code,
            "success": True,
            "errors": [],
            "message": f"Successfully generated code for '{spec.title}' ({len(code)} characters)"
        }
        
    except Exception as e:
        logger.error(f"Error in generate_code_from_spec tool: {e}", exc_info=True)
        return {
            "code": "",
            "success": False,
            "errors": [str(e)],
            "message": f"Error generating code: {str(e)}"
        }


def get_mcp_tools() -> list:
    """
    Get list of MCP tools for registration with Strands Agent.
    
    Returns:
        List of tool functions that can be registered with the agent
    """
    tools = [
        generate_diagram_from_code,
        validate_diagram_code,
        generate_code_from_spec
    ]
    
    return tools
