# Architecture Documentation

## System Overview

The Architecture Diagram Generator converts natural language descriptions into visual architecture diagrams using AI. Supports AWS, Azure, and GCP with multiple output formats and interactive modifications.

## Components

### Backend

- **FastAPI**: REST API server with request tracking middleware
- **Strands Agents**: Natural language processing (Bedrock Claude Sonnet 4)
- **Diagrams Library**: Diagram generation via Python code execution
- **Graphviz**: Rendering engine for multiple formats (PNG, SVG, PDF, DOT)

### Frontend

- **React 19+**: UI framework
- **Vite**: Build tool and dev server
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling

### Infrastructure

- **AWS EC2**: Deployment platform
- **Amazon Bedrock**: LLM provider
- **systemd**: Service management

## Data Flow

```text
User Input (Natural Language)
    ↓
Frontend (React)
    ↓
Backend API (FastAPI) [Request ID tracking]
    ↓
Strands Agent (Bedrock) → ArchitectureSpec (Pydantic)
    ↓
UniversalGenerator → DiagramsEngine
    ↓
Diagrams Library + Graphviz
    ↓
Generated Diagram (PNG/SVG/PDF/DOT)
    ↓
Returned to Frontend
```

## Architecture Components

### Backend

#### API Layer (`src/api/`)
- **FastAPI Router**: REST endpoints with request tracking
- **Endpoints**:
  - `POST /api/generate-diagram`: Generate diagram from natural language
  - `POST /api/modify-diagram`: Modify existing diagram via chat
  - `POST /api/execute-code`: Execute Python code directly (Advanced Code Mode)
  - `GET /api/diagrams/{filename}`: Retrieve generated diagram file
  - `POST /api/regenerate-format`: Regenerate diagram in different format
  - `GET /api/completions/{provider}`: Get code completions for provider
  - `POST /api/validate-code`: Validate Python code syntax
  - `POST /api/feedback`: Submit thumbs up/down feedback
  - `GET /api/error-logs/{request_id}`: Get logs for request ID
  - `GET /api/feedback/stats`: Get feedback statistics

#### Agents (`src/agents/`)
- **DiagramAgent**: Converts natural language to ArchitectureSpec
- **ModificationAgent**: Iterative diagram refinement with state management
- **ClassifierAgent**: Classifies diagram complexity and type
- **MCP Tools**: Optional integration with AWS Diagram MCP Server

#### Generators (`src/generators/`)
- **UniversalGenerator**: Routes to provider-specific engines
- **DiagramsEngine**: Generates Python code from ArchitectureSpec
- **GraphvizPresets**: Styling presets for diagrams

#### Resolvers (`src/resolvers/`)
- **ComponentResolver**: Provider-specific component mapping
- **IntelligentResolver**: Fuzzy matching for component names
- **LibraryDiscovery**: Discovers available diagram components

#### Advisors (`src/advisors/`)
- **AWSArchitecturalAdvisor**: AWS best practices and patterns
- **AzureArchitecturalAdvisor**: Azure best practices and patterns
- **GCPArchitecturalAdvisor**: GCP best practices and patterns

#### Models (`src/models/`)
- **ArchitectureSpec**: Pydantic model for architecture structure
- **NodeRegistry**: Component registry loaded from YAML configs

#### Storage (`src/storage/`)
- **FeedbackStorage**: File-based feedback persistence (JSON)
- **Session Storage**: In-memory session management with expiration

#### Services (`src/services/`)
- **LogCapture**: In-memory log buffer for error reporting per request ID

#### Integrations (`src/integrations/`)
- **MCPDiagramClient**: Optional MCP server integration (feature-flagged)

#### Validators (`src/validators/`)
- **InputValidator**: Validates user input and prevents non-cloud requests

### Frontend

#### Components (`src/components/`)
- **DiagramGenerator**: Main diagram generation interface
- **AdvancedCodeMode**: Direct Python code editing with Monaco Editor
- **ExamplesPanel**: Pre-built architecture examples
- **ProviderSelector**: Cloud provider selection (AWS/Azure/GCP)
- **FeedbackWidget**: Thumbs up/down feedback collection
- **ErrorDisplay**: Error message display with log retrieval
- **ProgressBar**: Loading state indicators

#### Pages (`src/pages/`)
- **HelpPage**: User documentation and help

#### Services (`src/services/`)
- **API Client**: TypeScript API client for backend communication

### Security & Performance

#### Security
- **Path Traversal Protection**: Validates filenames, prevents directory traversal
- **Input Validation**: Pydantic models validate all API inputs
- **Code Execution Sandbox**: Validates Python code before execution, blocks dangerous patterns
- **Session Expiration**: 1-hour TTL with automatic cleanup

#### Performance
- **Instance Caching**: Caches DiagramsEngine and ComponentResolver per provider
- **Automatic File Cleanup**: 24-hour retention for generated diagrams
- **Session Cleanup**: Background task removes expired sessions (every 5 minutes)
- **Request Tracking**: Request ID middleware for debugging and observability

