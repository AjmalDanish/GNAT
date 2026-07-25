# Global Network Anomaly Tracker (GNAT)

# Software Requirements Specification (SRS)

Version: 1.0

Document Status: Approved

Development Methodology: Agile Scrum

Architecture: Clean Architecture

Primary Framework: Django 5

Machine Learning Framework: PyTorch Geometric

Visualization: Plotly

Database: PostgreSQL

Deployment: Docker

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0 | Initial | First Release |

---

# Table of Contents

1. Introduction
2. Purpose
3. Scope
4. Objectives
5. Stakeholders
6. Actors
7. Functional Requirements
8. Non-Functional Requirements
9. System Architecture
10. Modules
11. Use Cases
12. User Stories
13. Constraints
14. Assumptions
15. Acceptance Criteria
16. Future Enhancements

---

# 1. Introduction

Global Network Anomaly Tracker (GNAT) is an AI-powered cybersecurity analytics platform designed to simulate worldwide network communication, model it as a graph, detect anomalies using Graph Neural Networks (GCNs), and visualize suspicious behavior on an interactive global map.

The application is intended to demonstrate enterprise software engineering, artificial intelligence, graph analytics, backend development, visualization, and deployment in a single production-grade system.

---

# 2. Purpose

The system will:

- Generate synthetic global network traffic.
- Construct graph structures from traffic.
- Train Graph Neural Networks.
- Detect anomalous nodes and edges.
- Visualize risk on an interactive world map.
- Store historical analyses.
- Provide secure user authentication.
- Expose REST APIs.
- Support deployment using Docker.

---

# 3. Scope

The application includes:

✔ User Authentication

✔ Data Generation

✔ Graph Construction

✔ Feature Engineering

✔ AI Model Training

✔ Model Inference

✔ Interactive Dashboard

✔ PostgreSQL Storage

✔ REST APIs

✔ Deployment

Out of Scope

- Real-time packet capture
- Distributed training
- Multi-GPU clusters
- Kubernetes deployment
- Cloud-native autoscaling

---

# 4. Objectives

Primary Objectives

- Detect graph anomalies using GNNs.
- Build a production-ready Django application.
- Visualize anomalies geographically.
- Demonstrate AI + Full Stack Engineering.

Secondary Objectives

- Resume-quality project.
- GitHub portfolio.
- Extensible architecture.
- Modular codebase.

---

# 5. Stakeholders

Primary User

- Security Analyst

Secondary User

- Administrator

Developer

- AI Engineer

System Administrator

- DevOps Engineer

Recruiters

- Portfolio reviewers

---

# 6. Actors

Actor

Security Analyst

Responsibilities

- Generate datasets
- Run AI analysis
- View predictions
- Filter anomalies
- Export reports

---

Actor

Administrator

Responsibilities

- Manage users
- Monitor logs
- View system status
- Configure application

---

# 7. Functional Requirements

FR-001

The system shall authenticate users.

Priority

High

---

FR-002

The system shall generate synthetic worldwide traffic.

Priority

High

---

FR-003

The system shall create weighted directed graphs.

Priority

High

---

FR-004

The system shall compute graph metrics.

Examples

- Degree
- Betweenness
- Closeness
- Eigenvector
- PageRank

Priority

High

---

FR-005

The system shall train Graph Neural Networks.

Priority

High

---

FR-006

The system shall generate anomaly risk scores.

Priority

High

---

FR-007

The system shall display nodes on a Plotly world map.

Priority

High

---

FR-008

The system shall support filtering by:

- Risk Score
- Country
- Region
- Connection Count

---

FR-009

The system shall expose REST APIs.

---

FR-010

The system shall save prediction history.

---

FR-011

The system shall export results.

Supported Formats

CSV

JSON

---

# 8. Non-Functional Requirements

Performance

- API response < 500 ms (excluding model inference)
- Dashboard load < 3 seconds
- Handle 100k synthetic edges

Reliability

- Automatic error logging
- Database transaction safety

Scalability

- Modular architecture
- Independent AI services

Maintainability

- Type hints
- Docstrings
- Unit tests
- Layered architecture

Security

- CSRF Protection
- Authentication
- Authorization
- Environment variables
- Password hashing

Availability

Target

99%

---

# 9. High-Level Architecture

```
Browser
      │
      ▼
Django Templates
      │
      ▼
Views
      │
      ▼
Service Layer
      │
      ▼
AI Engine
      │
      ├── NetworkX
      ├── PyTorch
      ├── PyTorch Geometric
      ▼
Database
(PostgreSQL)
```

---

# 10. Modules

Module 1

Authentication

Responsibilities

- Login
- Logout
- Registration
- Permissions

---

Module 2

Synthetic Data Engine

Responsibilities

- Load Cities
- Generate Traffic
- Export Dataset

---

Module 3

Graph Engine

Responsibilities

- Build Graph
- Metrics
- Feature Engineering

---

Module 4

AI Engine

Responsibilities

- Train GCN
- Predict
- Save Model

---

Module 5

Visualization

Responsibilities

- Plot World Map
- Draw Network
- Display Risk

---

Module 6

Dashboard

Responsibilities

- Statistics
- Filters
- Charts

---

Module 7

REST API

Responsibilities

- Predictions
- Dataset
- Metrics
- History

---

Module 8

Administration

Responsibilities

- Manage Users
- Logs
- Monitoring

---

# 11. Use Cases

Use Case 1

Generate Dataset

Actor

Security Analyst

Flow

Login

↓

Generate Data

↓

Validate

↓

Store Dataset

---

Use Case 2

Train AI

Login

↓

Create Graph

↓

Train GCN

↓

Save Model

---

Use Case 3

View Dashboard

Login

↓

Run Prediction

↓

View Map

↓

Filter Results

↓

Export

---

# 12. User Stories

As a Security Analyst

I want to generate synthetic traffic

So that I can train anomaly detection models.

---

As an Administrator

I want to manage users

So that only authorized users access the system.

---

As a Researcher

I want to compare anomaly scores

So that I can evaluate model performance.

---

# 13. Constraints

Python 3.12

Django 5

PostgreSQL

Docker

PyTorch Geometric

Plotly

Open Source Libraries Only

---

# 14. Assumptions

GPU may not be available.

Synthetic data is acceptable.

Internet required only for deployment.

World city dataset is publicly available.

---

# 15. Acceptance Criteria

The project is complete when:

✔ Users can log in.

✔ Synthetic traffic is generated.

✔ Graph is constructed.

✔ GNN trains successfully.

✔ Predictions are stored.

✔ Interactive world map works.

✔ Dashboard loads correctly.

✔ APIs return valid responses.

✔ Docker deployment succeeds.

✔ Documentation is complete.

---

# 16. Future Enhancements

- Live network packet ingestion
- Kafka streaming
- Neo4j graph database
- Graph Attention Networks (GAT)
- GraphSAGE
- Temporal Graph Networks
- Explainable AI (XAI)
- Real-time anomaly detection
- Kubernetes deployment
- Multi-region cloud deployment

---

# Success Definition

The application should be indistinguishable from a professional enterprise cybersecurity analytics platform and demonstrate expertise in:

- Software Engineering
- Artificial Intelligence
- Graph Machine Learning
- Backend Development
- Data Engineering
- Data Visualization
- DevOps
- Production Deployment

End of Software Requirements Specification.