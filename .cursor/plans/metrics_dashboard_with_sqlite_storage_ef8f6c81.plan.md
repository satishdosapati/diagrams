---
name: Metrics Dashboard with SQLite Storage
overview: Implement a separate dashboard service with SQLite storage for metrics and architecture specs. Start with SQLite for MVP, with clear migration path to RDS PostgreSQL later.
todos:
  - id: create_storage_module
    content: Create database_storage.py with SQLite implementation, schema initialization, and connection management
    status: pending
  - id: create_dashboard_service
    content: Create dashboard service structure (main.py, routes.py) with FastAPI app on port 8001
    status: pending
  - id: implement_dashboard_endpoints
    content: Implement dashboard API endpoints (metrics, summary, providers, architectures)
    status: pending
    dependencies:
      - create_dashboard_service
      - create_storage_module
  - id: integrate_metrics_recording
    content: Integrate metrics recording into main API generate_diagram endpoint
    status: pending
    dependencies:
      - create_storage_module
  - id: add_architecture_storage
    content: Add architecture storage methods and integrate into main API
    status: pending
    dependencies:
      - create_storage_module
  - id: update_configuration
    content: Update env.yaml and requirements.txt with database configuration
    status: pending
  - id: create_deployment_scripts
    content: Create dashboard startup script and update deployment documentation
    status: pending
    dependencies:
      - create_dashboard_service
  - id: add_tests
    content: Create tests for storage module and dashboard endpoints
    status: pending
    dependencies:
      - create_storage_module
      - implement_dashboard_endpoints
---

# Metrics Dashboard Implementation Plan

## Overview

Build a separate dashboard service (port 8001) with SQLite storage for metrics and architecture specs. The system will track diagram generation events, store architecture specifications, and provide analytics endpoints for dashboarding.

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  Main API       │         │  Dashboard API  │
│  (Port 8000)    │         │  (Port 8001)     │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │ INSERT events              │ SELECT queries
         │                           │
         └───────────┬───────────────┘
                     │
         ┌───────────▼───────────┐
         │   SQLite Database    │
         │   (diagrams.db)      │
         │                      │
         │  - events table      │
         │  - architectures     │
         │  - indexes           │
         └──────────────────────┘
```

## Implementation Steps

### Phase 1: Database Storage Module

**1.1 Create Unified Storage Module**

- **File**: `backend/src/storage/database_storage.py`
- **Purpose**: SQLite-based storage for metrics and architectures
- **Key Features**:
  - Connection management with WAL mode
  - Schema initialization
  - Metrics recording (`record_generation`)
  - Architecture storage (`save_architecture`, `get_architecture`)
  - Query methods for analytics
  - Data retention/cleanup

**1.2 Database Schema**

- **Tables**:
  - `events`: Metrics/events table with indexes on timestamp, provider, date
  - `architectures`: Architecture specs stored as JSONB (SQLite JSON1 extension)
  - `schema_version`: Track migrations
- **Indexes**: Optimize for common queries (date ranges, provider filters)

**1.3 Configuration**

- **File**: `config/env.yaml` - Add database configuration
- **Environment Variables**: `DATABASE_PATH`, `RETENTION_DAYS`

### Phase 2: Dashboard Service

**2.1 Dashboard Service Structure**

- **Directory**: `backend/dashboard/`
- **Files**:
  - `dashboard/main.py`: FastAPI app entry point (port 8001)
  - `dashboard/routes.py`: Dashboard API endpoints
  - `dashboard/__init__.py`: Package init

**2.2 Dashboard Endpoints**

- `GET /api/metrics`: Aggregated metrics by period (daily/weekly/monthly)
- `GET /api/summary`: Overall summary statistics
- `GET /api/providers`: Provider-specific statistics
- `GET /api/architectures`: List architectures with filters
- `GET /api/architectures/{generation_id}`: Get specific architecture
- `GET /api/architectures/search`: Search architectures
- `GET /api/health`: Health check

**2.3 Dashboard Configuration**

- CORS configuration for dashboard frontend
- Port configuration via `DASHBOARD_PORT` env var (default: 8001)

### Phase 3: Main API Integration

**3.1 Update Main API Routes**

- **File**: `backend/src/api/routes.py`
- **Changes**:
  - Import `DatabaseStorage` from storage module
  - Initialize storage instance
  - Add metrics recording to `generate_diagram` endpoint:
    - Generate `generation_id` early
    - Record success/failure metrics in try/except/finally blocks
    - Store architecture spec after successful generation
  - Ensure metrics failures don't break main API (silent failures)

**3.2 Add Architecture Retrieval Endpoints** (Optional)

- `GET /api/architectures/{generation_id}`: Retrieve architecture by ID
- `GET /api/architectures`: List user's architectures

### Phase 4: Dependencies & Configuration

**4.1 Update Requirements**

- **File**: `backend/requirements.txt`
- **Add**: No new dependencies (SQLite is stdlib, but may add `psycopg2` for future RDS migration)

**4.2 Environment Configuration**

- **File**: `config/env.yaml`
- **Add**:
  ```yaml
  database:
    path: "./data/diagrams.db"
    retention_days: 90
  dashboard:
    port: 8001
  ```


**4.3 Update .env.example** (if exists)

- Add database configuration variables

### Phase 5: Deployment & Scripts

**5.1 Dashboard Startup Script**

- **File**: `backend/dashboard/start_dashboard.sh`
- **Purpose**: Script to start dashboard service

**5.2 Update Deployment Scripts**

- Update `deployment/systemd/` scripts if needed
- Add dashboard service systemd file (optional)

**5.3 Update Useful Commands**

- **File**: `useful_commands.txt`
- Add commands for starting dashboard service

### Phase 6: Testing

**6.1 Storage Tests**

- **File**: `backend/tests/test_storage.py`
- Test metrics recording, architecture storage, queries, concurrency

**6.2 Dashboard API Tests**

- **File**: `backend/tests/test_dashboard.py`
- Test dashboard endpoints, aggregations, error handling

**6.3 Integration Tests**

- Update `backend/tests/test_api.py` to verify metrics recording

## Key Implementation Details

### Database Storage Class Structure

```python
class DatabaseStorage:
    def __init__(self, db_path: str)
    def _init_db(self)
    def _get_connection(self) -> sqlite3.Connection
    
    # Metrics methods
    def record_generation(...)
    def get_metrics(period, provider, start_date, end_date)
    
    # Architecture methods
    def save_architecture(...)
    def get_architecture(generation_id)
    def list_architectures(...)
    def search_architectures(...)
    
    # Maintenance
    def cleanup_old_data(retention_days)
```

### Metrics Recording Pattern

```python
# In generate_diagram endpoint
start_time = time.time()
generation_id = str(uuid.uuid4())  # Generate early
success = False

try:
    # ... generation logic ...
    success = True
    return response
except Exception as e:
    # Record failure
    storage.record_generation(..., success=False, error=...)
    raise
finally:
    # Record success (if not already recorded)
    if success:
        storage.record_generation(..., success=True)
```

### Migration Path to RDS

- Design storage interface to be database-agnostic
- Use connection string pattern (SQLite: file path, RDS: connection string)
- Create `RDSStorage` class later that implements same interface
- Migration script to move data from SQLite to RDS

## Files to Create/Modify

### New Files

- `backend/src/storage/database_storage.py`
- `backend/dashboard/__init__.py`
- `backend/dashboard/main.py`
- `backend/dashboard/routes.py`
- `backend/dashboard/start_dashboard.sh`
- `backend/tests/test_storage.py`
- `backend/tests/test_dashboard.py`

### Modified Files

- `backend/src/api/routes.py` - Add metrics recording
- `backend/requirements.txt` - Add any new dependencies
- `config/env.yaml` - Add database config
- `useful_commands.txt` - Add dashboard commands

## Success Criteria

1. Dashboard service runs independently on port 8001
2. Metrics are recorded for every diagram generation
3. Architectures are stored and retrievable
4. Dashboard endpoints return aggregated metrics
5. Data persists across EC2 reboots
6. Silent failure handling (metrics don't break main API)
7. Clear migration path to RDS PostgreSQL

## Future Enhancements (Out of Scope)

- RDS PostgreSQL migration
- Read replicas for scaling
- Materialized views for faster queries
- TimescaleDB extension for time-series optimization
- Dashboard frontend UI
- Real-time metrics via WebSockets