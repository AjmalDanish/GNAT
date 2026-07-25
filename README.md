# Global Network Anomaly Tracker (GNAT)

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://docs.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-orange.svg)]()

**AI-Powered Network Traffic Anomaly Detection Using Graph Neural Networks**

[![GitHub](https://img.shields.io/badge/GitHub-AjmalDanish%2FGNAT-blue.svg)](https://github.com/AjmalDanish/GNAT)
[![Issues](https://img.shields.io/badge/Issues-11-orange.svg)](https://github.com/AjmalDanish/GNAT/issues)
[![Pull Requests](https://img.shields.io/badge/PRs-Open-green.svg)](https://github.com/AjmalDanish/GNAT/pulls)

[Documentation](docs/) | [API Docs](/swagger/) | [Dashboard](/) | [Contributing](CONTRIBUTING.md)

</div>

---

## Overview

The Global Network Anomaly Tracker (GNAT) is an enterprise-grade web platform that simulates worldwide network traffic, detects anomalies using Graph Neural Networks (GNNs), and provides interactive visualizations on a world map.

### Key Features

- **Synthetic Data Generation**: Simulate realistic network traffic between cities worldwide
- **Graph Construction**: Transform network data into graph representations using NetworkX
- **AI-Powered Detection**: Use PyTorch Geometric for GNN-based anomaly detection
- **Interactive Visualization**: Real-time world map with anomaly heatmaps using Plotly
- **Enterprise Dashboard**: Comprehensive analytics and reporting interface
- **REST API**: Full-featured API for integration with external systems
- **Background Processing**: Celery for asynchronous task execution

## Tech Stack

| Category | Technology |
|----------|------------|
| **Backend** | Django 5, Django REST Framework |
| **Database** | PostgreSQL 16 |
| **AI/ML** | PyTorch, PyTorch Geometric, Scikit-learn |
| **Graph Processing** | NetworkX |
| **Visualization** | Plotly, Bootstrap 5 |
| **Task Queue** | Celery + Redis |
| **Deployment** | Docker, Docker Compose |
| **Testing** | Pytest, Coverage |

## Project Architecture

The project follows **Clean Architecture** principles with a layered approach:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│              (Templates, Static Files, HTMX)                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Application Layer                        │
│          (Views, Services, Serializers, Permissions)        │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      Domain Layer                           │
│    (Graph Processing, Analytics, AI Models, Business Logic) │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Infrastructure Layer                      │
│      (Database, Filesystem, Redis, Celery, Docker)         │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
Global-Network-Anomaly-Tracker/
├── config/                 # Django project configuration
│   ├── settings/          # Environment-specific settings
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py            # WSGI entry point
│   ├── asgi.py            # ASGI entry point
│   └── celery.py          # Celery configuration
├── apps/                   # Django applications
│   ├── accounts/          # Authentication & authorization
│   ├── dashboard/         # Main dashboard interface
│   ├── graph_engine/      # Graph generation & metrics
│   ├── ai_engine/         # AI/ML model training & inference
│   ├── visualization/     # Interactive visualizations
│   ├── analytics/         # Reports & analytics
│   ├── reports/           # Report generation
│   ├── notifications/     # Notification system
│   ├── api/               # REST API endpoints
│   └── common/            # Shared utilities
├── data/                   # Data directory
│   ├── raw/               # Raw datasets
│   ├── processed/         # Processed data
│   ├── synthetic/         # Generated traffic
│   └── exports/           # Export files
├── models/                 # AI model storage
│   ├── trained/           # Trained models
│   ├── checkpoints/       # Training checkpoints
│   └── exported/          # Exported models
├── templates/              # Django templates
├── static/                 # Static assets
├── media/                  # User-uploaded media
├── logs/                   # Application logs
├── tests/                  # Test suite
├── docs/                   # Documentation
├── deployment/             # Deployment configurations
├── requirements/           # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── docker-compose.yml      # Docker services definition
├── manage.py               # Django management script
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Installation

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (optional, for containerized deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/AjmalDanish/GNAT.git
   cd Global-Network-Anomaly-Tracker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements/development.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb gnat_db
   
   # Or use Docker for PostgreSQL
   docker-compose up -d postgres redis
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start the development server**
   ```bash
   python manage.py runserver
   ```

9. **Start Celery workers** (in a separate terminal)
   ```bash
   celery -A config.celery worker --loglevel=info
   ```

10. **Start Celery beat** (in a separate terminal, for scheduled tasks)
    ```bash
    celery -A config.celery beat --loglevel=info
    ```

### Docker Setup

Using Docker Compose is the simplest way to run the entire stack:

1. **Copy environment file**
   ```bash
   cp .env.example .env
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Create a superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the application**
   - Web: http://localhost:8000
   - API Docs (Swagger): http://localhost:8000/swagger/
   - Flower (Celery Monitor): http://localhost:5555

## Usage

### Running Management Commands

```bash
# Development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
pytest

# Start shell with Django environment
python manage.py shell_plus
```

### Accessing Different Interfaces

- **Dashboard**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation (Swagger)**: http://localhost:8000/swagger/
- **API Documentation (ReDoc)**: http://localhost:8000/redoc/
- **Celery Monitoring (Flower)**: http://localhost:5555/

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `SECRET_KEY` | Django secret key | (generated) |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/0` |
| `EMAIL_HOST` | SMTP server host | - |
| `TIME_ZONE` | Application timezone | `UTC` |

### Settings Modules

The application uses environment-specific settings:

- `config.settings.development` - Development environment
- `config.settings.production` - Production environment
- `config.settings.testing` - Testing environment

Set the `DJANGO_SETTINGS_MODULE` environment variable to select.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest tests/unit/test_graph_engine.py

# Run with verbose output
pytest -v

# Run integration tests only
pytest -m integration
```

## Development Workflow

### Code Style

The project enforces code quality standards:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type check with mypy
mypy .
```

### Pre-commit Hooks

Set up pre-commit hooks for automatic code quality checks:

```bash
pip install pre-commit
pre-commit install
```

## Project Phases

This project is developed in phases:

1. ✅ **Phase 1**: Django Project Setup (Current)
2. ⏳ **Phase 2**: Synthetic Data Generator
3. ⏳ **Phase 3**: Graph Construction
4. ⏳ **Phase 4**: Graph Analytics
5. ⏳ **Phase 5**: Graph Neural Network
6. ⏳ **Phase 6**: Training Pipeline
7. ⏳ **Phase 7**: Inference Pipeline
8. ⏳ **Phase 8**: Database Integration
9. ⏳ **Phase 9**: Django Backend
10. ⏳ **Phase 10**: REST APIs
11. ⏳ **Phase 11**: Authentication
12. ⏳ **Phase 12**: Dashboard
13. ⏳ **Phase 13**: Interactive World Map
14. ⏳ **Phase 14**: Background Tasks
15. ⏳ **Phase 15**: Admin Panel
16. ⏳ **Phase 16**: Testing
17. ⏳ **Phase 17**: Docker
18. ⏳ **Phase 18**: Deployment
19. ⏳ **Phase 19**: Documentation

See [PROJECT_ROADMAP.md](01_PROJECT_ROADMAP.md) for details.

## API Documentation

The project provides comprehensive API documentation via Swagger UI:

- **Interactive API Docs**: `/swagger/`
- **ReDoc Documentation**: `/redoc/`
- **OpenAPI Schema**: `/swagger.json`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](.github/CONTRIBUTING.md) before submitting a pull request.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/AjmalDanish/GNAT/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AjmalDanish/GNAT/discussions)

## Acknowledgments

- Built with [Django](https://www.djangoproject.com/)
- AI powered by [PyTorch Geometric](https://pytorch-geometric.readthedocs.io/)
- Visualization by [Plotly](https://plotly.com/)

---

<div align="center">

**Built with ❤️ for network security professionals**

[⬆ Back to Top](#global-network-anomaly-tracker-gnat)

</div>