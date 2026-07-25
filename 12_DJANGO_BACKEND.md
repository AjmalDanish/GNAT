# Global Network Anomaly Tracker (GNAT)

# Django Backend Design

Version: 1.0

Status:
Approved

Module:
Backend Application

Framework:
Django 5

Architecture:
Clean Architecture

Dependencies

Django

Django REST Framework

PostgreSQL

Celery

Redis

PyTorch Geometric

Plotly

---

# 1. Purpose

The Django Backend serves as the central application layer of GNAT.

It manages user requests, authentication, business logic, database operations, AI integration, and dashboard services.

---

# 2. Objectives

The backend shall

✔ Manage users

✔ Manage datasets

✔ Trigger graph generation

✔ Trigger AI inference

✔ Store prediction history

✔ Provide dashboard statistics

✔ Expose REST APIs

✔ Support background jobs

---

# 3. Application Structure

Project

config/

Apps

accounts/

dashboard/

graph_engine/

ai_engine/

datasets/

analytics/

reports/

notifications/

api/

core/

---

# 4. Application Responsibilities

accounts

Authentication

Authorization

User Profiles

Roles

dashboard

Dashboard Statistics

Charts

Widgets

Recent Activity

graph_engine

Graph Creation

Graph Validation

Feature Engineering

Exports

ai_engine

Training

Inference

Prediction

Risk Scores

datasets

Upload

Import

Export

Versioning

analytics

Metrics

Reports

Trend Analysis

reports

Generate Reports

Export Reports

History

notifications

System Notifications

Alerts

Messages

api

REST API Endpoints

Serializers

Permissions

core

Utilities

Constants

Exceptions

Validators

Logging

---

# 5. Request Flow

Browser

↓

URL

↓

View

↓

Service

↓

Repository

↓

Database

↓

Response

Business logic must only exist inside Services.

---

# 6. Service Layer

Responsibilities

Business Logic

Validation

Transactions

Workflow

AI Calls

Services

UserService

DatasetService

GraphService

TrainingService

InferenceService

DashboardService

ReportService

NotificationService

---

# 7. Repository Layer

Responsibilities

Database Access

Queries

Filtering

Bulk Operations

Repositories

UserRepository

DatasetRepository

PredictionRepository

GraphRepository

ModelRepository

ReportRepository

---

# 8. Database Models

Core Models

User

Profile

Dataset

Transaction

Graph

Node

Edge

Prediction

TrainingRun

Report

Notification

AuditLog

---

# 9. Authentication

Use Django Authentication

Support

Login

Logout

Password Change

Password Reset

Session Authentication

Token Authentication (Future)

---

# 10. User Roles

Administrator

Can manage everything

Analyst

Can upload datasets

Run predictions

View reports

Viewer

Read-only access

---

# 11. Dashboard Integration

Dashboard displays

Total Datasets

Total Nodes

Total Edges

Prediction Count

Average Risk

Recent Predictions

Training History

Graph Statistics

---

# 12. AI Integration

Backend communicates with

Graph Engine

Training Pipeline

Inference Engine

Communication through Service Layer only.

Views must never directly invoke AI models.

---

# 13. File Upload

Supported Formats

CSV

JSON

GraphML

Maximum Size

Configurable

Validation Required

Before Processing

---

# 14. Background Jobs

Use Celery

Tasks

Dataset Processing

Graph Generation

Model Training

Prediction

Report Generation

Notification Delivery

---

# 15. Configuration

Store configuration in

Environment Variables

settings.py

.env

No secrets should be hardcoded.

---

# 16. Security

CSRF Protection

SQL Injection Protection

XSS Protection

Password Hashing

Input Validation

Permission Checks

Secure File Uploads

---

# 17. Logging

Log

Authentication

Dataset Upload

Training

Inference

Errors

Warnings

Audit Events

---

# 18. Exception Handling

Create Custom Exceptions

ValidationError

DatasetError

GraphError

TrainingError

InferenceError

PermissionError

Log every exception.

Return user-friendly messages.

---

# 19. Testing

Unit Tests

Models

Views

Services

Repositories

Integration Tests

Authentication

Dataset Processing

AI Integration

Dashboard

API Tests

Performance Tests

---

# 20. Performance

Database Indexing

Query Optimization

Pagination

Bulk Inserts

Caching

Lazy Loading

Background Processing

---

# 21. API Readiness

Backend must expose

Authentication APIs

Dataset APIs

Graph APIs

Training APIs

Inference APIs

Dashboard APIs

Report APIs

Notification APIs

---

# 22. Expected Outputs

User Accounts

Stored Datasets

Generated Graphs

Trained Models

Predictions

Dashboard Data

Reports

Audit Logs

---

# 23. Success Criteria

The backend is complete when

✔ Authentication works

✔ Dataset upload works

✔ Graph generation works

✔ AI inference works

✔ Dashboard loads

✔ Reports generate

✔ APIs function correctly

✔ Tests pass

✔ Documentation complete

---

# Future Improvements

OAuth2

JWT Authentication

Multi-Tenant Support

API Versioning

Microservices

WebSockets

GraphQL

Real-Time Notifications

---

# GLM-4.7 Instructions

Generate implementation in the following order

1.

Create Django Apps

2.

Define Models

3.

Implement Repositories

4.

Implement Services

5.

Create Views

6.

Configure URL Routing

7.

Integrate AI Engine

8.

Implement Celery Tasks

9.

Write Tests

10.

Generate Documentation

Generate production-ready code.

Use SOLID principles.

Keep business logic inside services.

Use repositories for database access.

Include logging, validation, type hints, and docstrings.

Wait for approval after each component.

End of Django Backend Design