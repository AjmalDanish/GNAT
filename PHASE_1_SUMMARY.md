# Global Network Anomaly Tracker (GNAT)

## Phase 1: Django Project Setup - Summary

This document summarizes all files and architectural decisions made during Phase 1.

---

## Files Generated

### Configuration Files

| File | Purpose | Key Features |
|------|---------|--------------|
| `.gitignore` | Git ignore patterns | Excludes env files, cache, logs, media, models |
| `.env.example` | Environment variables template | All required configuration with defaults |
| `pyproject.toml` | Project configuration | Black, isort, mypy, pytest settings, metadata |
| `manage.py` | Django management script | Entry point for Django commands |

### Requirements Files

| File | Purpose | Dependencies |
|------|---------|--------------|
| `requirements/base.txt` | Core dependencies | Django, DRF, PostgreSQL, Celery, PyTorch, Plotly |
| `requirements/development.txt` | Dev dependencies | Debug toolbar, testing tools, formatters, linters |
| `requirements/production.txt` | Prod dependencies | Gunicorn, Whitenoise, Sentry |
| `requirements/testing.txt` | Test dependencies | Pytest, coverage, factory-boy, faker |

### Django Settings

| File | Purpose | Key Settings |
|------|---------|--------------|
| `config/settings/base.py` | Common configuration | Database, logging, DRF, Celery, security defaults |
| `config/settings/development.py` | Development overrides | Debug mode, debug toolbar, console logging |
| `config/settings/production.py` | Production overrides | Security hardening, file serving, Sentry |
| `config/settings/testing.py` | Testing overrides | In-memory DB, fast password hashing, dummy cache |

### Django Core Files

| File | Purpose |
|------|---------|
| `config/urls.py` | Root URL routing, API docs, error handlers |
| `config/wsgi.py` | WSGI entry point for Gunicorn |
| `config/asgi.py` | ASGI entry point for async/WebSocket support |
| `config/celery.py` | Celery configuration for background tasks |

### Django Applications (10 apps created)

| App | Purpose | Status |
|-----|---------|--------|
| `accounts` | Authentication & authorization | Structure created, Phase 11 implementation |
| `dashboard` | Main dashboard interface | Structure created, Phase 17 implementation |
| `graph_engine` | Graph generation & metrics | Structure created, Phase 3 & 8 implementation |
| `ai_engine` | AI/ML models & inference | Structure created, Phase 5, 6, 7, 11 implementation |
| `visualization` | Interactive visualizations | Structure created, Phase 16 implementation |
| `analytics` | Reports & analytics | Structure created, Phase 17 implementation |
| `reports` | Report generation | Structure created, Phase 17 implementation |
| `notifications` | Notification system | Structure created, Phase 19 implementation |
| `api` | REST API endpoints | Structure created, Phase 13 implementation |
| `common` | Shared utilities | Exception handler, context processors created |

### Docker Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Multi-service Docker setup (web, postgres, redis, celery workers, flower) |
| `deployment/docker/Dockerfile` | Multi-stage Docker build for production |

### CI/CD Files

| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | Lint, test, security scan, build pipeline |
| `.github/workflows/test.yml` | Matrix testing across OS/Python versions |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Project overview, installation, usage |

---

## Architectural Decisions

### 1. Clean Architecture Implementation

**Decision**: Follow layered architecture with separation of concerns.

**Rationale**:
- Makes the codebase maintainable and testable
- Enables future migration to microservices
- Clear boundaries between layers (Presentation → Application → Domain → Infrastructure)

**Implementation**:
- Views never access models directly
- Business logic in services layer
- Data access through repositories
- AI code isolated in ai_engine app

### 2. Environment-Specific Settings

**Decision**: Split settings into base, development, production, testing modules.

**Rationale**:
- Prevents accidental production settings in development
- Allows easy environment switching via `DJANGO_SETTINGS_MODULE`
- Follows Django best practices
- Enables environment-specific optimizations

**Implementation**:
```python
# base.py: Common configuration
# development.py: Debug mode, console logging, relaxed security
# production.py: Security hardening, file serving, monitoring
# testing.py: In-memory DB, fast execution
```

### 3. Django REST Framework Configuration

**Decision**: Comprehensive DRF setup with best practices.

**Rationale**:
- Consistent API responses
- Built-in authentication and permissions
- Pagination for large datasets
- Throttling to prevent abuse
- Exception handling for user-friendly errors

**Implementation**:
- Session authentication (JWT future)
- IsAuthenticated by default
- PageNumberPagination
- DjangoFilterBackend for filtering
- Custom exception handler in common app

### 4. Celery for Background Tasks

**Decision**: Use Celery with Redis broker for async task processing.

**Rationale**:
- Long-running AI training shouldn't block web requests
- Scheduled tasks for cleanup and reports
- Distributed task processing
- Task monitoring with Flower

**Implementation**:
- Dedicated queues for different task types (ai_tasks, graph_tasks, etc.)
- Task routing based on priority
- Celery beat for scheduled tasks
- Signal handlers for task lifecycle events

### 5. Logging Strategy

**Decision**: Structured logging with rotating file handlers.

**Rationale**:
- Debugging production issues
- Audit trail for security
- Performance monitoring
- Separation of logs by component (app, training, prediction, errors)

**Implementation**:
- RotatingFileHandler with size limits
- Separate log files per component
- JSON formatter for production (structured logging)
- Console logging in development

### 6. PostgreSQL Configuration

**Decision**: Use PostgreSQL with connection pooling.

**Rationale**:
- ACID compliance for data integrity
- JSON support for flexible schemas
- Full-text search capabilities
- Better performance than MySQL for complex queries

**Implementation**:
- Connection pooling with `CONN_MAX_AGE`
- Query timeout to prevent long-running queries
- Persistent connections for performance

### 7. Security Configuration

**Decision**: Security-first approach with production hardening.

**Rationale**:
- Protect user data and credentials
- Prevent common web vulnerabilities
- Meet enterprise security standards

**Implementation**:
- Environment variables for secrets
- HSTS in production
- Secure cookies
- CORS restrictions
- CSRF protection
- X-Frame-Options: DENY
- Content-Type nosniff

### 8. Docker Multi-Stage Build

**Decision**: Multi-stage Docker build for optimized production images.

**Rationale**:
- Smaller final image size
- Security (build tools not in runtime)
- Faster deployment
- Consistent build environment

**Implementation**:
```dockerfile
# base stage: System dependencies
# builder stage: Build Python dependencies
# runtime stage: Minimal runtime environment
```

### 9. Celery Task Routing

**Decision**: Route tasks to dedicated queues based on type and priority.

**Rationale**:
- Prevent long-running AI tasks from blocking quick tasks
- Dedicated workers for each queue type
- Priority-based execution
- Better resource allocation

**Implementation**:
```python
task_routes = {
    "apps.ai_engine.tasks.*": {"queue": "ai_tasks", "priority": 9},
    "apps.graph_engine.tasks.*": {"queue": "graph_tasks", "priority": 8},
    # ... more routes
}
```

### 10. Type Hints and Docstrings

**Decision**: Enforce type hints and comprehensive docstrings.

**Rationale**:
- Better IDE support (autocompletion, type checking)
- Self-documenting code
- Easier maintenance
- mypy static type checking

**Implementation**:
- All functions use type hints
- Docstrings for modules, classes, functions
- pyproject.toml config for mypy

### 11. Testing Strategy

**Decision**: Comprehensive testing with pytest and coverage.

**Rationale**:
- Catch bugs early
- Ensure code quality
- Documentation via tests
- Confidence in refactoring

**Implementation**:
- pytest for test framework
- pytest-django for Django integration
- pytest-cov for coverage reporting
- In-memory SQLite for tests
- Factory-Boy for test data

### 12. Git Workflow

**Decision**: Git flow with CI/CD.

**Rationale**:
- Controlled deployments
- Code quality checks before merge
- Automated testing
- Version history

**Implementation**:
- Main branch (production)
- Develop branch (staging)
- Feature branches
- Pull request requirements (CI passing)

---

## Directory Structure

```
Global-Network-Anomaly-Tracker-Blueprint/
├── config/                    # Django project configuration
│   ├── settings/              # Environment-specific settings
│   ├── urls.py                # Root URL configuration
│   ├── wsgi.py                # WSGI entry point
│   ├── asgi.py                # ASGI entry point
│   └── celery.py              # Celery configuration
├── apps/                      # Django applications
│   ├── accounts/              # Authentication & authorization
│   ├── dashboard/             # Main dashboard
│   ├── graph_engine/          # Graph processing
│   ├── ai_engine/             # AI/ML models
│   ├── visualization/         # Visualizations
│   ├── analytics/             # Analytics
│   ├── reports/               # Reports
│   ├── notifications/         # Notifications
│   ├── api/                   # REST API
│   └── common/                # Shared utilities
├── data/                      # Data storage
├── models/                    # AI model storage
├── templates/                 # Django templates
├── static/                    # Static files
├── media/                     # User media
├── logs/                      # Application logs
├── tests/                     # Test suite
├── docs/                      # Documentation
├── deployment/                # Deployment configs
├── requirements/              # Python dependencies
├── .github/                   # GitHub workflows
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore patterns
├── docker-compose.yml         # Docker services
├── pyproject.toml             # Project configuration
├── manage.py                  # Django management script
└── README.md                  # Project documentation
```

---

## Next Steps (Phase 2)

Phase 1 is complete. The next phase is:

**Phase 2: Synthetic Data Generator**

Will implement:
- City and country data models
- Synthetic network traffic generation
- Dataset management system
- Validation and quality checks

---

## How to Run

### Local Development

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements/development.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Set up database
createdb gnat_db

# 5. Run migrations (after implementing models in Phase 8)
python manage.py migrate

# 6. Start development server
python manage.py runserver

# 7. Start Celery (in separate terminal)
celery -A config.celery worker --loglevel=info
```

### Docker Development

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start all services
docker-compose up -d

# 3. Run migrations
docker-compose exec web python manage.py migrate

# 4. Access the application
# Web: http://localhost:8000
# Admin: http://localhost:8000/admin/
# API Docs: http://localhost:8000/swagger/
# Flower: http://localhost:5555
```

---

## Phase 1 Deliverables Checklist

- [x] Complete folder structure
- [x] requirements.txt (base, development, production, testing)
- [x] pyproject.toml with project configuration
- [x] .env.example with all environment variables
- [x] Django settings (base.py, development.py, production.py, testing.py)
- [x] urls.py with routing
- [x] wsgi.py for production deployment
- [x] asgi.py for async support
- [x] manage.py entry point
- [x] Logging configuration
- [x] PostgreSQL configuration
- [x] Static/media configuration
- [x] Environment variable loader (django-environ)
- [x] Celery configuration
- [x] Initial README.md
- [x] .gitignore
- [x] Docker-ready structure (docker-compose.yml, Dockerfile)
- [x] All Django apps created (10 apps)
- [x] Business logic NOT implemented (as specified)

---

## End of Phase 1

Phase 1: Django Project Setup is complete and ready for review.

The project structure follows Clean Architecture principles with:
- Environment-based configuration
- Security-first defaults
- Production-ready settings
- Comprehensive logging
- Background task support (Celery)
- Docker containerization
- CI/CD pipeline setup