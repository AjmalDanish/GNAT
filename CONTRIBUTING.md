# Contributing to GNAT

Thank you for your interest in contributing to the Global Network Anomaly Tracker (GNAT)!

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)

---

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment:

- Be respectful and considerate
- Use inclusive language
- Focus on constructive feedback
- Assume good intentions

---

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (optional)
- Git

### Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/GNAT.git
   cd GNAT
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/GNAT.git
   ```

4. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements/development.txt
   ```

6. Copy environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

7. Set up database:
   ```bash
   createdb gnat_db
   python manage.py migrate
   ```

8. Run tests:
   ```bash
   pytest
   ```

---

## Development Workflow

### 1. Create an Issue

Always start by creating an issue for your work:

1. Go to the [Issues](https://github.com/YOUR_USERNAME/GNAT/issues) page
2. Click "New Issue"
3. Choose the appropriate template (Bug Report or Feature Request)
4. Fill in all required fields
5. Add appropriate labels
5. Submit the issue

### 2. Create a Feature Branch

For every feature or bug fix, create a new branch from `develop`:

```bash
# Update develop branch
git checkout develop
git pull upstream develop

# Create feature branch
git checkout -b feature/<module-name>
# or
git checkout -b bugfix/<issue-name>
# or
git checkout -b hotfix/<issue-name>
# or
git checkout -b release/vX.Y.Z
```

**Branch Naming Convention:**

- `feature/<module-name>` - New features
- `bugfix/<issue-name>` - Bug fixes
- `hotfix/<issue-name>` - Urgent production fixes
- `release/vX.Y.Z` - Release preparation

### 3. Implement Your Changes

- Write clean, well-documented code
- Follow the coding standards below
- Add tests for your changes
- Update documentation

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest tests/unit/test_graph_engine.py

# Run integration tests only
pytest -m integration
```

### 5. Run Code Quality Checks

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

### 6. Commit Your Changes

Follow the Conventional Commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**

```bash
git commit -m "feat(ai): implement GCN model architecture"
git commit -m "fix(api): resolve serializer validation bug"
git commit -m "docs(readme): update installation guide"
git commit -m "perf(graph): optimize graph construction"
```

### 7. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/<module-name>

# Create Pull Request on GitHub
```

---

## Coding Standards

### Python Code Style

Follow PEP 8 with these project-specific rules:

- Maximum line length: 100 characters
- Use type hints for all functions
- Docstrings for all modules, classes, and public functions
- No magic numbers or hardcoded values
- Use `dataclass` for simple data structures
- Use `Enum` for fixed sets of values

### Type Hints

```python
from typing import Any, Dict, List, Optional

def process_graph(graph_id: int, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process a graph with given options."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_metrics(graph: Graph) -> Dict[str, float]:
    """
    Calculate graph metrics.

    Args:
        graph: The graph to analyze.

    Returns:
        Dictionary of metric names and values.

    Raises:
        ValueError: If graph is empty.
    """
    ...
```

### Import Order

```python
# Standard library imports
import os
from typing import Any

# Third-party imports
from django.db import models
from rest_framework import serializers

# Django imports
from apps.accounts.models import User

# Local imports
from .utils import helper_function
```

### Error Handling

```python
try:
    result = some_function()
except SpecificException as e:
    logger.error(f"Error processing: {e}")
    raise CustomException("Detailed error message") from e
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests for individual functions/classes
├── integration/    # Integration tests for multiple components
├── performance/    # Performance and load tests
└── security/       # Security tests
```

### Writing Tests

```python
import pytest
from apps.graph_engine.services import GraphService

class TestGraphService:
    """Test cases for GraphService."""

    @pytest.fixture
    def sample_graph_data(self):
        """Fixture providing sample graph data."""
        return {...}

    def test_graph_creation(self, sample_graph_data):
        """Test that graph is created correctly."""
        service = GraphService()
        graph = service.create_graph(sample_graph_data)
        
        assert graph is not None
        assert graph.node_count > 0
        assert graph.edge_count > 0

    @pytest.mark.integration
    def test_graph_persistence(self, sample_graph_data):
        """Test graph persistence to database."""
        ...
```

### Test Coverage

- Aim for >80% code coverage
- Test edge cases and error conditions
- Mock external dependencies
- Use fixtures for test data

---

## Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Examples

```
feat(ai): implement GCN model architecture

- Add GCN layer configuration
- Implement forward pass
- Add model serialization
- Update documentation

Closes #123
```

```
fix(api): resolve serializer validation bug

The serializer was not properly validating email format,
causing invalid emails to be accepted. This commit fixes
the validation logic.

Fixes #456
```

---

## Pull Request Process

### Before Opening a PR

- [ ] All tests pass
- [ ] Code is properly formatted (black, isort)
- [ ] Code passes linting (flake8)
- [ ] Type checking passes (mypy)
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Commits follow the conventional format

### PR Description

Use the provided template:

1. **Type**: Select the type of change
2. **Related Issue**: Link to the issue being addressed
3. **Description**: Explain what the PR does
4. **Changes Made**: List key changes
5. **Files Changed**: List modified files
6. **Testing**: Describe testing performed
7. **Documentation**: Confirm documentation updates
8. **Checklist**: Complete all items

### Code Review

- Respond to review comments promptly
- Make requested changes in new commits
- Keep PRs focused and reasonably sized
- Squash commits if needed before merging

### Merging

- PRs are merged into `develop` by maintainers
- Maintainers will squash commits
- PRs must have at least one approval
- All CI checks must pass

---

## Project Structure

```
Global-Network-Anomaly-Tracker/
├── config/                 # Django project configuration
│   ├── settings/          # Environment-specific settings
│   ├── urls.py            # Root URL routing
│   ├── wsgi.py            # WSGI entry point
│   ├── asgi.py            # ASGI entry point
│   └── celery.py          # Celery configuration
├── apps/                   # Django applications
│   ├── accounts/          # Authentication
│   ├── dashboard/         # Dashboard
│   ├── graph_engine/      # Graph processing
│   ├── ai_engine/         # AI/ML models
│   ├── visualization/     # Visualizations
│   ├── analytics/         # Analytics
│   ├── reports/           # Reports
│   ├── notifications/     # Notifications
│   ├── api/               # REST API
│   └── common/            # Shared utilities
├── data/                   # Data storage
├── models/                 # AI models
├── templates/              # Django templates
├── static/                 # Static assets
├── media/                  # User media
├── logs/                   # Application logs
├── tests/                  # Test suite
├── docs/                   # Documentation
├── deployment/             # Deployment configs
├── requirements/           # Python dependencies
├── .github/                # GitHub workflows and templates
├── .env.example            # Environment variables
├── .gitignore              # Git ignore rules
├── CHANGELOG.md            # Changelog
├── CONTRIBUTING.md         # This file
├── LICENSE                 # MIT License
├── README.md               # Project readme
├── docker-compose.yml      # Docker services
├── pyproject.toml          # Project config
└── manage.py               # Django management
```

---

## Asking for Help

- GitHub Issues: Use issues for bugs and feature requests
- GitHub Discussions: Use discussions for questions and ideas
- Contact: dev@gnat.example.com

---

## License

By contributing to GNAT, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to GNAT! 🚀