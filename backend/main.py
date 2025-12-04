"""
FastAPI application entry point for MVP.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
import logging
import time

from src.api.routes import router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Architecture Diagram Generator API",
    description="""
    Generate cloud architecture diagrams from natural language descriptions.
    
    ## Features
    
    * **Natural Language Processing**: Convert text descriptions into architecture diagrams
    * **Multi-Cloud Support**: AWS, Azure, and GCP
    * **Multiple Output Formats**: PNG, SVG, PDF, DOT, JPG
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

# Request ID tracking middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests for tracking."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Add request ID to response headers
    start_time = time.time()
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

