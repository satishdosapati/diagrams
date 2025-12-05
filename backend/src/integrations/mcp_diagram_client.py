"""
MCP Client wrapper for AWS Diagram MCP Server.

This module provides a Python interface to interact with the AWS Diagram MCP Server
for diagram code generation, validation, and enhancement.
"""
import os
import json
import subprocess
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPDiagramClient:
    """
    Client for AWS Diagram MCP Server.
    
    Provides methods to interact with MCP server tools for diagram generation.
    """
    
    def __init__(self, server_command: Optional[str] = None):
        """
        Initialize MCP Diagram Client.
        
        Args:
            server_command: Optional custom MCP server command.
                          Defaults to environment variable or standard command.
        """
        self.server_command = server_command or os.getenv(
            "MCP_DIAGRAM_SERVER_COMMAND",
            "uvx awslabs.aws-diagram-mcp-server"
        )
        self.enabled = os.getenv("USE_MCP_DIAGRAM_SERVER", "false").lower() == "true"
        
        logger.info(f"[MCP] MCPDiagramClient initialized")
        logger.info(f"[MCP] Enabled: {self.enabled}")
        logger.info(f"[MCP] Server command: {self.server_command}")
    
    def generate_diagram(
        self,
        code: str,
        diagram_type: str = "aws_architecture",
        title: str = "Diagram"
    ) -> Dict[str, Any]:
        """
        Call MCP server's generate_diagram tool to generate/validate diagram code.
        
        Args:
            code: Python code for diagram generation (using diagrams library)
            diagram_type: Type of diagram (aws_architecture, sequence, flow, class)
            title: Diagram title
            
        Returns:
            Dict with:
            - 'code': Validated/enhanced Python code
            - 'success': Boolean indicating success
            - 'error': Error message if failed
            - 'output_path': Path to generated diagram (if successful)
        """
        if not self.enabled:
            logger.debug("[MCP] MCP server disabled, skipping generate_diagram call")
            return {
                "code": code,
                "success": False,
                "error": "MCP server disabled",
                "output_path": None
            }
        
        logger.info(f"[MCP] === Calling generate_diagram tool ===")
        logger.info(f"[MCP] Diagram type: {diagram_type}")
        logger.info(f"[MCP] Title: {title}")
        logger.debug(f"[MCP] Code length: {len(code)} characters")
        
        try:
            # Prepare MCP tool input
            tool_input = {
                "code": code,
                "diagram_type": diagram_type,
                "title": title
            }
            
            logger.debug(f"[MCP] Tool input prepared: {json.dumps(tool_input, indent=2)[:500]}...")
            
            # Call MCP server via subprocess (stdio protocol)
            # Note: In production, use proper MCP client library
            result = self._call_mcp_tool("generate_diagram", tool_input)
            
            if result.get("success"):
                logger.info("[MCP] generate_diagram succeeded")
                logger.debug(f"[MCP] Response: {result.get('code', '')[:200]}...")
                return result
            else:
                logger.warning(f"[MCP] generate_diagram failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"[MCP] Error calling generate_diagram: {e}", exc_info=True)
            return {
                "code": code,
                "success": False,
                "error": str(e),
                "output_path": None
            }
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """
        Validate diagram code using MCP server's code scanning.
        
        Args:
            code: Python code to validate
            
        Returns:
            Dict with validation results
        """
        if not self.enabled:
            logger.debug("[MCP] MCP server disabled, skipping validate_code call")
            return {
                "valid": True,
                "error": None,
                "warnings": []
            }
        
        logger.info("[MCP] === Calling validate_code ===")
        logger.debug(f"[MCP] Code length: {len(code)} characters")
        
        try:
            tool_input = {"code": code}
            result = self._call_mcp_tool("validate_code", tool_input)
            
            if result.get("valid"):
                logger.info("[MCP] Code validation passed")
            else:
                logger.warning(f"[MCP] Code validation failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"[MCP] Error validating code: {e}", exc_info=True)
            return {
                "valid": False,
                "error": str(e),
                "warnings": []
            }
    
    def _call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call MCP tool via stdio protocol.
        
        This is a simplified implementation. In production, use proper MCP client library.
        
        Args:
            tool_name: Name of MCP tool to call
            params: Tool parameters
            
        Returns:
            Tool response as dict
        """
        logger.debug(f"[MCP] Calling MCP tool: {tool_name}")
        logger.debug(f"[MCP] Parameters: {json.dumps(params, indent=2)[:300]}...")
        
        try:
            # For now, we'll use a placeholder approach
            # Actual MCP protocol requires proper client library
            # This implementation shows the structure but may need adjustment
            
            # Option 1: If MCP server supports direct tool calls via CLI
            # result = subprocess.run(
            #     [self.server_command, tool_name],
            #     input=json.dumps(params),
            #     capture_output=True,
            #     text=True,
            #     timeout=30
            # )
            
            # Option 2: Use MCP Python SDK (if available)
            # from mcp import Client
            # client = Client(self.server_command)
            # result = client.call_tool(tool_name, params)
            
            # For quick test: Return input code as-is with success flag
            # This allows testing the integration flow without full MCP server setup
            logger.info(f"[MCP] Tool call simulated (MCP server integration pending)")
            logger.info(f"[MCP] Tool: {tool_name}, Params keys: {list(params.keys())}")
            
            # Return simulated success response
            return {
                "code": params.get("code", ""),
                "success": True,
                "error": None,
                "output_path": None,
                "valid": True,
                "warnings": []
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"[MCP] Tool call timeout: {tool_name}")
            return {
                "success": False,
                "error": "MCP server timeout",
                "code": params.get("code", "")
            }
        except Exception as e:
            logger.error(f"[MCP] Error calling MCP tool {tool_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "code": params.get("code", "")
            }


# Global client instance
_mcp_client: Optional[MCPDiagramClient] = None


def get_mcp_client() -> MCPDiagramClient:
    """Get or create global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPDiagramClient()
    return _mcp_client
