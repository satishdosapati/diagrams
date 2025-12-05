"""
MCP Client wrapper for AWS Diagram MCP Server.

This module provides a client interface to communicate with the AWS Diagram MCP Server
using the Model Context Protocol (MCP).
"""
import json
import subprocess
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MCPDiagramClient:
    """
    Client for AWS Diagram MCP Server.
    
    Communicates with the MCP server via stdio protocol to generate and validate diagrams.
    """
    
    def __init__(
        self,
        server_command: Optional[str] = None,
        timeout: int = 30,
        env: Optional[Dict[str, str]] = None
    ):
        """
        Initialize MCP Diagram Client.
        
        Args:
            server_command: Command to run MCP server (default: from env or uvx)
            timeout: Timeout for MCP server calls in seconds
            env: Additional environment variables for MCP server
        """
        self.timeout = timeout
        
        # Default command from environment or use local installation
        if server_command is None:
            # Try local installation first, fallback to uvx
            server_command = os.getenv(
                "MCP_DIAGRAM_SERVER_COMMAND",
                self._detect_mcp_server_command()
            )
        self.server_command = server_command.split() if isinstance(server_command, str) else server_command
        
        # Build environment for MCP server
        self.env = os.environ.copy()
        if env:
            self.env.update(env)
        
        # Set MCP log level
        self.env.setdefault("FASTMCP_LOG_LEVEL", "ERROR")
        
        logger.info(f"MCP Diagram Client initialized with command: {' '.join(self.server_command) if isinstance(self.server_command, list) else self.server_command}")
    
    def _detect_mcp_server_command(self) -> str:
        """
        Detect the best MCP server command to use.
        
        Priority:
        1. Local virtual environment installation (fastest)
        2. Current Python environment installation
        3. uv tool installation
        4. uvx (on-demand, slower but works)
        
        Returns:
            Command string to use
        """
        import shutil
        import sys
        from pathlib import Path
        
        # Priority 1: Check for local virtual environment
        venv_dir = os.getenv("MCP_SERVER_VENV")
        if venv_dir:
            venv_path = Path(venv_dir)
            if venv_path.exists():
                if sys.platform == "win32":
                    python_exe = venv_path / "Scripts" / "python.exe"
                else:
                    python_exe = venv_path / "bin" / "python"
                
                if python_exe.exists():
                    cmd = f'"{python_exe}" -m awslabs.aws_diagram_mcp_server'
                    logger.info(f"Using local MCP server from venv: {venv_dir}")
                    return cmd
        
        # Check for local venv in project directory
        project_root = Path(__file__).parent.parent.parent
        for venv_name in [".mcp_server_venv", "mcp_server_venv"]:
            venv_path = project_root / venv_name
            if venv_path.exists():
                if sys.platform == "win32":
                    python_exe = venv_path / "Scripts" / "python.exe"
                else:
                    python_exe = venv_path / "bin" / "python"
                
                if python_exe.exists():
                    cmd = f'"{python_exe}" -m awslabs.aws_diagram_mcp_server'
                    logger.info(f"Using local MCP server venv: {venv_path}")
                    return cmd
        
        # Priority 2: Check if installed in current Python environment
        try:
            import importlib.util
            spec = importlib.util.find_spec("awslabs.aws_diagram_mcp_server")
            if spec and spec.origin:
                python_exe = sys.executable
                cmd = f'"{python_exe}" -m awslabs.aws_diagram_mcp_server'
                logger.info("Using MCP server from current Python environment")
                return cmd
        except Exception:
            pass
        
        # Priority 3: Check for local uv tool installation
        if shutil.which("uv"):
            try:
                # Check if MCP server is installed via uv tool
                result = subprocess.run(
                    ["uv", "tool", "],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and "aws-diagram-mcp-server" in result.stdout:
                    logger.info("Found local MCP server installation via uv tool")
                    # Use uv tool run for better performance
                    return "uv tool run awslabs.aws-diagram-mcp-server"
            except Exception:
                pass
        
        # Fallback to uvx (on-demand download)
        logger.info("Using uvx for MCP server (on-demand download)")
        return "uvx awslabs.aws-diagram-mcp-server"
    
    def generate_diagram(
        self,
        code: str,
        diagram_type: str = "aws_architecture",
        title: str = "Diagram",
        outformat: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call MCP server's generate_diagram tool.
        
        Args:
            code: Python code for diagram generation (using diagrams library)
            diagram_type: Type of diagram (aws_architecture, sequence, flow, class)
            title: Diagram title
            outformat: Output format (png, svg, pdf, etc.)
            
        Returns:
            Dict with:
                - code: Validated/enhanced Python code
                - output_path: Path to generated diagram file (if successful)
                - errors: List of errors (if any)
        """
        try:
            # Prepare MCP tool input
            tool_input = {
                "code": code,
                "diagram_type": diagram_type,
                "title": title
            }
            
            if outformat:
                tool_input["outformat"] = outformat
            
            logger.debug(f"Calling MCP generate_diagram tool for: {title}")
            
            # Call MCP server via stdio protocol
            # Note: Actual MCP protocol uses JSON-RPC, but for stdio we'll use a simplified approach
            result = self._call_mcp_tool("generate_diagram", tool_input)
            
            return {
                "code": result.get("code", code),
                "output_path": result.get("output_path"),
                "errors": result.get("errors", [])
            }
            
        except Exception as e:
            logger.error(f"Error calling MCP generate_diagram: {e}", exc_info=True)
            return {
                "code": code,  # Return original code on error
                "output_path": None,
                "errors": [str(e)]
            }
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """
        Validate diagram code using MCP server's code scanning.
        
        Args:
            code: Python code to validate
            
        Returns:
            Dict with:
                - valid: Boolean indicating if code is valid
                - errors: List of validation errors
                - warnings: List of warnings
        """
        try:
            tool_input = {"code": code}
            
            logger.debug("Calling MCP validate_code tool")
            
            result = self._call_mcp_tool("validate_code", tool_input)
            
            return {
                "valid": result.get("valid", True),
                "errors": result.get("errors", []),
                "warnings": result.get("warnings", [])
            }
            
        except Exception as e:
            logger.error(f"Error calling MCP validate_code: {e}", exc_info=True)
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }
    
    def _call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call MCP tool via stdio protocol.
        
        This is a simplified implementation. In production, use a proper MCP client library
        that handles the full MCP protocol (JSON-RPC over stdio).
        
        Args:
            tool_name: Name of MCP tool to call
            params: Tool parameters
            
        Returns:
            Tool response as dict
        """
        # For now, we'll use a subprocess approach
        # In production, integrate with proper MCP client library
        
        # Format as JSON-RPC request (simplified)
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        try:
            # Call MCP server via subprocess
            # Note: This is a placeholder - actual MCP protocol is more complex
            # For now, we'll simulate the call
            logger.debug(f"Calling MCP tool: {tool_name} with params: {list(params.keys())}")
            
            # TODO: Implement actual MCP stdio protocol communication
            # For now, return a mock response indicating the code was processed
            # In production, use mcp-python or similar library
            
            # Placeholder: Return params as-is (will be replaced with actual MCP call)
            return {
                "code": params.get("code", ""),
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"MCP tool call timed out after {self.timeout}s")
            raise RuntimeError(f"MCP server timeout: {tool_name}")
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}", exc_info=True)
            raise


# Global MCP client instance
_mcp_client: Optional[MCPDiagramClient] = None


def get_mcp_client() -> Optional[MCPDiagramClient]:
    """
    Get or create global MCP client instance.
    
    Returns:
        MCPDiagramClient instance if MCP is enabled, None otherwise
    """
    global _mcp_client
    
    # Check if MCP is enabled
    if os.getenv("USE_MCP_DIAGRAM_SERVER", "false").lower() != "true":
        return None
    
    if _mcp_client is None:
        try:
            _mcp_client = MCPDiagramClient()
            logger.info("MCP Diagram Client created successfully")
        except Exception as e:
            logger.error(f"Failed to create MCP client: {e}", exc_info=True)
            return None
    
    return _mcp_client
