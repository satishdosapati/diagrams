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

from ..agents.diagram_agent import DiagramAgent
from ..agents.modification_agent import ModificationAgent
from ..generators.universal_generator import UniversalGenerator
from ..models.spec import ArchitectureSpec

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize agents and generator
agent = DiagramAgent()
modification_agent = ModificationAgent()
generator = UniversalGenerator()

# In-memory storage for current specs (session-based)
current_specs: dict[str, ArchitectureSpec] = {}


class GenerateDiagramRequest(BaseModel):
    """Request model for diagram generation."""
    description: str
    provider: str = "aws"  # Default to AWS for backward compatibility


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

