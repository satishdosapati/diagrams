"""
FastAPI application entry point for MVP.
"""
# IMPORTANT: Load .env file BEFORE any other imports that might use environment variables
from pathlib import Path
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try loading from current directory as fallback
    load_dotenv()

# Configure logging level (must be before other imports that log)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add log capture handler for error reporting
from src.services.log_capture import LogCaptureHandler
log_capture_handler = LogCaptureHandler()
log_capture_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(log_capture_handler)

logger = logging.getLogger(__name__)
logger.info(f"Environment loaded. USE_MCP_DIAGRAM_SERVER={os.getenv('USE_MCP_DIAGRAM_SERVER', 'not set')}")

# Now import other modules (they will have access to environment variables)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid
import time

from src.api.routes import router

app = FastAPI(
    title="Architecture Diagram Generator API",
    description="""
    Generate cloud architecture diagrams from natural language descriptions.
    
    ## Features
    
    * **Natural Language Processing**: Convert text descriptions into architecture diagrams
    * **Multi-Cloud Support**: AWS, Azure, and GCP
    * **Multiple Output Formats**: PNG, SVG, PDF, DOT
    * **Interactive Modifications**: Chat-based diagram modifications
    * **Advanced Code Mode**: Direct Python code editing
    
    ## Endpoints
    
    * `POST /api/generate-diagram`: Generate diagram from natural language
    * `POST /api/modify-diagram`: Modify existing diagram via chat
    * `POST /api/execute-code`: Execute Python code to generate diagram
    * `GET /api/diagrams/{filename}`: Retrieve generated diagram file
    * `POST /api/regenerate-format`: Regenerate diagram in different format
    * `GET /api/completions/{provider}`: Get code completions for provider
    * `POST /api/validate-code`: Validate Python code syntax
    
    ## Authentication
    
    Currently no authentication required. For production, add API keys or OAuth.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
# Allow all origins for flexibility (works with any EC2 instance IP)
# Frontend automatically detects the hostname and connects to backend on same hostname
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# Add EC2 public IP if provided via environment variable
EC2_PUBLIC_IP = os.getenv("EC2_PUBLIC_IP")
if EC2_PUBLIC_IP:
    allowed_origins.append(f"http://{EC2_PUBLIC_IP}:3000")

# Add FRONTEND_URL if provided
FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    allowed_origins.append(FRONTEND_URL)

# CORS configuration - restrict to known origins and localhost
# For production, set FRONTEND_URL environment variable with your domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|.*\.yourdomain\.com):3000" if os.getenv("ENVIRONMENT") == "production" else r"http://.*:3000",
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Security middleware: Path traversal protection
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Security middleware to prevent path traversal attacks."""
    path = str(request.url.path)
    
        # Check for path traversal patterns in diagrams endpoint
        if '/api/diagrams/' in path or path.startswith('/api/diagrams/'):
            # Check for path traversal patterns (including URL-encoded)
            import urllib.parse
            decoded_path = urllib.parse.unquote(path)
            
            # Check for .. patterns (including URL-encoded %2E%2E)
            if '..' in path or '..' in decoded_path or '%2E%2E' in path.upper() or '%2e%2e' in path.lower():
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid file path: path traversal detected"}
                )
            
            # Check for null bytes
            if '\x00' in decoded_path:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid file path: null byte detected"}
                )
            
            # Check for excessive path depth (more than /api/diagrams/{filename})
            # Split path and count non-empty segments
            path_segments = [seg for seg in path.split('/') if seg]
            # Expected: ['api', 'diagrams', '{filename}'] = 3 segments
            if len(path_segments) != 3 or path_segments[0] != 'api' or path_segments[1] != 'diagrams':
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid file path: path traversal detected"}
                )
    
    return await call_next(request)

# Request ID tracking middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests for tracking."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Add request_id to logging context
    old_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.request_id = request_id
        return record
    logging.setLogRecordFactory(record_factory)
    
    # Add request ID to response headers
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        # Log request with ID
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Time: {process_time:.4f}s"
        )
        
        return response
    finally:
        # Restore original factory
        logging.setLogRecordFactory(old_factory)

# Include API routes
app.include_router(router, prefix="/api", tags=["diagrams"])

@app.get("/", tags=["info"])
async def root():
    """
    Root endpoint - API information.
    
    Returns basic API information and version.
    """
    return {
        "message": "Architecture Diagram Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["info"])
async def health():
    """
    Health check endpoint.
    
    Returns API health status. Use this for monitoring and load balancer health checks.
    """
    return {"status": "healthy", "service": "diagram-generator-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

