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

## Current Architecture (Production Ready)

### Backend Components

- **FastAPI Application**: REST API with request tracking middleware
- **Strands Agents**: 
  - DiagramAgent: Natural language to ArchitectureSpec conversion
  - ModificationAgent: Chat-based diagram modifications
  - ClassifierAgent: Diagram type classification
- **Generators**:
  - UniversalGenerator: Router for different diagram types
  - DiagramsEngine: Python code generation and execution
- **Resolvers**:
  - ComponentResolver: Maps components to Diagrams library classes
  - IntelligentResolver: Fuzzy matching for component names
  - LibraryDiscovery: Discovers available components from Diagrams library
- **Advisors**:
  - AWSArchitecturalAdvisor: Enhances AWS diagrams with best practices
- **Validators**:
  - InputValidator: Validates user input before processing

### Frontend Components

- **DiagramGenerator**: Main component with mode switching
- **AdvancedCodeMode**: Direct Python code editing with Monaco editor
- **DiagramChat**: Chat interface for modifications
- **ExamplesPanel**: Pre-built architecture examples sidebar
- **ProviderSelector**: Cloud provider selection

### Security Features

- Path traversal protection for file serving
- Input validation and sanitization
- Session expiration (1 hour TTL)
- CORS configuration for production
- Request ID tracking for debugging

### Performance Optimizations

- Instance caching for DiagramsEngine and ComponentResolver
- Automatic file cleanup (24-hour retention)
- Session cleanup (every 5 minutes)
- Request processing time tracking

### Session Management

- In-memory session storage with expiration
- Automatic cleanup of expired sessions
- Last accessed timestamp tracking
- Session-based diagram modifications

## Phase 1 (MVP) Architecture (Historical)

- Single provider: AWS only
- Simple ArchitectureSpec model
- Basic DiagramsEngine
- Single API endpoint
- Simple React UI

