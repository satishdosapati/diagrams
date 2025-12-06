# Architecture Documentation

## System Overview

The Architecture Diagram Generator converts natural language descriptions into visual architecture diagrams using AI.

## Components

### Backend

- **FastAPI**: REST API server
- **Strands Agents**: Natural language processing
- **Diagrams Library**: Diagram generation
- **Graphviz**: Rendering engine

### Frontend

- **React**: UI framework
- **Vite**: Build tool and dev server
- **TypeScript**: Type safety

### Infrastructure

- **AWS EC2**: Deployment platform
- **Amazon Bedrock**: LLM provider
- **systemd**: Service management

## Data Flow

```
User Input (Natural Language)
    ↓
Frontend (React)
    ↓
Backend API (FastAPI)
    ↓
Strands Agent (Bedrock)
    ↓
ArchitectureSpec (Pydantic)
    ↓
DiagramsEngine
    ↓
Diagrams Library + Graphviz
    ↓
Generated Diagram (PNG)
    ↓
Returned to Frontend
```

## Architecture Components

### Backend
- **FastAPI**: REST API with request tracking
- **Strands Agents**: Natural language processing (DiagramAgent, ModificationAgent, ClassifierAgent)
- **Generators**: UniversalGenerator routes to DiagramsEngine for code generation
- **Resolvers**: Component mapping with intelligent fuzzy matching
- **Advisors**: Provider-specific architectural best practices

### Frontend
- **React + TypeScript**: UI framework with type safety
- **Components**: DiagramGenerator, AdvancedCodeMode, ExamplesPanel, ProviderSelector

### Security & Performance
- Path traversal protection, input validation, session expiration (1 hour)
- Instance caching, automatic file cleanup (24-hour retention), session cleanup

