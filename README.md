# Architecture Diagram Generator

AI-powered architecture diagram generator that converts natural language descriptions into visual architecture diagrams.

## Features

- ✅ **Natural Language Processing**: Convert text descriptions to diagrams using Strands Agents
- ✅ **Multi-Cloud Support**: AWS, Azure, and GCP with provider consistency enforcement
- ✅ **Multiple Output Formats**: PNG, SVG, PDF, DOT, JPG
- ✅ **Chat-Based Modifications**: Iterative refinement through conversation
- ✅ **Advanced Code Mode**: Direct Python code editing with autocomplete
- ✅ **Examples Panel**: Pre-built architecture examples for each provider
- ✅ **Session Management**: Automatic expiration and cleanup
- ✅ **Request Tracking**: Request ID tracking for debugging
- ✅ **Production Ready**: Security hardening, API documentation, deployment scripts

## Project Structure

```
diagrams/
├── backend/              # Python FastAPI backend
│   ├── src/
│   │   ├── api/         # API routes with request tracking
│   │   ├── agents/      # Strands agents (diagram, modification, classifier)
│   │   ├── generators/  # Diagram generators (universal, diagrams engine)
│   │   ├── models/      # Pydantic models (ArchitectureSpec, etc.)
│   │   ├── resolvers/   # Component resolvers (intelligent, library discovery)
│   │   ├── advisors/    # Architectural advisors (AWS advisor)
│   │   └── validators/  # Input validation
│   ├── config/          # Node registry YAML files
│   ├── tests/           # Test suite
│   └── main.py          # FastAPI application entry point
├── frontend/            # React TypeScript frontend
│   └── src/
│       ├── components/  # React components (DiagramGenerator, AdvancedCodeMode, etc.)
│       ├── services/    # API client services
│       ├── data/        # Example prompts data
│       └── pages/       # Page components (HelpPage)
├── deployment/          # EC2 deployment scripts and systemd services
├── docs/               # Comprehensive documentation
│   ├── phases/         # Phase-by-phase implementation docs
│   ├── API.md          # API endpoint documentation
│   ├── ARCHITECTURE.md # System architecture
│   └── DEPLOYMENT.md   # Deployment guide
└── config/             # Feature flags and environment config
```

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Development Phases

- ✅ **Phase 1**: MVP - Basic AWS diagram generation
- ✅ **Phase 2**: Provider selection (AWS/Azure/GCP)
- ✅ **Phase 3**: Chat-based modifications
- ✅ **Phase 4**: Universal generator
- ✅ **Phase 5**: Polish & production - Security, optimization, documentation

## Documentation

See `docs/` directory for detailed documentation:
- [Architecture](docs/ARCHITECTURE.md) - System architecture and data flow
- [API Documentation](docs/API.md) - Complete API endpoint reference
- [Deployment Guide](docs/DEPLOYMENT.md) - EC2 deployment instructions
- [Phase Documentation](docs/phases/) - Implementation phases

**API Documentation (Interactive):**
- Swagger UI: `http://localhost:8000/docs` (when backend is running)
- ReDoc: `http://localhost:8000/redoc`

## Testing

```bash
cd backend
pytest tests/
```

## Deployment

See [DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md) or [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for EC2 deployment instructions.

## Security Features

- ✅ Path traversal protection for file serving
- ✅ Input validation and sanitization
- ✅ Session expiration (1 hour TTL)
- ✅ CORS configuration for production
- ✅ Request ID tracking for debugging
- ✅ Automatic file cleanup (24-hour retention)

## Recent Improvements

- ✅ Output format selection (PNG, SVG, PDF, DOT, JPG)
- ✅ Download format dropdown with regeneration
- ✅ Instance caching for performance optimization
- ✅ Comprehensive API documentation with Swagger UI
- ✅ Request ID tracking middleware
- ✅ Session management with automatic cleanup
- ✅ File cleanup for old diagrams
- ✅ TypeScript type safety improvements
