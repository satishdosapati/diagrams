"""
MCP Client wrapper for AWS Diagram MCP Server.

This module provides a Python interface to interact with the AWS Diagram MCP Server
for diagram code generation, validation, and enhancement.

Implements MCP (Model Context Protocol) JSON-RPC 2.0 over stdio.
"""
import os
import json
import subprocess
import logging
import threading
import time
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path
from queue import Queue, Empty

logger = logging.getLogger(__name__)


class MCPDiagramClient:
    """
    Client for AWS Diagram MCP Server.
    
    Provides methods to interact with MCP server tools for diagram generation.
    Implements MCP JSON-RPC 2.0 protocol over stdio.
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
        
        # MCP server process and communication
        self._process: Optional[subprocess.Popen] = None
        self._request_id_counter = 0
        self._pending_requests: Dict[int, Queue] = {}
        self._response_reader_thread: Optional[threading.Thread] = None
        self._initialized = False
        self._lock = threading.Lock()
        
        # Parse server command into list for subprocess
        self._server_command_list, self._use_shell = self._parse_server_command(self.server_command)
        
        logger.info(f"[MCP] MCPDiagramClient initialized")
        logger.info(f"[MCP] Enabled: {self.enabled}")
        logger.info(f"[MCP] Server command: {self.server_command}")
        
        # Initialize connection if enabled
        if self.enabled:
            try:
                self._initialize_connection()
            except Exception as e:
                logger.error(f"[MCP] Failed to initialize MCP connection: {e}", exc_info=True)
                self.enabled = False
    
    def _parse_server_command(self, command: str) -> Tuple[List[str], bool]:
        """
        Parse server command string into list for subprocess.
        
        Handles commands like:
        - "uvx awslabs.aws-diagram-mcp-server"
        - "uv tool run awslabs.aws-diagram-mcp-server"
        
        Returns:
            Tuple of (command_list, use_shell)
        """
        # Check if command contains shell operators or needs shell
        if "|" in command or "&&" in command or ";" in command or "$" in command:
            return [command], True
        
        # Simple split for most cases
        return command.split(), False
    
    def _initialize_connection(self):
        """Initialize MCP server connection and perform handshake."""
        if self._process is not None:
            logger.debug("[MCP] Connection already initialized")
            return
        
        logger.info("[MCP] === Initializing MCP server connection ===")
        
        try:
            # Start MCP server process
            logger.debug(f"[MCP] Starting process: {self._server_command_list}")
            logger.debug(f"[MCP] Using shell: {self._use_shell}")
            
            self._process = subprocess.Popen(
                self._server_command_list,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                shell=self._use_shell,
                env=os.environ.copy()
            )
            
            # Start response reader thread
            self._response_reader_thread = threading.Thread(
                target=self._read_responses,
                daemon=True
            )
            self._response_reader_thread.start()
            
            # Start stderr reader thread (for error logging)
            self._stderr_reader_thread = threading.Thread(
                target=self._read_stderr,
                daemon=True
            )
            self._stderr_reader_thread.start()
            
            # Wait a moment for server to start
            time.sleep(0.5)
            
            # Check if process is still alive
            if self._process.poll() is not None:
                raise Exception(f"MCP server process died immediately after start. Exit code: {self._process.returncode}")
            
            # Send initialize request
            init_result = self._send_initialize()
            if init_result:
                # Send initialized notification
                self._send_initialized()
                self._initialized = True
                self._connection_retries = 0  # Reset retry counter on success
                logger.info("[MCP] Connection initialized successfully")
                
                # Optionally list available tools for debugging
                try:
                    tools = self.list_tools()
                    if tools:
                        tool_names = [t.get("name", "unknown") for t in tools]
                        logger.info(f"[MCP] Available tools: {', '.join(tool_names)}")
                except Exception as e:
                    logger.debug(f"[MCP] Could not list tools: {e}")
            else:
                raise Exception("Failed to initialize MCP server")
                
        except Exception as e:
            logger.error(f"[MCP] Error initializing connection: {e}", exc_info=True)
            self._cleanup_connection()
            raise
    
    def _send_initialize(self) -> bool:
        """Send initialize request to MCP server."""
        logger.debug("[MCP] Sending initialize request")
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "diagram-generator",
                    "version": "1.0.0"
                }
            }
        }
        
        response = self._send_request(request, timeout=10.0)
        if response and "result" in response:
            server_info = response.get("result", {}).get("serverInfo", {})
            logger.info(f"[MCP] Server initialized: {server_info.get('name', 'unknown')} v{server_info.get('version', 'unknown')}")
            return True
        
        if response and "error" in response:
            error = response["error"]
            logger.error(f"[MCP] Initialize failed: {error.get('message', 'Unknown error')}")
        
        return False
    
    def _send_initialized(self):
        """Send initialized notification to MCP server."""
        logger.debug("[MCP] Sending initialized notification")
        
        notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        try:
            if self._process and self._process.stdin:
                self._process.stdin.write(json.dumps(notification) + "\n")
                self._process.stdin.flush()
        except Exception as e:
            logger.error(f"[MCP] Error sending initialized notification: {e}")
    
    def _read_responses(self):
        """Background thread to read responses from MCP server."""
        logger.debug("[MCP] Response reader thread started")
        
        try:
            if not self._process or not self._process.stdout:
                return
            
            for line in self._process.stdout:
                if not line.strip():
                    continue
                
                try:
                    response = json.loads(line.strip())
                    request_id = response.get("id")
                    
                    if request_id is not None:
                        # This is a response to a request
                        if request_id in self._pending_requests:
                            self._pending_requests[request_id].put(response)
                        else:
                            logger.warning(f"[MCP] Received response for unknown request ID: {request_id}")
                    else:
                        # This is a notification (no ID)
                        logger.debug(f"[MCP] Received notification: {response.get('method', 'unknown')}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"[MCP] Failed to parse response JSON: {e}, line: {line[:100]}")
                except Exception as e:
                    logger.error(f"[MCP] Error processing response: {e}", exc_info=True)
                    
        except Exception as e:
            logger.error(f"[MCP] Response reader thread error: {e}", exc_info=True)
        finally:
            logger.debug("[MCP] Response reader thread ended")
    
    def _read_stderr(self):
        """Background thread to read stderr from MCP server."""
        logger.debug("[MCP] Stderr reader thread started")
        
        try:
            if not self._process or not self._process.stderr:
                return
            
            for line in self._process.stderr:
                if not line.strip():
                    continue
                
                # Log stderr output (MCP servers often log to stderr)
                logger.debug(f"[MCP] Server stderr: {line.strip()}")
                
        except Exception as e:
            logger.error(f"[MCP] Stderr reader thread error: {e}", exc_info=True)
        finally:
            logger.debug("[MCP] Stderr reader thread ended")
    
    def _get_next_request_id(self) -> int:
        """Get next unique request ID."""
        with self._lock:
            self._request_id_counter += 1
            return self._request_id_counter
    
    def _send_request(self, request: Dict[str, Any], timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """
        Send JSON-RPC request and wait for response.
        
        Args:
            request: JSON-RPC request dict
            timeout: Timeout in seconds
            
        Returns:
            Response dict or None if timeout/error
        """
        if not self._process or not self._process.stdin:
            logger.error("[MCP] Process not initialized")
            return None
        
        request_id = request.get("id")
        if request_id is None:
            logger.error("[MCP] Request missing ID")
            return None
        
        # Create queue for response
        response_queue = Queue()
        self._pending_requests[request_id] = response_queue
        
        try:
            # Send request
            request_json = json.dumps(request)
            logger.debug(f"[MCP] Sending request ID {request_id}: {request.get('method', 'unknown')}")
            self._process.stdin.write(request_json + "\n")
            self._process.stdin.flush()
            
            # Wait for response
            try:
                response = response_queue.get(timeout=timeout)
                return response
            except Empty:
                logger.error(f"[MCP] Request {request_id} timed out after {timeout}s")
                return None
                
        except Exception as e:
            logger.error(f"[MCP] Error sending request: {e}", exc_info=True)
            return None
        finally:
            # Cleanup
            self._pending_requests.pop(request_id, None)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from MCP server.
        
        Returns:
            List of tool definitions
        """
        if not self.enabled or not self._initialized:
            logger.debug("[MCP] Cannot list tools - MCP not enabled or initialized")
            return []
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": self._get_next_request_id(),
                "method": "tools/list"
            }
            
            response = self._send_request(request, timeout=10.0)
            if response and "result" in response:
                tools = response["result"].get("tools", [])
                logger.info(f"[MCP] Found {len(tools)} available tools")
                return tools
            return []
        except Exception as e:
            logger.error(f"[MCP] Error listing tools: {e}", exc_info=True)
            return []
    
    def _cleanup_connection(self):
        """Clean up MCP server connection."""
        logger.debug("[MCP] Cleaning up connection")
        
        if self._process:
            try:
                if self._process.stdin:
                    self._process.stdin.close()
                if self._process.stdout:
                    self._process.stdout.close()
                if self._process.stderr:
                    self._process.stderr.close()
                self._process.terminate()
                self._process.wait(timeout=5)
            except Exception as e:
                logger.warning(f"[MCP] Error during cleanup: {e}")
                try:
                    self._process.kill()
                except:
                    pass
            finally:
                self._process = None
        
        self._initialized = False
        self._pending_requests.clear()
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            self._cleanup_connection()
        except:
            pass
    
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
        Validate diagram code by attempting to generate diagram.
        
        Note: AWS Diagram MCP Server doesn't have a separate validate_code tool.
        We validate by attempting to generate the diagram and checking for errors.
        
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
        
        logger.info("[MCP] === Validating code via generate_diagram ===")
        logger.debug(f"[MCP] Code length: {len(code)} characters")
        
        try:
            # Use generate_diagram to validate (it will fail if code is invalid)
            tool_input = {
                "code": code,
                "diagram_type": "aws_architecture",
                "title": "Validation Test"
            }
            result = self._call_mcp_tool("generate_diagram", tool_input)
            
            # If generate_diagram succeeds, code is valid
            valid = result.get("success", False)
            error = result.get("error")
            
            if valid:
                logger.info("[MCP] Code validation passed")
            else:
                logger.warning(f"[MCP] Code validation failed: {error}")
            
            return {
                "valid": valid,
                "error": error,
                "warnings": result.get("warnings", [])
            }
            
        except Exception as e:
            logger.error(f"[MCP] Error validating code: {e}", exc_info=True)
            return {
                "valid": False,
                "error": str(e),
                "warnings": []
            }
    
    def _call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call MCP tool via JSON-RPC 2.0 stdio protocol.
        
        Args:
            tool_name: Name of MCP tool to call (e.g., "generate_diagram")
            params: Tool parameters
            
        Returns:
            Tool response as dict with standardized format
        """
        logger.debug(f"[MCP] Calling MCP tool: {tool_name}")
        logger.debug(f"[MCP] Parameters: {json.dumps(params, indent=2)[:300]}...")
        
        if not self.enabled:
            logger.debug("[MCP] MCP disabled, returning simulated response")
            return self._simulated_response(tool_name, params)
        
        # Ensure connection is initialized
        if not self._initialized or (self._process and self._process.poll() is not None):
            try:
                if self._process and self._process.poll() is not None:
                    logger.warning("[MCP] Process died, reinitializing...")
                    self._cleanup_connection()
                
                # Retry connection if needed
                if self._connection_retries < self._max_retries:
                    self._connection_retries += 1
                    logger.info(f"[MCP] Initializing connection (attempt {self._connection_retries})")
                    self._initialize_connection()
                else:
                    raise Exception(f"MCP server connection failed after {self._max_retries} retries")
            except Exception as e:
                logger.error(f"[MCP] Failed to initialize connection: {e}")
                return self._simulated_response(tool_name, params, error=str(e))
        
        try:
            # Check if process is still alive
            if self._process and self._process.poll() is not None:
                logger.warning("[MCP] Process died during tool call, reinitializing...")
                self._cleanup_connection()
                # Reinitialize
                try:
                    self._initialize_connection()
                except Exception as e:
                    logger.error(f"[MCP] Failed to reinitialize: {e}")
                    return self._simulated_response(tool_name, params, error=f"Process died and reinit failed: {e}")
            
            # Build JSON-RPC request
            request_id = self._get_next_request_id()
            request = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": params
                }
            }
            
            # Send request and get response
            response = self._send_request(request, timeout=30.0)
            
            if not response:
                logger.error(f"[MCP] No response received for tool {tool_name}")
                return self._simulated_response(tool_name, params, error="No response from MCP server")
            
            # Check for JSON-RPC error
            if "error" in response:
                error = response["error"]
                logger.error(f"[MCP] Tool call error: {error}")
                return self._simulated_response(
                    tool_name, 
                    params, 
                    error=f"MCP error: {error.get('message', 'Unknown error')}"
                )
            
            # Extract result
            result = response.get("result", {})
            
            # Parse result based on tool type
            if tool_name == "generate_diagram":
                return self._parse_generate_diagram_result(result, params)
            elif tool_name == "validate_code":
                return self._parse_validate_code_result(result, params)
            else:
                # Generic result parsing
                return {
                    "code": params.get("code", ""),
                    "success": True,
                    "error": None,
                    "output_path": result.get("output_path"),
                    "valid": True,
                    "warnings": []
                }
                
        except Exception as e:
            logger.error(f"[MCP] Error calling MCP tool {tool_name}: {e}", exc_info=True)
            return self._simulated_response(tool_name, params, error=str(e))
    
    def _parse_generate_diagram_result(self, result: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse generate_diagram tool result.
        
        MCP server may return:
        - result.content: List of content items (text, image, etc.)
        - result.isError: Boolean indicating if there was an error
        - Enhanced code or diagram file path
        """
        # MCP server returns result.content which may be a list of text/image parts
        content = result.get("content", [])
        is_error = result.get("isError", False)
        
        # Start with original code
        code = params.get("code", "")
        output_path = None
        warnings = []
        
        if is_error:
            # Extract error message from content
            error_msg = "Unknown error"
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        error_msg = item.get("text", error_msg)
                        break
            return {
                "code": code,
                "success": False,
                "error": error_msg,
                "output_path": None,
                "valid": False,
                "warnings": warnings
            }
        
        # Parse content items
        if isinstance(content, list) and len(content) > 0:
            for item in content:
                if not isinstance(item, dict):
                    continue
                
                item_type = item.get("type", "")
                item_text = item.get("text", "")
                
                if item_type == "text":
                    # Check if this is enhanced code
                    if "from diagrams" in item_text or "with Diagram" in item_text:
                        # This looks like Python code - use it as enhanced code
                        code = item_text
                        logger.debug("[MCP] Received enhanced code from MCP server")
                    elif "output" in item_text.lower() or "path" in item_text.lower() or "generated" in item_text.lower():
                        # Try to extract file path
                        import re
                        # Look for file paths
                        path_patterns = [
                            r'[\'"]([^\'"]+\.(png|svg|pdf|jpg|jpeg))[\'"]',  # Quoted paths
                            r'(/[^\s]+\.(png|svg|pdf|jpg|jpeg))',  # Absolute paths
                            r'([a-zA-Z0-9_\-/]+\.(png|svg|pdf|jpg|jpeg))'  # Relative paths
                        ]
                        for pattern in path_patterns:
                            path_match = re.search(pattern, item_text)
                            if path_match:
                                output_path = path_match.group(1)
                                logger.debug(f"[MCP] Extracted output path: {output_path}")
                                break
                    elif "warning" in item_text.lower():
                        warnings.append(item_text)
                
                elif item_type == "image":
                    # MCP server returned image directly
                    image_uri = item.get("data", "")
                    if image_uri:
                        # Could be data URI or file path
                        if image_uri.startswith("file://"):
                            output_path = image_uri[7:]  # Remove file:// prefix
                        elif image_uri.startswith("/"):
                            output_path = image_uri
        
        # If no enhanced code received, keep original
        # MCP server may have validated/enhanced it but not returned it
        return {
            "code": code,
            "success": True,
            "error": None,
            "output_path": output_path,
            "valid": True,
            "warnings": warnings
        }
    
    def _parse_validate_code_result(self, result: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Parse validate_code tool result."""
        content = result.get("content", [])
        
        valid = True
        error = None
        warnings = []
        
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text", "")
                    if "error" in text.lower() or "invalid" in text.lower():
                        valid = False
                        error = text
                    elif "warning" in text.lower():
                        warnings.append(text)
        
        return {
            "valid": valid,
            "error": error,
            "warnings": warnings
        }
    
    def _simulated_response(self, tool_name: str, params: Dict[str, Any], error: Optional[str] = None) -> Dict[str, Any]:
        """Return simulated response when MCP is disabled or fails."""
        if error:
            logger.warning(f"[MCP] Using simulated response due to error: {error}")
        else:
            logger.debug(f"[MCP] Using simulated response (MCP disabled or unavailable)")
        
        if tool_name == "validate_code":
            return {
                "valid": error is None,
                "error": error,
                "warnings": []
            }
        else:
            return {
                "code": params.get("code", ""),
                "success": error is None,
                "error": error,
                "output_path": None,
                "valid": True,
                "warnings": []
            }


# Global client instance
_mcp_client: Optional[MCPDiagramClient] = None


def get_mcp_client() -> MCPDiagramClient:
    """Get or create global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPDiagramClient()
    return _mcp_client
