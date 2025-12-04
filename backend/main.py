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

# Use allow_origin_regex to allow any IP address on port 3000
# This allows the frontend to work regardless of EC2 IP without hardcoding
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"http://.*:3000",  # Allow any IP/hostname on port 3000
    allow_credentials=True,
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

