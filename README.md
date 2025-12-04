# Architecture Diagram Generator

AI-powered architecture diagram generator that converts natural language descriptions into visual architecture diagrams.

## Features

- ✅ Natural language to diagram conversion using Strands Agents
- ✅ Support for AWS, Azure, GCP providers
- ✅ Chat-based iterative diagram modification
- ✅ Universal generator supporting multiple diagram types
- ✅ Provider consistency enforcement

## Project Structure

```
diagram-generator/
├── backend/          # Python FastAPI backend
├── frontend/         # React frontend
├── deployment/       # EC2 deployment scripts
├── docs/            # Documentation
└── config/          # Configuration files
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
- ⏳ **Phase 5**: Polish & production

## Documentation

See `docs/` directory for detailed documentation:
- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Phase Documentation](docs/phases/)

## Testing

```bash
cd backend
pytest tests/
```

## Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for EC2 deployment instructions.
