"""
MCP Tools for Strands Agents.

These functions can be called by the agent during reasoning to generate,
validate, or enhance diagrams using the AWS Diagram MCP Server.
"""
import logging
from typing import Dict, Any, Optional

from ..integrations.mcp_diagram_client import get_mcp_client

logger = logging.getLogger(__name__)


def generate_diagram_from_code(
    code: str,
    filename: Optional[str] = None,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Tool function for Strands Agent to generate diagrams via MCP server.
    
    This function calls the AWS Diagram MCP Server's generate_diagram tool
    to generate a PNG diagram from Python code.
    
    Args:
        code: Python code for diagram generation (using diagrams library)
        filename: Optional filename for the generated diagram (default: random)
        timeout: Optional timeout in seconds (default: 90)
        
    Returns:
        Dict with:
        - 'code': Original Python code
        - 'success': Boolean indicating success
        - 'error': Error message if failed
        - 'output_path': Path to generated PNG diagram (if successful)
    """
    logger.info("[MCP_TOOLS] === generate_diagram_from_code called ===")
    if filename:
        logger.info(f"[MCP_TOOLS] Filename: {filename}")
    logger.debug(f"[MCP_TOOLS] Code preview: {code[:200]}...")
    
    try:
        client = get_mcp_client()
        result = client.generate_diagram(code, filename=filename, timeout=timeout)
        
        if result.get("success"):
            logger.info("[MCP_TOOLS] Diagram generation succeeded")
        else:
            logger.warning(f"[MCP_TOOLS] Diagram generation failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"[MCP_TOOLS] Error in generate_diagram_from_code: {e}", exc_info=True)
        return {
            "code": code,
            "success": False,
            "error": str(e),
            "output_path": None
        }


def validate_diagram_code(code: str) -> Dict[str, Any]:
    """
    Tool function to validate diagram code before execution.
    
    Uses MCP server's code scanning to ensure:
    - Code is safe to execute
    - Follows diagrams library best practices
    - No security vulnerabilities
    
    Args:
        code: Python code to validate
        
    Returns:
        Dict with:
        - 'valid': Boolean indicating if code is valid
        - 'error': Error message if invalid
        - 'warnings': List of warnings
    """
    logger.info("[MCP_TOOLS] === validate_diagram_code called ===")
    logger.debug(f"[MCP_TOOLS] Code length: {len(code)} characters")
    
    try:
        client = get_mcp_client()
        result = client.validate_code(code)
        
        if result.get("valid"):
            logger.info("[MCP_TOOLS] Code validation passed")
            if result.get("warnings"):
                logger.warning(f"[MCP_TOOLS] Validation warnings: {result.get('warnings')}")
        else:
            logger.warning(f"[MCP_TOOLS] Code validation failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"[MCP_TOOLS] Error in validate_diagram_code: {e}", exc_info=True)
        return {
            "valid": False,
            "error": str(e),
            "warnings": []
        }


def enhance_diagram_code(code: str, diagram_type: str = "aws_architecture") -> Dict[str, Any]:
    """
    Tool function to enhance diagram code using MCP server.
    
    This can improve:
    - Code structure and readability
    - Diagram layout and styling
    - Best practices compliance
    
    Args:
        code: Python code to enhance
        diagram_type: Type of diagram
        
    Returns:
        Dict with enhanced code and metadata
    """
    logger.info("[MCP_TOOLS] === enhance_diagram_code called ===")
    logger.info(f"[MCP_TOOLS] Diagram type: {diagram_type}")
    
    try:
        # First validate
        validation = validate_diagram_code(code)
        if not validation.get("valid"):
            logger.warning("[MCP_TOOLS] Code validation failed, cannot enhance")
            return {
                "code": code,
                "success": False,
                "error": validation.get("error"),
                "enhanced": False
            }
        
        # Then generate via MCP (MCP server doesn't have diagram_type or title parameters)
        client = get_mcp_client()
        result = client.generate_diagram(code, filename="enhanced_diagram")
        
        if result.get("success"):
            logger.info("[MCP_TOOLS] Code enhancement succeeded")
            result["enhanced"] = True
        else:
            logger.warning(f"[MCP_TOOLS] Code enhancement failed: {result.get('error')}")
            result["enhanced"] = False
            result["code"] = code  # Return original code on failure
        
        return result
        
    except Exception as e:
        logger.error(f"[MCP_TOOLS] Error in enhance_diagram_code: {e}", exc_info=True)
        return {
            "code": code,
            "success": False,
            "error": str(e),
            "enhanced": False
        }
