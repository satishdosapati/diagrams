"""
API routes for diagram generation (MVP).
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
import os
import uuid
import logging
import traceback
from pathlib import Path
import re

from typing import Optional, Union, List, Literal
from ..agents.diagram_agent import DiagramAgent
from ..agents.modification_agent import ModificationAgent
from ..generators.universal_generator import UniversalGenerator
from ..models.spec import ArchitectureSpec, GraphvizAttributes

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize agents and generator
agent = DiagramAgent()
modification_agent = ModificationAgent()
generator = UniversalGenerator()

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
    generated_code: Optional[str] = None


class ModifyDiagramRequest(BaseModel):
    """Request model for diagram modification."""
    session_id: str
    modification: str


class ModifyDiagramResponse(BaseModel):
    """Response model for diagram modification."""
    diagram_url: str
    message: str
    changes: list[str]
    updated_spec: dict


class UndoDiagramRequest(BaseModel):
    """Request model for undo operation."""
    session_id: str


class RegenerateFormatRequest(BaseModel):
    """Request model for regenerating diagram in different format."""
    session_id: str
    outformat: str


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
            - direction: Optional diagram direction (LR, TB, etc.)
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
        logger.info(f"[{request_id}] Generating diagram for provider: {request.provider}")
        
        # Generate spec from description (pass provider from UI)
        # Provider from UI takes precedence - no need to detect or override
        spec = agent.generate_spec(request.description, provider=request.provider)
        
        # Apply Graphviz attributes if provided
        if request.graphviz_attrs:
            graphviz_attrs = GraphvizAttributes(
                graph_attr=request.graphviz_attrs.graph_attr or {},
                node_attr=request.graphviz_attrs.node_attr or {},
                edge_attr=request.graphviz_attrs.edge_attr or {}
            )
            spec.graphviz_attrs = graphviz_attrs
        
        # Apply direction override if provided
        if request.direction:
            spec.direction = request.direction
        
        # Apply outformat override if provided (normalize invalid formats)
        if request.outformat:
            from ..generators.diagrams_engine import normalize_format_list
            spec.outformat = normalize_format_list(request.outformat)
        
        # Generate diagram using universal generator
        diagram_path = generator.generate(spec)
        
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
        generated_code = engine._generate_code(spec, resolver)
        
        # Create session and store spec with timestamp
        session_id = str(uuid.uuid4())
        current_time = time.time()
        current_specs[session_id] = {
            "spec": spec,
            "created_at": current_time,
            "last_accessed": current_time
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
            generated_code=generated_code
        )
    
    except Exception as e:
        logger.error(f"Error generating diagram: {str(e)}", exc_info=True)
        error_detail = str(e)
        # Include traceback in detail for debugging (can be removed in production)
        if os.getenv("DEBUG", "false").lower() == "true":
            error_detail += f"\n\nTraceback:\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diagram: {error_detail}"
        )


@router.get("/diagrams/{filename}", tags=["diagrams"])
async def get_diagram(filename: str):
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
    if not filename or not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=403, detail="Invalid file path")
    
    output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
    file_path = output_dir / filename
    
    # Security: Ensure file is within output directory
    try:
        file_path.resolve().relative_to(output_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid file path")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    return FileResponse(str(file_path))


@router.post("/modify-diagram", response_model=ModifyDiagramResponse, tags=["diagrams"])
async def modify_diagram(request: ModifyDiagramRequest):
    """
    Modify existing diagram based on chat message.
    
    Use this endpoint to make changes to an existing diagram through natural language.
    Requires a valid session_id from a previous diagram generation.
    
    **Example Request:**
    ```json
    {
        "session_id": "uuid-from-previous-request",
        "modification": "Add a Lambda function between API Gateway and DynamoDB"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "diagram_url": "/api/diagrams/updated_diagram.png",
        "message": "Diagram modified successfully",
        "changes": ["Added Lambda function", "Updated connections"],
        "updated_spec": {...}
    }
    ```
    
    Args:
        request: Modification request containing:
            - session_id: Session ID from previous diagram generation
            - modification: Natural language description of desired changes
    
    Returns:
        ModifyDiagramResponse with:
            - diagram_url: URL to access the updated diagram
            - message: Success message
            - changes: List of changes made
            - updated_spec: Updated architecture specification
    
    Raises:
        HTTPException: 
            - 404: Session not found or expired
            - 500: Modification failed
    """
    try:
        # Get current spec
        current_spec = _get_session_spec(request.session_id)
        if not current_spec:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired. Please generate a diagram first."
            )
        
        # Modify spec
        updated_spec, changes = modification_agent.modify(
            request.session_id,
            current_spec,
            request.modification
        )
        
        # Generate updated diagram using universal generator
        diagram_path = generator.generate(updated_spec)
        
        # Update stored spec
        _update_session_spec(request.session_id, updated_spec)
        
        # Return response
        diagram_filename = os.path.basename(diagram_path)
        diagram_url = f"/api/diagrams/{diagram_filename}"
        
        return ModifyDiagramResponse(
            diagram_url=diagram_url,
            message="Diagram updated successfully",
            changes=changes,
            updated_spec=updated_spec.model_dump()
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error modifying diagram: {str(e)}", exc_info=True)
        error_detail = str(e)
        if os.getenv("DEBUG", "false").lower() == "true":
            error_detail += f"\n\nTraceback:\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=f"Failed to modify diagram: {error_detail}"
        )


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
        current_spec = _get_session_spec(request.session_id)
        if not current_spec:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired"
            )
        
        # Create a copy of the spec with new format (normalize invalid formats)
        from copy import deepcopy
        from ..generators.diagrams_engine import normalize_format_list
        spec_copy = deepcopy(current_spec)
        spec_copy.outformat = normalize_format_list(request.outformat)
        
        # Regenerate diagram with new format
        diagram_path = generator.generate(spec_copy)
        
        # Return relative URL
        diagram_filename = os.path.basename(diagram_path)
        diagram_url = f"/api/diagrams/{diagram_filename}"
        
        return GenerateDiagramResponse(
            diagram_url=diagram_url,
            message=f"Diagram regenerated in {request.outformat.upper()} format",
            session_id=request.session_id,
            generated_code=None  # Don't regenerate code, just the diagram
        )
    
    except Exception as e:
        logger.error(f"Error regenerating format: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate diagram: {str(e)}"
        )


@router.post("/undo-diagram", response_model=ModifyDiagramResponse)
async def undo_diagram(request: UndoDiagramRequest):
    """
    Undo last modification (simplified - just returns current spec).
    In full implementation, would maintain history stack.
    """
    try:
        current_spec = _get_session_spec(request.session_id)
        if not current_spec:
            raise HTTPException(
                status_code=404,
                detail="Session not found or expired"
            )
        
        # Regenerate diagram with current spec using universal generator
        diagram_path = generator.generate(current_spec)
        
        diagram_filename = os.path.basename(diagram_path)
        diagram_url = f"/api/diagrams/{diagram_filename}"
        
        return ModifyDiagramResponse(
            diagram_url=diagram_url,
            message="Diagram restored",
            changes=[],
            updated_spec=current_spec.model_dump()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to undo: {str(e)}"
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
            warnings=[]
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
    """
    try:
        from ..resolvers.library_discovery import LibraryDiscovery
        
        discovery = LibraryDiscovery(provider)
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
        
        # Basic syntax check
        try:
            ast.parse(request.code)
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
        # Extract variable names
        var_pattern = r'(\w+)\s*=\s*\w+\('
        defined_vars = set(re.findall(var_pattern, request.code))
        
        # Check connection operators
        connection_pattern = r'(\w+)\s*[><-]+\s*(\w+)'
        connections = re.findall(connection_pattern, request.code)
        
        for from_var, to_var in connections:
            if from_var not in defined_vars and from_var not in ['Edge', 'Cluster']:
                errors.append(f"Undefined variable '{from_var}' used in connection")
            if to_var not in defined_vars and to_var not in ['Edge', 'Cluster']:
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

