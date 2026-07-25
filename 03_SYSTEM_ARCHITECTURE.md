# Global Network Anomaly Tracker (GNAT)

# System Architecture Document

Version: 1.0

Status: Approved

Architecture Style:
Clean Architecture + Layered Architecture + Modular Monolith

Framework:
Django 5

AI Framework:
PyTorch Geometric

Database:
PostgreSQL

Visualization:
Plotly

Deployment:
Docker

---

# 1. Purpose

This document defines the overall software architecture of the Global Network Anomaly Tracker.

It serves as the single architectural reference for every module generated during development.

All generated code MUST follow this document.

---

# 2. Architecture Principles

The system follows:

• Clean Architecture

• SOLID Principles

• Separation of Concerns

• Single Responsibility Principle

• Dependency Inversion

• Layered Architecture

• Modular Design

• Domain Driven Design (Lightweight)

---

# 3. High Level Architecture

                    +----------------------+
                    |      Web Browser     |
                    +----------+-----------+
                               |
                               |
                    Django Templates / HTMX
                               |
                               |
                    +----------v-----------+
                    |     Django Views     |
                    +----------+-----------+
                               |
                      Service Layer
                               |
        +----------+-----------+-----------+
        |          |                       |
        |          |                       |
 Data Engine   AI Engine           Visualization
        |          |                       |
        +----------+-----------+-----------+
                               |
                         PostgreSQL
                               |
                         File Storage
                               |
                    Trained AI Models

---

# 4. Layer Architecture

Presentation Layer

Responsibilities

• HTML

• Bootstrap

• Plotly

• HTMX

• JavaScript

Contains

Templates

Static Files

Forms

---

Application Layer

Responsibilities

Business Logic

Authentication

Validation

Workflow

Contains

Views

Services

Serializers

Permissions

---

Domain Layer

Responsibilities

Graph Processing

Graph Analytics

Feature Engineering

Risk Calculation

AI Model Management

Contains

Pure Python Logic

No Django Dependencies

---

Infrastructure Layer

Responsibilities

Database

Filesystem

Logging

Docker

Redis

Celery

External Services

---

# 5. Django Project Structure

gnat/

    config/

        settings/

            base.py

            development.py

            production.py

        urls.py

        asgi.py

        wsgi.py

    apps/

        accounts/

        dashboard/

        graph_engine/

        ai_engine/

        visualization/

        analytics/

        api/

        core/

    media/

    static/

    templates/

    logs/

    tests/

---

# 6. Application Responsibilities

accounts

Authentication

Authorization

Roles

Permissions

Profiles

--------------------------------

dashboard

Homepage

Statistics

Charts

History

--------------------------------

graph_engine

Load Data

Generate Graph

Graph Metrics

Feature Engineering

--------------------------------

ai_engine

Dataset

Training

Inference

Model Loading

Risk Prediction

--------------------------------

visualization

Plotly

World Map

Heatmaps

Graph Rendering

--------------------------------

analytics

Reports

Export

History

KPIs

--------------------------------

api

REST Endpoints

Serializers

Authentication

Swagger

--------------------------------

core

Utilities

Logging

Configuration

Constants

Exceptions

Validators

---

# 7. Request Flow

User

↓

Browser

↓

Django URL

↓

View

↓

Service Layer

↓

Business Logic

↓

Database

↓

AI Model

↓

Visualization

↓

HTML Response

---

# 8. AI Pipeline

Cities Dataset

↓

Synthetic Generator

↓

NetworkX Graph

↓

Feature Engineering

↓

PyTorch Geometric

↓

Graph Convolution Network

↓

Risk Score

↓

Database

↓

Dashboard

---

# 9. Data Flow

CSV

↓

Pandas

↓

Cleaning

↓

Graph Builder

↓

Metrics

↓

Node Features

↓

GCN

↓

Inference

↓

Risk Score

↓

Plotly Map

---

# 10. Component Diagram

+----------------------+
| Authentication |
+----------+-----------+

|

+----------v-----------+
| Dataset Generator |
+----------+-----------+

|

+----------v-----------+
| Graph Engine |
+----------+-----------+

|

+----------v-----------+
| AI Engine |
+----------+-----------+

|

+----------v-----------+
| Prediction Service |
+----------+-----------+

|

+----------v-----------+
| Plotly Visualization |
+----------+-----------+

|

+----------v-----------+
| Dashboard |
+----------------------+

---

# 11. Database Interaction

Views never access models directly.

Views

↓

Services

↓

Repositories

↓

Models

↓

PostgreSQL

Advantages

• Easy Testing

• Clean Code

• Better Maintenance

---

# 12. Design Patterns

Repository Pattern

Service Layer Pattern

Factory Pattern

Singleton (Configuration)

Strategy Pattern

Dependency Injection

Builder Pattern

DTO Pattern

Adapter Pattern

Facade Pattern

Observer Pattern (Future)

---

# 13. Error Handling Strategy

Global Exception Middleware

↓

Logging

↓

Custom Exceptions

↓

JSON Error Response

↓

User Friendly Message

Every exception must be logged.

---

# 14. Logging Architecture

Application Logs

↓

File Logs

↓

Console Logs

↓

Future

ELK Stack

Logging Levels

DEBUG

INFO

WARNING

ERROR

CRITICAL

---

# 15. Security Architecture

User Authentication

↓

Permission Check

↓

Input Validation

↓

Business Logic

↓

Database

Security Measures

CSRF

CORS

HTTPS

Environment Variables

Password Hashing

Secure Cookies

Session Expiry

Rate Limiting

---

# 16. AI Architecture

Data Loader

↓

Graph Builder

↓

Feature Generator

↓

Dataset

↓

GCN

↓

Trainer

↓

Checkpoint

↓

Inference

↓

Prediction Service

---

# 17. Deployment Architecture

Browser

↓

Nginx

↓

Gunicorn

↓

Django

↓

PostgreSQL

↓

Redis

↓

Celery

↓

AI Models

↓

Storage

Docker Compose manages all services.

---

# 18. Scalability

Future Ready

Horizontal Scaling

Separate AI Service

Microservices

Kafka

Neo4j

Graph Database

GPU Cluster

Cloud Storage

Kubernetes

---

# 19. Directory Ownership

accounts

Authentication

dashboard

User Interface

graph_engine

Graph Analytics

ai_engine

Machine Learning

visualization

Maps

analytics

Reports

api

REST

core

Utilities

config

Configuration

---

# 20. Architecture Rules

Views must never contain AI code.

Models must never contain business logic.

Business logic belongs inside Services.

AI code belongs only inside ai_engine.

Visualization belongs only inside visualization.

Database access must go through repositories.

Every module must be independently testable.

No circular imports.

No duplicated logic.

---

# 21. Future Architecture

Current

Modular Monolith

↓

Future

Microservices

↓

Containerized AI

↓

Kubernetes

↓

Cloud Native

↓

Distributed Training

---

# Final Architecture Goals

The completed application should resemble a professional cybersecurity analytics platform capable of:

✔ Secure Authentication

✔ AI-based Anomaly Detection

✔ Interactive Global Visualization

✔ Enterprise Dashboard

✔ REST APIs

✔ Production Deployment

✔ Clean Architecture

✔ High Maintainability

✔ Resume-Level Engineering Quality

End of Architecture Document