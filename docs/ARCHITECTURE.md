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

## Phase 1 (MVP) Architecture

- Single provider: AWS only
- Simple ArchitectureSpec model
- Basic DiagramsEngine
- Single API endpoint
- Simple React UI

