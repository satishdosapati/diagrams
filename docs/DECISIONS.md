# Architectural Decisions

This document records key architectural decisions, their rationale, and alternatives considered.

## Decision Log Format

Each decision follows this structure:
- **Date**: When the decision was made
- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: What problem we're solving
- **Decision**: What we decided
- **Consequences**: Impact and trade-offs
- **Alternatives**: What we considered but didn't choose

---

## ADR-001: Use Strands Agents for Natural Language Processing

**Date**: 2024-12-XX  
**Status**: Accepted  
**Context**: Need to convert natural language descriptions into structured architecture specifications.

**Decision**: Use Strands Agents with Amazon Bedrock (Claude Sonnet 4) for natural language understanding and structured output generation.

**Consequences**:
- ✅ High-quality structured output via Pydantic models
- ✅ Easy to extend with new agents (modification, classification)
- ✅ Built-in error handling and retries
- ⚠️ Dependency on AWS Bedrock (cost, availability)
- ⚠️ Requires AWS credentials configuration

**Alternatives Considered**:
- Direct LLM API calls (OpenAI, Anthropic) - Less structured output, more manual parsing
- Rule-based parsing - Too rigid, doesn't scale
- Hybrid approach - More complex, Strands provides better abstraction

---

## ADR-002: Python Diagrams Library for Diagram Generation

**Date**: 2024-12-XX  
**Status**: Accepted  
**Context**: Need to generate visual architecture diagrams from structured specifications.

**Decision**: Use the `diagrams` Python library with Graphviz as the rendering engine.

**Consequences**:
- ✅ Clean, Pythonic API for diagram generation
- ✅ Multi-provider support (AWS, Azure, GCP, Kubernetes, etc.)
- ✅ Graphviz provides powerful layout algorithms
- ✅ Supports clusters, custom styling, multiple formats
- ⚠️ Requires Graphviz system dependency
- ⚠️ Code generation approach (execute Python code dynamically)

**Alternatives Considered**:
- Direct Graphviz DOT file generation - More verbose, less maintainable
- PlantUML - Less flexible, different syntax
- Mermaid.js - JavaScript-based, would require Node.js backend
- Custom rendering - Too much work, reinventing the wheel

---

## ADR-003: FastAPI for Backend Framework

**Date**: 2024-12-XX  
**Status**: Accepted  
**Context**: Need a modern Python web framework for REST API.

**Decision**: Use FastAPI for the backend API server.

**Consequences**:
- ✅ Automatic OpenAPI/Swagger documentation
- ✅ Type validation via Pydantic (consistent with Strands)
- ✅ Async support for better performance
- ✅ Modern Python features (type hints, dataclasses)
- ✅ Easy to test and maintain

**Alternatives Considered**:
- Flask - Less modern, manual documentation
- Django - Overkill for API-only service
- Tornado - Less popular, fewer resources

---

## ADR-004: React + TypeScript for Frontend

**Date**: 2024-12-XX  
**Status**: Accepted  
**Context**: Need a modern, type-safe frontend framework.

**Decision**: Use React 19+ with TypeScript and Vite for the frontend.

**Consequences**:
- ✅ Type safety catches errors at compile time
- ✅ Modern React features (hooks, concurrent rendering)
- ✅ Fast development with Vite HMR
- ✅ Large ecosystem and community
- ⚠️ Learning curve for TypeScript

**Alternatives Considered**:
- Vue.js - Less popular in enterprise
- Svelte - Smaller ecosystem
- Plain JavaScript - No type safety

---

## ADR-005: Session-Based State Management

**Date**: 2024-12-XX  
**Status**: Accepted  
**Context**: Need to track diagram state for chat-based modifications.

**Decision**: Use in-memory session storage with automatic expiration (1 hour TTL).

**Consequences**:
- ✅ Simple implementation, no database required
- ✅ Fast access (in-memory)
- ✅ Automatic cleanup prevents memory leaks
- ⚠️ Lost on server restart
- ⚠️ Not scalable across multiple instances

**Alternatives Considered**:
- Redis - More complex, requires infrastructure
- Database (PostgreSQL) - Overkill for MVP, adds latency
- Stateless (regenerate each time) - Poor UX for modifications

**Future Consideration**: Move to Redis for production multi-instance deployments.

---

## ADR-006: Code Generation Approach

**Date**: 2024-12-XX  
**Status**: Accepted  
**Context**: Need to generate Python code for diagrams library execution.

**Decision**: Generate Python code as strings and execute dynamically using `exec()`.

**Consequences**:
- ✅ Full flexibility with diagrams library API
- ✅ Easy to debug (can see generated code)
- ✅ Supports all diagrams library features
- ⚠️ Security risk (code execution)
- ⚠️ Requires sandboxing/validation

**Security Measures**:
- Input validation before code generation
- Restricted imports (only diagrams library)
- No file system access
- Timeout on execution

**Alternatives Considered**:
- Direct API calls to diagrams library - Less flexible, harder to customize
- AST manipulation - More complex, harder to debug
- Template-based generation - Less flexible

---

## ADR-007: Multi-Provider Support Architecture

**Date**: 2024-12-XX  
**Status**: Accepted  
**Context**: Support multiple cloud providers (AWS, Azure, GCP) with consistent API.

**Decision**: Use provider-specific resolvers with a unified ArchitectureSpec model.

**Consequences**:
- ✅ Consistent API across providers
- ✅ Easy to add new providers
- ✅ Provider-specific optimizations possible
- ✅ Type safety with provider validation
- ⚠️ More code to maintain

**Architecture**:
- `ComponentResolver` interface
- Provider-specific resolvers (AWSResolver, AzureResolver, GCPResolver)
- Provider validation in API layer
- Provider-aware code generation

**Alternatives Considered**:
- Single universal resolver - Too complex, hard to maintain
- Separate APIs per provider - Inconsistent, more endpoints

---

## ADR-008: Clusters and Grouping Support

**Date**: 2024-12-XX  
**Status**: Accepted  
**Context**: Need to represent hierarchical architectures (VPCs, subnets, services).

**Decision**: Add `Cluster` model to ArchitectureSpec with support for nested clusters via `parent_id`.

**Consequences**:
- ✅ Realistic architecture representation
- ✅ Better visual organization
- ✅ Supports complex nested structures
- ⚠️ More complex code generation
- ⚠️ Requires careful validation (circular references)

**Implementation**:
- Flat cluster list with `parent_id` references (avoids recursion issues)
- Auto-clustering for 3+ related components
- Cluster-level Graphviz attributes

**Alternatives Considered**:
- Recursive cluster model - Causes issues with Strands structured output
- No clustering - Less realistic diagrams
- Manual grouping only - Poor UX

---

## ADR-009: Graphviz Attributes Support

**Date**: 2024-12-XX  
**Status**: Accepted  
**Context**: Users need control over diagram styling and appearance.

**Decision**: Support Graphviz attributes at graph, node, and edge levels, plus per-component and per-connection overrides.

**Consequences**:
- ✅ Full control over diagram appearance
- ✅ Professional, presentation-ready diagrams
- ✅ Brand consistency possible
- ⚠️ Complex API (many options)
- ⚠️ Requires Graphviz knowledge for advanced use

**Implementation**:
- `GraphvizAttributes` model with graph_attr, node_attr, edge_attr
- Preset themes for quick styling
- Per-component and per-connection overrides

**Alternatives Considered**:
- Fixed styling only - Too limiting
- CSS-like styling - Doesn't map to Graphviz
- Template-based themes only - Less flexible

---

## ADR-010: Feedback System for Continuous Improvement

**Date**: 2024-12-XX  
**Status**: Accepted (Phase 1 Complete)  
**Context**: Want to learn from user feedback to improve diagram generation.

**Decision**: Implement thumbs up/down feedback system with pattern extraction from successful generations.

**Consequences**:
- ✅ Self-improving system over time
- ✅ User-driven quality improvements
- ✅ Pattern learning for better code generation
- ⚠️ Requires sufficient feedback volume
- ⚠️ Pattern application not yet implemented (Phase 2)

**Current State (Phase 1)**:
- Feedback collection
- Pattern extraction (imports, structure)
- Pattern storage with success rates

**Future (Phase 2)**:
- Automatic pattern application
- Anti-pattern detection
- Context-aware pattern selection

**Alternatives Considered**:
- No feedback - No improvement over time
- Manual pattern updates - Slow, doesn't scale
- A/B testing - More complex infrastructure

---

## ADR-011: Always Use Left-to-Right Layout Direction

**Date**: 2024-12-XX  
**Status**: Accepted  
**Context**: Need consistent diagram layout for better readability.

**Decision**: Always enforce left-to-right (LR) direction for all architecture diagrams, regardless of user input.

**Consequences**:
- ✅ Consistent, predictable layouts
- ✅ Better readability (natural left-to-right flow)
- ✅ Matches common architecture diagram conventions
- ⚠️ Less flexibility for users who want other directions

**Rationale**:
- Architecture diagrams typically flow left-to-right (source → processing → storage)
- Consistent direction improves user experience
- Can be overridden in Advanced Code Mode if needed

**Alternatives Considered**:
- User-selectable direction - Inconsistent results
- Auto-detect based on diagram type - Too complex, unreliable
- Default to LR but allow override - Confusing API

---

## ADR-012: File Cleanup Strategy

**Date**: 2024-12-XX  
**Status**: Accepted  
**Context**: Generated diagram files accumulate and consume disk space.

**Decision**: Automatic cleanup of files older than 24 hours, with background cleanup task running every 5 minutes.

**Consequences**:
- ✅ Prevents disk space issues
- ✅ Automatic, no manual intervention
- ✅ Reasonable retention (24 hours)
- ⚠️ Files deleted after 24 hours (no long-term storage)

**Implementation**:
- Background task in FastAPI startup
- Scans output directory for old files
- Deletes files older than 24 hours
- Runs every 5 minutes

**Alternatives Considered**:
- No cleanup - Disk space issues
- Manual cleanup - Poor UX
- Longer retention (7 days) - More disk usage
- Cloud storage (S3) - More complex, additional cost

---

## ADR-013: Security - Path Traversal Protection

**Date**: 2024-12-XX  
**Status**: Accepted  
**Context**: File serving endpoint could be vulnerable to path traversal attacks.

**Decision**: Validate and sanitize all file paths, reject any paths containing `..` or absolute paths.

**Consequences**:
- ✅ Prevents directory traversal attacks
- ✅ Simple, effective protection
- ✅ Clear error messages for invalid requests
- ⚠️ Requires careful validation logic

**Implementation**:
- Path normalization
- Reject paths with `..`
- Reject absolute paths
- Whitelist approach (only allow specific patterns)

**Alternatives Considered**:
- No validation - Security vulnerability
- Complex path resolution - More error-prone
- Database-backed file tracking - Overkill

---

## Summary

These decisions reflect the project's focus on:
1. **Simplicity**: Choose proven, well-documented solutions
2. **Type Safety**: Use TypeScript and Pydantic throughout
3. **Flexibility**: Support multiple providers and customization options
4. **Security**: Input validation, path protection, code execution safety
5. **User Experience**: Consistent layouts, easy-to-use API, helpful features
6. **Maintainability**: Clear architecture, good documentation, testable code

For questions or updates to these decisions, please document the rationale and update this file.