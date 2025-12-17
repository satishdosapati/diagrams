"""
API routes for diagram generation (MVP).
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from starlette.requests import Request
from pydantic import BaseModel, Field, field_validator
import os
import uuid
import logging
import traceback
from pathlib import Path
import re

from typing import Optional, Union, List, Literal
from ..agents.diagram_agent import DiagramAgent
from ..agents.prompt_rewriter_agent import PromptRewriterAgent
from ..generators.universal_generator import UniversalGenerator
from ..models.spec import ArchitectureSpec, GraphvizAttributes
from ..storage.feedback_storage import FeedbackStorage
from ..services.log_capture import get_log_capture

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize agents and generator
agent = DiagramAgent()
prompt_rewriter_agent = PromptRewriterAgent()
generator = UniversalGenerator()

# Initialize feedback storage
feedback_storage = FeedbackStorage()

# Cache for DiagramsEngine and ComponentResolver instances per provider
# Format: {provider: {"engine": DiagramsEngine, "resolver": ComponentResolver}}
_engine_cache: dict[str, dict] = {}

# In-memory storage for current specs (session-based)
# Format: {session_id: {"spec": ArchitectureSpec, "created_at": float, "last_accessed": float}}
current_specs: dict[str, dict] = {}

# Session expiration time (1 hour)
SESSION_EXPIRY_SECONDS = 3600

# Cleanup old sessions periodically
import time
_last_cleanup = time.time()
CLEANUP_INTERVAL = 300  # 5 minutes

def _cleanup_expired_sessions():
    """Remove expired sessions from memory."""
    global _last_cleanup
    current_time = time.time()
    
    # Only cleanup every CLEANUP_INTERVAL seconds
    if current_time - _last_cleanup < CLEANUP_INTERVAL:
        return
    
    _last_cleanup = current_time
    expired_sessions = [
        session_id for session_id, session_data in current_specs.items()
        if current_time - session_data.get("last_accessed", 0) > SESSION_EXPIRY_SECONDS
    ]
    
    for session_id in expired_sessions:
        del current_specs[session_id]
        logger.info(f"Cleaned up expired session: {session_id}")
    
    if expired_sessions:
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

def _get_session_spec(session_id: str) -> Optional[ArchitectureSpec]:
    """Get spec from session, updating last_accessed timestamp."""
    session_data = current_specs.get(session_id)
    if not session_data:
        return None
    
    # Check if session expired
    current_time = time.time()
    if current_time - session_data.get("last_accessed", 0) > SESSION_EXPIRY_SECONDS:
        del current_specs[session_id]
        logger.info(f"Session expired: {session_id}")
        return None
    
    # Update last accessed time
    session_data["last_accessed"] = current_time
    return session_data["spec"]

def _update_session_spec(session_id: str, spec: ArchitectureSpec):
    """Update spec in session."""
    if session_id in current_specs:
        current_specs[session_id]["spec"] = spec
        current_specs[session_id]["last_accessed"] = time.time()


class GraphvizAttrsRequest(BaseModel):
    """Graphviz attributes request model."""
    graph_attr: Optional[dict] = None
    node_attr: Optional[dict] = None
    edge_attr: Optional[dict] = None


class GenerateDiagramRequest(BaseModel):
    """Request model for diagram generation."""
    description: str
    provider: str = "aws"  # Default to AWS for backward compatibility
    graphviz_attrs: Optional[GraphvizAttrsRequest] = None
    direction: Optional[Literal["TB", "BT", "LR", "RL"]] = None
    outformat: Optional[Union[str, List[str]]] = None


class GenerateDiagramResponse(BaseModel):
    """Response model for diagram generation."""
    diagram_url: str
    message: str
    session_id: str
    generation_id: str  # Unique ID for this generation (for feedback)
    generated_code: Optional[str] = None


class RegenerateFormatRequest(BaseModel):
    """Request model for regenerating diagram in different format."""
    session_id: str
    outformat: str
    direction: Optional[Literal["TB", "BT", "LR", "RL"]] = None


class ExecuteCodeRequest(BaseModel):
    """Request model for direct code execution."""
    code: str
    provider: str = "aws"
    title: str = "Diagram"
    outformat: Optional[str] = "png"


class ExecuteCodeResponse(BaseModel):
    """Response model for code execution."""
    diagram_url: str
    message: str
    errors: List[str] = []
    warnings: List[str] = []


class ValidateCodeRequest(BaseModel):
    """Request model for code validation."""
    code: str


class ValidateCodeResponse(BaseModel):
    """Response model for code validation."""
    valid: bool
    errors: List[str] = []
    suggestions: List[str] = []


class SubmitFeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    generation_id: str
    session_id: str
    thumbs_up: bool = Field(..., description="Thumbs up (true) or thumbs down (false)")
    code_hash: Optional[str] = None
    code: Optional[str] = None  # Optional: include code for pattern extraction
    
    @field_validator('thumbs_up')
    @classmethod
    def validate_thumbs_up(cls, v):
        """Validate thumbs_up is a boolean."""
        if not isinstance(v, bool):
            raise ValueError("thumbs_up must be a boolean (true or false)")
        return v


class FeedbackResponse(BaseModel):
    """Response model for feedback submission."""
    feedback_id: str
    message: str


class RewritePromptRequest(BaseModel):
    """Request model for prompt rewriting."""
    description: str = Field(..., description="Original architecture description")
    provider: str = Field(..., description="Cloud provider (aws, azure, gcp)")


class SuggestedCluster(BaseModel):
    """Suggested cluster grouping."""
    name: str
    components: List[str]
    pattern: Optional[str] = None


class RewritePromptResponse(BaseModel):
    """Response model for prompt rewriting."""
    rewritten_description: str
    improvements: List[str]
    components_identified: List[str]
    suggested_clusters: List[SuggestedCluster]


@router.post("/rewrite-prompt", response_model=RewritePromptResponse, tags=["diagrams"])
async def rewrite_prompt(request: RewritePromptRequest, http_request: Request = None):
    """
    Rewrite architecture prompt with clustering guidance and icon availability checks.
    
    This endpoint enhances user prompts by:
    - Adding clustering hints for better diagram organization
    - Checking icon availability and preferring available components
    - Identifying architectural patterns
    - Suggesting component groupings
    
    **Example Request:**
    ```json
    {
        "description": "serverless app with api gateway lambda dynamodb",
        "provider": "aws"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "rewritten_description": "Create a serverless architecture with Amazon API Gateway, AWS Lambda functions, and Amazon DynamoDB. Group API Gateway in the API Layer cluster...",
        "improvements": ["Added full AWS service names", "Identified serverless pattern"],
        "components_identified": ["api_gateway", "lambda", "dynamodb"],
        "suggested_clusters": [...]
    }
    ```
    
    Args:
        request: Prompt rewriting request containing description and provider
        http_request: FastAPI request object (for request ID tracking)
    
    Returns:
        RewritePromptResponse with rewritten prompt and clustering suggestions
    
    Raises:
        HTTPException: If rewriting fails (500) or input is invalid (400)
    """
    try:
        # Get request ID for logging
        request_id = getattr(http_request.state, 'request_id', 'unknown') if http_request else 'unknown'
        logger.info(f"[{request_id}] === Starting prompt rewrite ===")
        logger.info(f"[{request_id}] Provider: {request.provider}")
        logger.info(f"[{request_id}] Description length: {len(request.description)} characters")
        
        # Validate input
        if not request.description or not request.description.strip():
            raise HTTPException(
                status_code=400,
                detail="Description cannot be empty"
            )
        
        if request.provider not in ["aws", "azure", "gcp"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider: {request.provider}. Must be one of: aws, azure, gcp"
            )
        
        # Rewrite prompt
        try:
            result = prompt_rewriter_agent.rewrite(request.description, request.provider)
            logger.info(f"[{request_id}] Prompt rewritten successfully")
            logger.debug(f"[{request_id}] Improvements: {result.get('improvements', [])}")
            logger.debug(f"[{request_id}] Components identified: {result.get('components_identified', [])}")
            logger.debug(f"[{request_id}] Clusters suggested: {len(result.get('suggested_clusters', []))}")
            
            return RewritePromptResponse(**result)
        except Exception as rewrite_error:
            logger.error(f"[{request_id}] ERROR in prompt rewrite: {rewrite_error}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to rewrite prompt: {str(rewrite_error)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in rewrite_prompt: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/generate-diagram", response_model=GenerateDiagramResponse, tags=["diagrams"])
async def generate_diagram(request: GenerateDiagramRequest, http_request: Request = None):
    """
    Generate architecture diagram from natural language description.
    
    This endpoint uses AI to convert a natural language description into a cloud architecture diagram.
    Supports AWS, Azure, and GCP providers with multiple output formats.
    
    **Example Request:**
    ```json
    {
        "description": "VPC with EC2 instance and RDS database",
        "provider": "aws",
        "outformat": "png"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "diagram_url": "/api/diagrams/my_diagram.png",
        "message": "Successfully generated diagram: My Architecture",
        "session_id": "uuid-here",
        "generated_code": "from diagrams import Diagram..."
    }
    ```
    
    Args:
        request: Diagram generation request containing:
            - description: Natural language description of the architecture
            - provider: Cloud provider (aws, azure, gcp)
            - outformat: Output format (png, svg, pdf, dot)
            - graphviz_attrs: Optional Graphviz styling attributes
            - direction: (Deprecated - always uses LR for left-to-right layout)
        http_request: FastAPI request object (for request ID tracking)
    
    Returns:
        GenerateDiagramResponse with:
            - diagram_url: URL to access the generated diagram
            - message: Success message
            - session_id: Session ID for subsequent modifications
            - generated_code: Python code used to generate the diagram
    
    Raises:
        HTTPException: If diagram generation fails (500) or input is invalid (400)
    """
    try:
        # Get request ID for logging
        request_id = getattr(http_request.state, 'request_id', 'unknown') if http_request else 'unknown'
        logger.info(f"[{request_id}] === Starting diagram generation ===")
        logger.info(f"[{request_id}] Provider: {request.provider}")
        logger.info(f"[{request_id}] Description length: {len(request.description)} characters")
        
        # Check MCP status
        from ..integrations.mcp_diagram_client import get_mcp_client
        mcp_client = get_mcp_client()
        if mcp_client.enabled:
            logger.info(f"[{request_id}] MCP Diagram Server: ENABLED")
        else:
            logger.debug(f"[{request_id}] MCP Diagram Server: DISABLED")
        
        # Generate spec from description (pass provider from UI)
        # Provider from UI takes precedence - no need to detect or override
        logger.debug(f"[{request_id}] Calling agent.generate_spec with provider={request.provider}")
        try:
            spec = agent.generate_spec(request.description, provider=request.provider)
            logger.info(f"[{request_id}] Spec generated: {len(spec.components)} components, {len(spec.connections)} connections")
            logger.debug(f"[{request_id}] Spec provider: {spec.provider}, title: {spec.title}")
            if spec.components:
                logger.debug(f"[{request_id}] Component types: {[c.get_node_id() for c in spec.components[:5]]}")
        except Exception as spec_error:
            logger.error(f"[{request_id}] ERROR in spec generation: {spec_error}", exc_info=True)
            logger.error(f"[{request_id}] Provider: {request.provider}, Description: {request.description[:100]}")
            raise
        
        # Apply Graphviz attributes if provided
        if request.graphviz_attrs:
            graphviz_attrs = GraphvizAttributes(
                graph_attr=request.graphviz_attrs.graph_attr or {},
                node_attr=request.graphviz_attrs.node_attr or {},
                edge_attr=request.graphviz_attrs.edge_attr or {}
            )
            spec.graphviz_attrs = graphviz_attrs
        
        # Always use left-to-right direction for all diagrams
        # This ensures consistent, professional diagram layout
        spec.direction = "LR"
        
        # Apply outformat override if provided (normalize invalid formats)
        if request.outformat:
            from ..generators.diagrams_engine import normalize_format_list
            spec.outformat = normalize_format_list(request.outformat)
        
        # Generate diagram using universal generator
        logger.debug(f"[{request_id}] Calling generator.generate with provider={spec.provider}")
        try:
            diagram_path = generator.generate(spec)
            logger.info(f"[{request_id}] Diagram generated successfully: {diagram_path}")
        except Exception as gen_error:
            logger.error(f"[{request_id}] ERROR in diagram generation: {gen_error}", exc_info=True)
            logger.error(f"[{request_id}] Spec details - Provider: {spec.provider}, Components: {len(spec.components)}, Connections: {len(spec.connections)}")
            if spec.components:
                logger.error(f"[{request_id}] Component details: {[(c.id, c.get_node_id(), c.provider) for c in spec.components]}")
            raise
        
        # Generate Python code for Advanced Code Mode (use cached instances)
        from ..generators.diagrams_engine import DiagramsEngine
        from ..resolvers.component_resolver import ComponentResolver
        
        # Get or create cached engine and resolver for this provider
        if spec.provider not in _engine_cache:
            _engine_cache[spec.provider] = {
                "engine": DiagramsEngine(),
                "resolver": None  # Single resolver per provider
            }
        
        engine = _engine_cache[spec.provider]["engine"]
        
        # ComponentResolver is provider-specific, cache per provider
        if _engine_cache[spec.provider]["resolver"] is None:
            try:
                _engine_cache[spec.provider]["resolver"] = ComponentResolver(primary_provider=spec.provider)
            except Exception as e:
                logger.error(f"Failed to create ComponentResolver for {spec.provider}: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize resolver for provider '{spec.provider}': {str(e)}"
                )
        
        resolver = _engine_cache[spec.provider]["resolver"]
        logger.debug(f"[{request_id}] Generating code with resolver for provider={spec.provider}")
        try:
            generated_code = engine._generate_code(spec, resolver)
            logger.debug(f"[{request_id}] Code generated successfully, length: {len(generated_code)}")
        except Exception as code_error:
            logger.error(f"[{request_id}] ERROR in code generation: {code_error}", exc_info=True)
            logger.error(f"[{request_id}] Failed to generate code for provider={spec.provider}")
            if spec.components:
                logger.error(f"[{request_id}] Problematic components: {[(c.id, c.name, c.get_node_id()) for c in spec.components]}")
            raise
        
        # Create session and store spec with timestamp
        session_id = str(uuid.uuid4())
        generation_id = str(uuid.uuid4())  # Unique ID for this generation
        current_time = time.time()
        current_specs[session_id] = {
            "spec": spec,
            "created_at": current_time,
            "last_accessed": current_time,
            "generation_id": generation_id  # Store generation_id with session
        }
        
        # Cleanup old sessions periodically
        _cleanup_expired_sessions()
        
        # Return relative URL (will be served as static file)
        diagram_filename = os.path.basename(diagram_path)
        diagram_url = f"/api/diagrams/{diagram_filename}"
        
        return GenerateDiagramResponse(
            diagram_url=diagram_url,
            message=f"Successfully generated diagram: {spec.title}",
            session_id=session_id,
            generation_id=generation_id,
            generated_code=generated_code
        )
    
    except ValueError as e:
        # Validation errors (non-cloud requests, invalid input) - return 400
        request_id = getattr(http_request.state, 'request_id', 'unknown') if http_request else 'unknown'
        error_msg = str(e)
        logger.error(f"[{request_id}] Validation error (400): {error_msg}")
        logger.error(f"[{request_id}] Request details - Provider: {request.provider if hasattr(request, 'provider') else 'N/A'}, Description length: {len(request.description) if hasattr(request, 'description') else 'N/A'}")
        # Include more context in error for debugging
        if os.getenv("DEBUG", "false").lower() == "true":
            import traceback
            logger.error(f"[{request_id}] Validation error traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=400,
            detail=error_msg
        )
    except Exception as e:
        # Unexpected backend failures - return 500
        request_id = getattr(http_request.state, 'request_id', 'unknown') if http_request else 'unknown'
        logger.error(f"[{request_id}] Error generating diagram: {str(e)}", exc_info=True)
        error_detail = str(e)
        # Include traceback in detail for debugging (can be removed in production)
        if os.getenv("DEBUG", "false").lower() == "true":
            error_detail += f"\n\nTraceback:\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diagram: {error_detail}"
        )


@router.get("/diagrams/{filename}", tags=["diagrams"])
async def get_diagram(filename: str, request: Request):
    """
    Serve generated diagram file.
    
    Retrieve a previously generated diagram file by filename.
    Files are served from the configured OUTPUT_DIR.
    
    **Example:**
    ```
    GET /api/diagrams/my_architecture.png
    ```
    
    Args:
        filename: Diagram filename (e.g., "my_architecture.png")
    
    Returns:
        FileResponse: The diagram file (image or DOT source)
    
    Raises:
        HTTPException:
            - 400: Invalid filename format
            - 403: Path traversal attempt detected
            - 404: Diagram file not found
    """
    # Security: Validate filename to prevent path traversal
    # Check for path traversal FIRST (security-critical)
    if not filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Check raw request path (catches path traversal before normalization)
    # Request is now required, so we can always check the raw path
    raw_path = str(request.url.path)
    # Check for path traversal patterns in the raw URL path
    if '..' in raw_path or '/../' in raw_path or raw_path.endswith('/..'):
        raise HTTPException(status_code=400, detail="Invalid file path: path traversal detected")
    
    # Check for excessive path depth (more than /api/diagrams/{filename})
    # Normalized paths should have exactly 3 path segments: ['api', 'diagrams', '{filename}']
    path_parts = [p for p in raw_path.split('/') if p]
    if len(path_parts) != 3 or path_parts[0] != 'api' or path_parts[1] != 'diagrams':
        # Path structure is wrong - could be path traversal attempt
        raise HTTPException(status_code=400, detail="Invalid file path: path traversal detected")
    
    # Validate filename length (prevent filesystem errors)
    if len(filename) > 255:  # Common filesystem limit
        raise HTTPException(status_code=400, detail="Filename too long (maximum 255 characters)")
    
    # Prevent directory traversal attacks - check filename for dangerous patterns FIRST
    # This catches cases where FastAPI might have normalized the path parameter
    dangerous_patterns = ['..', '/', '\\', '\x00']
    if any(pattern in filename for pattern in dangerous_patterns):
        raise HTTPException(status_code=400, detail="Invalid file path: path traversal detected")
    
    # Prevent absolute paths and hidden files
    if filename.startswith('.') or filename.startswith('/') or (len(filename) > 1 and filename[1] == ':'):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Validate filename format (alphanumeric, dots, underscores, hyphens only)
    # Note: dots are allowed for file extensions, but we've already checked for '..' above
    if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        raise HTTPException(status_code=400, detail="Invalid filename format")
    
    output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
    file_path = output_dir / filename
    
    # Security: Ensure file is within output directory (double-check)
    try:
        resolved_path = file_path.resolve()
        resolved_output_dir = output_dir.resolve()
        resolved_path.relative_to(resolved_output_dir)
    except ValueError:
        # Path is outside output directory - security violation
        raise HTTPException(status_code=403, detail="Invalid file path: outside allowed directory")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    # Determine media type based on file extension for proper content-type headers
    media_type = None
    filename_lower = filename.lower()
    if filename_lower.endswith('.svg'):
        media_type = "image/svg+xml"
    elif filename_lower.endswith('.png'):
        media_type = "image/png"
    elif filename_lower.endswith('.pdf'):
        media_type = "application/pdf"
    elif filename_lower.endswith('.dot'):
        media_type = "text/plain; charset=utf-8"
    
    return FileResponse(str(file_path), media_type=media_type)


@router.post("/regenerate-format", response_model=GenerateDiagramResponse, tags=["diagrams"])
async def regenerate_format(request: RegenerateFormatRequest):
    """
    Regenerate diagram in a different output format.
    
    Convert an existing diagram to a different format without regenerating from scratch.
    Useful for downloading diagrams in multiple formats.
    
    **Example Request:**
    ```json
    {
        "session_id": "uuid-from-previous-request",
        "outformat": "svg"
    }
    ```
    
    **Supported Formats:**
    - png: PNG image (default)
    - svg: Scalable Vector Graphics
    - pdf: PDF document
    - dot: Graphviz DOT source code
    
    Args:
        request: Regeneration request containing:
            - session_id: Session ID from previous diagram generation
            - outformat: Desired output format
    
    Returns:
        GenerateDiagramResponse with new diagram URL
    
    Raises:
        HTTPException:
            - 404: Session not found or expired
            - 500: Regeneration failed
    """
    try:
        # Get session data (not just spec) to retrieve generation_id
        session_data = current_specs.get(request.session_id)
        if not session_data:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired"
            )
        
        # Check if session expired
        current_time = time.time()
        if current_time - session_data.get("last_accessed", 0) > SESSION_EXPIRY_SECONDS:
            del current_specs[request.session_id]
            logger.info(f"Session expired: {request.session_id}")
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired"
            )
        
        # Update last accessed time
        session_data["last_accessed"] = current_time
        current_spec = session_data["spec"]
        generation_id = session_data.get("generation_id", str(uuid.uuid4()))  # Fallback to new ID if missing
        
        # Create a copy of the spec with new format (normalize invalid formats)
        from copy import deepcopy
        from ..generators.diagrams_engine import normalize_format_list
        spec_copy = deepcopy(current_spec)
        spec_copy.outformat = normalize_format_list(request.outformat)
        
        # Update direction if provided
        if request.direction:
            spec_copy.direction = request.direction
            # Also update rankdir in graph_attr for Graphviz compatibility
            if not spec_copy.graphviz_attrs:
                spec_copy.graphviz_attrs = GraphvizAttributes()
            spec_copy.graphviz_attrs.graph_attr["rankdir"] = request.direction
        
        # Regenerate diagram with new format and/or direction
        diagram_path = generator.generate(spec_copy)
        
        # Return relative URL
        diagram_filename = os.path.basename(diagram_path)
        diagram_url = f"/api/diagrams/{diagram_filename}"
        
        return GenerateDiagramResponse(
            diagram_url=diagram_url,
            message=f"Diagram regenerated in {request.outformat.upper()} format",
            session_id=request.session_id,
            generation_id=generation_id,
            generated_code=None  # Don't regenerate code, just the diagram
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is (e.g., 404 for session not found)
        raise
    except Exception as e:
        logger.error(f"Error regenerating format: {str(e)}", exc_info=True)
        error_detail = str(e)
        if os.getenv("DEBUG", "false").lower() == "true":
            error_detail += f"\n\nTraceback:\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate diagram: {error_detail}"
        )


@router.post("/execute-code", response_model=ExecuteCodeResponse)
async def execute_code(request: ExecuteCodeRequest):
    """
    Execute Python code directly to generate diagram (Advanced Code Mode).
    
    Args:
        request: Code execution request with Python code
        
    Returns:
        Response with diagram URL or errors
    """
    try:
        # Security: Check for dangerous patterns
        dangerous_patterns = [
            'eval(',
            'exec(',
            '__import__',
            'open(',
            'file(',
            'input(',
            'raw_input(',
            'compile(',
            'reload(',
            'execfile(',
            'subprocess',
            'os.system',
            'os.popen',
            'os.spawn',
            'os.exec',
            'popen2',
            'commands',
            'urllib.urlopen',
            'urllib2.urlopen',
            'httplib',
            'socket',
            'sys.exit',
        ]
        
        code_lower = request.code.lower()
        security_warnings = []
        security_errors = []
        
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                # Critical patterns should be errors, not warnings
                if pattern in ['eval(', 'exec(', '__import__', 'os.system', 'os.popen', 'os.spawn', 'os.exec', 'subprocess']:
                    security_errors.append(f"Dangerous pattern detected: {pattern}")
                else:
                    security_warnings.append(f"Potentially dangerous pattern detected: {pattern}")
        
        # Check for SSRF patterns (URLs with localhost/internal IPs)
        import re
        url_patterns = re.findall(r'https?://[^\s\'"]+', request.code, re.IGNORECASE)
        for url in url_patterns:
            url_lower = url.lower()
            if any(blocked in url_lower for blocked in ['localhost', '127.0.0.1', '0.0.0.0', '192.168.', '10.', '172.']):
                security_errors.append(f"SSRF attempt detected: {url}")
        
        # If critical security errors found, reject
        if security_errors:
            return ExecuteCodeResponse(
                diagram_url="",
                message="Code execution blocked due to security concerns",
                errors=security_errors,
                warnings=security_warnings
            )
        
        from ..generators.diagrams_engine import DiagramsEngine
        
        engine = DiagramsEngine()
        
        # Execute code directly
        output_path = engine._execute_code(
            request.code,
            request.title,
            request.outformat
        )
        
        # Return diagram URL
        diagram_filename = os.path.basename(output_path)
        diagram_url = f"/api/diagrams/{diagram_filename}"
        
        return ExecuteCodeResponse(
            diagram_url=diagram_url,
            message="Code executed successfully",
            errors=[],
            warnings=security_warnings if security_warnings else []
        )
    
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}", exc_info=True)
        error_msg = str(e)
        
        # Try to extract more specific error information
        errors = [error_msg]
        if "STDERR:" in error_msg:
            # Extract stderr content
            stderr_start = error_msg.find("STDERR:")
            errors = [error_msg[stderr_start:].strip()]
        
        return ExecuteCodeResponse(
            diagram_url="",
            message="Code execution failed",
            errors=errors,
            warnings=[]
        )


@router.get("/completions/{provider}")
async def get_completions(provider: str):
    """
    Get available classes and imports for auto-completion.
    
    Args:
        provider: Cloud provider (aws, azure, gcp)
        
    Returns:
        Dictionary of available classes organized by category
        
    Raises:
        HTTPException: 400 if provider is invalid
    """
    # Validate provider
    valid_providers = {"aws", "azure", "gcp"}
    if provider.lower() not in valid_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider: '{provider}'. Supported providers: {', '.join(sorted(valid_providers))}"
        )
    
    try:
        from ..resolvers.library_discovery import LibraryDiscovery
        
        discovery = LibraryDiscovery(provider.lower())
        all_classes = discovery.get_all_available_classes()
        
        # Organize by category
        completions = {}
        imports_map = {}
        
        # Get module categories
        module_categories = discovery.module_categories
        
        for category, module_path in module_categories.items():
            classes = all_classes.get(module_path, set())
            if classes:
                class_list = sorted(list(classes))
                completions[category] = class_list
                
                # Build import map
                for class_name in class_list:
                    imports_map[class_name] = f"from {module_path} import {class_name}"
        
        return {
            "classes": completions,
            "imports": imports_map,
            "keywords": ["Diagram", "Cluster", "Edge"],
            "operators": [">>", "<<", "-"]
        }
    
    except Exception as e:
        logger.error(f"Error getting completions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get completions: {str(e)}"
        )


@router.post("/validate-code", response_model=ValidateCodeResponse, tags=["code"])
async def validate_code(request: ValidateCodeRequest):
    """
    Validate Python code syntax and check for common errors.
    
    Validates Python code before execution. Checks for:
    - Syntax errors
    - Missing imports
    - Undefined variables in connections
    
    **Example Request:**
    ```json
    {
        "code": "from diagrams import Diagram\\nfrom diagrams.aws.compute import EC2"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "valid": true,
        "errors": [],
        "suggestions": []
    }
    ```
    
    Args:
        request: Validation request containing:
            - code: Python code to validate
    
    Returns:
        ValidateCodeResponse with:
            - valid: Whether code is valid
            - errors: List of error messages
            - suggestions: List of improvement suggestions
    
    Raises:
        HTTPException: 500 if validation process fails
    """
    try:
        import ast
        import re
        
        errors = []
        suggestions = []
        
        # Basic syntax check and parse AST tree
        tree = None
        try:
            tree = ast.parse(request.code)
        except SyntaxError as e:
            errors.append(f"Syntax error: {e.msg} at line {e.lineno}")
            suggestions.append(f"Check syntax around line {e.lineno}")
            return ValidateCodeResponse(
                valid=False,
                errors=errors,
                suggestions=suggestions
            )
        
        # Check for common issues
        code_lower = request.code.lower()
        
        # Check if Diagram is imported
        if "with diagram" in code_lower and "from diagrams import" not in code_lower:
            suggestions.append("Add: from diagrams import Diagram")
        
        # Check for common import patterns
        if re.search(r'\b(ec2|lambda|s3|rds)\b', code_lower, re.IGNORECASE):
            if "from diagrams" not in code_lower:
                suggestions.append("Add imports for components (e.g., from diagrams.aws.compute import EC2)")
        
        # Check for undefined variables in connections
        # Use AST to properly detect all variable assignments (including lists)
        # This matches how Python actually parses code and handles all valid patterns
        # from the official diagrams library examples
        defined_vars = set()
        if tree is not None:
            try:
                # Use the AST tree from syntax check
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                defined_vars.add(target.id)
            except Exception as e:
                # Fallback to regex if AST walking fails
                var_pattern_single = r'(\w+)\s*=\s*\w+\('
                var_pattern_list = r'(\w+)\s*=\s*\['
                defined_vars = set(re.findall(var_pattern_single, request.code))
                defined_vars.update(re.findall(var_pattern_list, request.code))
                logger.warning(f"AST walking failed, using regex fallback: {e}")
        else:
            # Fallback to regex if tree is None (shouldn't happen after syntax check)
            var_pattern_single = r'(\w+)\s*=\s*\w+\('
            var_pattern_list = r'(\w+)\s*=\s*\['
            defined_vars = set(re.findall(var_pattern_single, request.code))
            defined_vars.update(re.findall(var_pattern_list, request.code))
        
        # Check connection operators
        connection_pattern = r'(\w+)\s*[><-]+\s*(\w+)'
        connections = re.findall(connection_pattern, request.code)
        
        # Filter out connections that are part of inline lists (e.g., ELB >> [EC2, EC2] >> RDS)
        # These are valid patterns from official examples and shouldn't trigger errors
        valid_connections = []
        for from_var, to_var in connections:
            # Skip validation for Edge and Cluster (these are imported classes, not variables)
            if from_var in ['Edge', 'Cluster'] or to_var in ['Edge', 'Cluster']:
                continue
            
            # Find the actual match position to check context
            for match in re.finditer(connection_pattern, request.code):
                if match.group(1) == from_var and match.group(2) == to_var:
                    # Check if this connection involves an inline list
                    match_start = match.start()
                    before_full = request.code[:match_start]
                    after_full = request.code[match.end():]
                    
                    # Count brackets to see if we're inside a list
                    open_brackets = before_full.count('[') - before_full.count(']')
                    if open_brackets > 0:
                        # We're inside brackets (inline list), skip validation
                        # This handles patterns like: ELB("lb") >> [EC2("w1"), EC2("w2")] >> RDS("db")
                        continue
                    
                    # Check if the connection ends with a bracket (inline list on right side)
                    if after_full.strip().startswith('['):
                        # Pattern like: var >> [node1, node2]
                        continue
                    
                    valid_connections.append((from_var, to_var))
                    break
        
        # Validate connections
        for from_var, to_var in valid_connections:
            if from_var not in defined_vars:
                errors.append(f"Undefined variable '{from_var}' used in connection")
            if to_var not in defined_vars:
                errors.append(f"Undefined variable '{to_var}' used in connection")
        
        return ValidateCodeResponse(
            valid=len(errors) == 0,
            errors=errors,
            suggestions=suggestions
        )
    
    except Exception as e:
        logger.error(f"Error validating code: {str(e)}", exc_info=True)
        return ValidateCodeResponse(
            valid=False,
            errors=[f"Validation error: {str(e)}"],
            suggestions=[]
        )


@router.post("/feedback", response_model=FeedbackResponse, tags=["feedback"])
async def submit_feedback(request: SubmitFeedbackRequest):
    """
    Submit thumbs up/down feedback for a diagram generation.
    
    Args:
        request: Feedback request with generation_id, session_id, and thumbs_up
        
    Returns:
        FeedbackResponse with feedback_id
    """
    try:
        # Calculate code hash if code provided
        code_hash = None
        if request.code:
            import hashlib
            code_hash = hashlib.sha256(request.code.encode('utf-8')).hexdigest()
        elif request.code_hash:
            code_hash = request.code_hash
        
        # Save feedback
        feedback_id = feedback_storage.save_feedback(
            generation_id=request.generation_id,
            session_id=request.session_id,
            thumbs_up=request.thumbs_up,
            code_hash=code_hash,
            code=request.code
        )
        
        logger.info(f"Feedback submitted: {feedback_id} - {'👍' if request.thumbs_up else '👎'} for generation {request.generation_id}")
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            message="Thank you for your feedback!"
        )
    
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/error-logs/{request_id}", tags=["errors"])
async def get_error_logs(request_id: str):
    """
    Get logs for a specific request ID.
    Used for error reporting.
    
    Args:
        request_id: Request identifier from X-Request-ID header
        
    Returns:
        JSON with request_id and logs array
    """
    log_capture = get_log_capture()
    
    # Try to get logs for this specific request
    logs = log_capture.get_logs(request_id)
    
    # If no logs found for this request, return last 50 logs as fallback
    if not logs:
        logs = log_capture.get_last_n_logs(50)
        logger.warning(f"No logs found for request_id {request_id}, returning last 50 logs")
    
    return {
        "request_id": request_id,
        "logs": logs,
        "last_50_lines": len(logs) <= 50
    }


@router.get("/feedback/stats", tags=["feedback"])
async def get_feedback_stats(days: int = 30):
    """
    Get feedback statistics.
    
    Args:
        days: Number of days to look back (default: 30)
        
    Returns:
        Dictionary with feedback statistics
    """
    try:
        stats = feedback_storage.get_feedback_stats(days=days)
        return stats
    except Exception as e:
        logger.error(f"Error getting feedback stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get feedback stats: {str(e)}"
        )

