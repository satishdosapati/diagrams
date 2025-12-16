# Architecture Diagram Generator

AI-powered architecture diagram generator that converts natural language descriptions into visual architecture diagrams.

## Features

- ✅ **Natural Language Processing**: Convert text descriptions to diagrams using Strands Agents
- ✅ **Multi-Cloud Support**: AWS, Azure, and GCP with provider consistency enforcement
- ✅ **Multiple Output Formats**: PNG, SVG, PDF, DOT
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
│   ├── API.md          # API endpoint documentation
│   ├── ARCHITECTURE.md # System architecture
│   ├── DECISIONS.md    # Architectural decisions (ADR format)
│   ├── EC2_DEPLOYMENT_GUIDE.md # EC2 deployment guide
│   └── EC2_QUICK_REFERENCE.md   # EC2 quick reference
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
- ⏳ **Phase 3**: Chat-based modifications (not yet implemented)
- ✅ **Phase 4**: Universal generator
- ✅ **Phase 5**: Polish & production - Security, optimization, documentation

## Documentation

Essential documentation:
- [Architecture](docs/ARCHITECTURE.md) - System architecture overview
- [API Documentation](docs/API.md) - API endpoints and quick reference
- [Architectural Decisions](docs/DECISIONS.md) - Key design decisions

**Interactive API Docs:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Quick test run:
```bash
cd backend
pytest tests/ -v
```

For comprehensive test reports and detailed instructions, see [Test Instructions](backend/tests/TEST_INSTRUCTIONS.md).

Quick reference:
```bash
# Full test suite with reports
python tests/run_tests.py --all-reports --verbose

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
python tests/run_tests.py --coverage
```

## Deployment

### Prerequisites
- AWS EC2 instance (Amazon Linux 2023)
- Security group: ports 22, 3000, 8000
- IAM role attached to EC2 instance with Bedrock access permissions

### Quick Deploy
```bash
# SSH into EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Pull and deploy
cd /opt/diagram-generator
git pull origin main
bash deployment/deploy-git.sh
```

### Initial Setup
1. Install dependencies: `sudo yum install -y python3 python3-pip nodejs graphviz git`
2. Clone repository to `/opt/diagram-generator`
3. Setup backend: `cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
4. Setup frontend: `cd frontend && npm install && npm run build`
5. Configure `.env` in `backend/` with AWS region and Bedrock model ID (IAM role provides credentials)
6. Create systemd services (see `deployment/systemd/` directory)
7. Start services: `sudo systemctl start diagram-api diagram-frontend`

### Updating
```bash
cd /opt/diagram-generator
git pull origin main
bash deployment/deploy-git.sh
# Or manually:
# cd backend && source venv/bin/activate && pip install -r requirements.txt && sudo systemctl restart diagram-api
# cd ../frontend && npm install && npm run build && sudo systemctl restart diagram-frontend
```

### Troubleshooting

**Service Issues:**
- Check logs: `sudo journalctl -u diagram-api.service -f`
- Verify services: `sudo systemctl status diagram-api diagram-frontend`
- Restart services: `sudo systemctl restart diagram-api diagram-frontend`

**Backend Errors:**
- **ModuleNotFoundError: No module named 'strands'**
  ```bash
  cd backend
  source venv/bin/activate
  pip install git+https://github.com/strands-agents/sdk-python.git
  deactivate
  ```
- **Dependency conflicts**: Upgrade packages:
  ```bash
  pip install --upgrade uvicorn[standard] pydantic python-multipart anyio
  pip install -r requirements.txt --upgrade
  ```
- **Python version**: Ensure Python 3.10+ is installed
  ```bash
  python3 --version  # Should be 3.10+
  # If not available: sudo yum install -y python3.11 python3.11-pip python3.11-devel
  ```

## Security Features

- ✅ Path traversal protection for file serving
- ✅ Input validation and sanitization
- ✅ Session expiration (1 hour TTL)
- ✅ CORS configuration for production
- ✅ Request ID tracking for debugging
- ✅ Automatic file cleanup (24-hour retention)

## Recent Improvements

- ✅ Output format selection (PNG, SVG, PDF, DOT)
- ✅ Download format dropdown with regeneration
- ✅ Instance caching for performance optimization
- ✅ Comprehensive API documentation with Swagger UI
- ✅ Request ID tracking middleware
- ✅ Session management with automatic cleanup
- ✅ File cleanup for old diagrams
- ✅ TypeScript type safety improvements
