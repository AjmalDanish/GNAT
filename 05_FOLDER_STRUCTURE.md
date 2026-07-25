# Global Network Anomaly Tracker (GNAT)

# Project Folder Structure

Version: 1.0

Status:
Approved

Architecture:
Clean Architecture + Modular Monolith

Framework:
Django 5

---

# Purpose

This document defines the complete directory structure of the project.

Every generated file MUST follow this structure.

No file should be placed outside its designated module.

---

# Root Directory

Global-Network-Anomaly-Tracker/

```
Global-Network-Anomaly-Tracker/

├── config/
├── apps/
├── data/
├── models/
├── notebooks/
├── scripts/
├── docs/
├── tests/
├── templates/
├── static/
├── media/
├── logs/
├── requirements/
├── deployment/
├── .github/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── README.md
└── pyproject.toml
```

---

# Config

Responsible for project configuration.

```
config/

    settings/

        base.py

        development.py

        production.py

        testing.py

    urls.py

    asgi.py

    wsgi.py

    celery.py

```

Never place business logic here.

---

# Apps Directory

Contains all Django applications.

```
apps/

    accounts/

    dashboard/

    graph_engine/

    ai_engine/

    visualization/

    analytics/

    api/

    reports/

    notifications/

    common/

```

Each application must remain independent.

---

# Standard Django App Layout

Every application follows exactly this structure.

```
app_name/

    migrations/

    admin.py

    apps.py

    models.py

    urls.py

    views.py

    serializers.py

    permissions.py

    forms.py

    signals.py

    filters.py

    tasks.py

    services/

    repositories/

    validators/

    constants/

    exceptions/

    utils/

    tests/

```

---

# accounts

Responsibilities

Authentication

Authorization

Permissions

Profiles

JWT (future)

Password Reset

---

# dashboard

Responsibilities

Dashboard

Statistics

KPIs

Recent Analysis

Charts

---

# graph_engine

Responsibilities

Dataset Loading

Graph Creation

Feature Engineering

Graph Metrics

Graph Validation

Graph Utilities

---

Folder Layout

```
graph_engine/

    services/

    repositories/

    algorithms/

    metrics/

    builders/

    validators/

    tests/

```

---

# ai_engine

Responsibilities

Dataset Preparation

Model Training

Inference

Evaluation

Model Registry

Explainability

---

Folder Layout

```
ai_engine/

    datasets/

    models/

    trainers/

    inference/

    checkpoints/

    evaluation/

    explainability/

    feature_engineering/

    services/

    repositories/

    tests/

```

---

# visualization

Responsibilities

World Map

Network Layer

Risk Layer

Charts

Animations

Exports

---

Folder Layout

```
visualization/

    plotly/

    maps/

    charts/

    exports/

    themes/

    assets/

    tests/

```

---

# analytics

Responsibilities

Reports

Historical Analysis

Statistics

Trend Analysis

KPIs

---

# reports

Responsibilities

Generate

PDF

CSV

JSON

Excel

---

# api

Responsibilities

REST APIs

Authentication

Swagger

OpenAPI

Pagination

Filtering

---

Folder Layout

```
api/

    v1/

    serializers/

    permissions/

    pagination/

    filters/

    routers/

    schemas/

    tests/

```

---

# notifications

Responsibilities

Email

Alerts

System Notifications

Future SMS

---

# common

Shared utilities.

Contains

Logging

Configuration

Exceptions

Validators

Constants

Mixins

Decorators

Helpers

---

# Data Directory

```
data/

    raw/

    processed/

    synthetic/

    exports/

    cache/

```

raw

Downloaded datasets.

processed

Clean datasets.

synthetic

Generated traffic.

exports

CSV exports.

cache

Temporary files.

---

# Models Directory

```
models/

    trained/

    checkpoints/

    exported/

    metadata/

```

trained

Final AI models.

checkpoints

Intermediate checkpoints.

exported

ONNX/TorchScript.

metadata

Training metadata.

---

# Notebooks

```
notebooks/

    experiments/

    prototypes/

```

Used only for research.

Never import notebook code into production.

---

# Scripts

```
scripts/

    setup/

    maintenance/

    migration/

    utilities/

```

Contains automation scripts.

---

# Documentation

```
docs/

    architecture/

    api/

    deployment/

    diagrams/

    tutorials/

```

Every architectural document belongs here.

---

# Tests

```
tests/

    unit/

    integration/

    performance/

    security/

```

Every feature must include tests.

---

# Templates

```
templates/

    base/

    dashboard/

    accounts/

    visualization/

    reports/

```

Contains Django templates only.

---

# Static

```
static/

    css/

    js/

    images/

    icons/

    fonts/

```

---

# Media

```
media/

    reports/

    uploads/

    avatars/

    exports/

```

---

# Logs

```
logs/

    application/

    training/

    prediction/

    errors/

```

Never commit log files.

---

# Requirements

```
requirements/

    base.txt

    development.txt

    production.txt

    testing.txt

```

Avoid a single requirements.txt for maintainability.

---

# Deployment

```
deployment/

    docker/

    nginx/

    gunicorn/

    scripts/

```

---

# GitHub

```
.github/

    workflows/

        ci.yml

        lint.yml

        tests.yml

```

---

# Import Rules

Allowed

Views

↓

Services

↓

Repositories

↓

Models

Forbidden

Views → Models directly

Views → AI Model directly

Templates → Database

AI → Templates

---

# Naming Conventions

Directories

snake_case

Python Files

snake_case.py

Classes

PascalCase

Functions

snake_case

Variables

snake_case

Constants

UPPER_CASE

---

# File Size Limits

Python File

Maximum 300 lines

Function

Maximum 40 lines

Class

Maximum 300 lines

Split files if larger.

---

# Dependency Rules

Presentation

↓

Application

↓

Domain

↓

Infrastructure

Dependencies never flow upward.

---

# Logging

Every module must use

Python logging

Never print() in production.

---

# Configuration

Configuration belongs only inside

config/

Environment variables

.env

Never hardcode

Passwords

Secrets

API Keys

Database URLs

---

# Final Directory Principles

✔ Single Responsibility

✔ Modular

✔ Testable

✔ Scalable

✔ Enterprise Ready

✔ Clean Imports

✔ Low Coupling

✔ High Cohesion

✔ Future Microservice Migration Ready

End of Folder Structure Document