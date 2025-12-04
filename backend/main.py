"""
FastAPI application entry point for MVP.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

from src.api.routes import router

app = FastAPI(
    title="Architecture Diagram Generator API",
    description="Generate architecture diagrams from natural language",
    version="1.0.0"
)

# CORS middleware - Allow access from public IP and localhost
# Get allowed origins from environment or allow all for development
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
if cors_origins_env == "*":
    # Allow all origins (useful for development and public APIs)
    allowed_origins = ["*"]
else:
    # Use specific origins from environment variable (comma-separated)
    allowed_origins = [origin.strip() for origin in cors_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Allow public IP, localhost, or all origins
    allow_credentials=True if "*" not in allowed_origins else False,  # Credentials not allowed with "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["diagrams"])

@app.get("/")
async def root():
    return {"message": "Architecture Diagram Generator API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

