"""
API routes for diagram generation (MVP).
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
import logging
import traceback

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

# In-memory storage for current specs (session-based)
current_specs: dict[str, ArchitectureSpec] = {}


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


@router.post("/generate-diagram", response_model=GenerateDiagramResponse)
async def generate_diagram(request: GenerateDiagramRequest):
    """
    Generate architecture diagram from natural language description.
    
    Args:
        request: Diagram generation request with description
        
    Returns:
        Response with diagram URL
    """
    try:
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
        
        # Apply outformat override if provided
        if request.outformat:
            spec.outformat = request.outformat
        
        # Generate diagram using universal generator
        diagram_path = generator.generate(spec)
        
        # Create session and store spec
        session_id = str(uuid.uuid4())
        current_specs[session_id] = spec
        
        # Return relative URL (will be served as static file)
        diagram_filename = os.path.basename(diagram_path)
        diagram_url = f"/api/diagrams/{diagram_filename}"
        
        return GenerateDiagramResponse(
            diagram_url=diagram_url,
            message=f"Successfully generated diagram: {spec.title}",
            session_id=session_id
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


@router.get("/diagrams/{filename}")
async def get_diagram(filename: str):
    """
    Serve generated diagram file.
    
    Args:
        filename: Diagram filename
        
    Returns:
        Diagram image file
    """
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    file_path = os.path.join(output_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    return FileResponse(file_path)


@router.post("/modify-diagram", response_model=ModifyDiagramResponse)
async def modify_diagram(request: ModifyDiagramRequest):
    """
    Modify existing diagram based on chat message.
    
    Args:
        request: Modification request with session ID and modification text
        
    Returns:
        Response with updated diagram and changes
    """
    try:
        # Get current spec
        current_spec = current_specs.get(request.session_id)
        if not current_spec:
            raise HTTPException(
                status_code=404,
                detail="Session not found. Please generate a diagram first."
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
        current_specs[request.session_id] = updated_spec
        
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


@router.post("/undo-diagram", response_model=ModifyDiagramResponse)
async def undo_diagram(request: UndoDiagramRequest):
    """
    Undo last modification (simplified - just returns current spec).
    In full implementation, would maintain history stack.
    """
    try:
        current_spec = current_specs.get(request.session_id)
        if not current_spec:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
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


@router.post("/validate-code", response_model=ValidateCodeResponse)
async def validate_code(request: ValidateCodeRequest):
    """
    Validate Python code syntax and check for common errors.
    
    Args:
        request: Code validation request
        
    Returns:
        Validation result with errors and suggestions
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

