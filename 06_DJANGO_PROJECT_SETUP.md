# Global Network Anomaly Tracker (GNAT)

# Django Project Setup Guide

Version: 1.0

Status:
Approved

Python Version:
3.12+

Framework:
Django 5

Database:
PostgreSQL

Development Environment:
VS Code

Operating Systems

• Windows 11
• Ubuntu 24.04
• macOS

---

# Objective

Create a production-ready Django project with enterprise configuration before any application code is written.

This setup will be the foundation for every future module.

---

# Phase 1

Development Environment

Install

Python 3.12+

Git

Docker Desktop

PostgreSQL

Redis

Visual Studio Code

Recommended VS Code Extensions

Python

Pylance

Black Formatter

Docker

GitLens

Error Lens

Markdown Preview

Thunder Client

---

# Phase 2

Create Project

Project Name

Global-Network-Anomaly-Tracker

Django Project Name

config

Repository

github.com/<username>/Global-Network-Anomaly-Tracker

Default Branch

main

Development Branch

develop

Feature Branch Format

feature/module-name

Bugfix Branch

bugfix/issue-name

---

# Phase 3

Virtual Environment

Create

Python Virtual Environment

Activate Environment

Upgrade

pip

wheel

setuptools

---

# Phase 4

Install Dependencies

Core

Django

Django REST Framework

django-filter

django-environ

django-cors-headers

Database

psycopg

AI

torch

torch-geometric

networkx

numpy

pandas

scikit-learn

Visualization

plotly

Development

pytest

pytest-django

coverage

black

isort

flake8

mypy

pre-commit

rich

gunicorn

whitenoise

celery

redis

---

# Phase 5

Environment Variables

Create

.env

Never commit

.env

Create

.env.example

Variables

SECRET_KEY

DEBUG

ALLOWED_HOSTS

DATABASE_NAME

DATABASE_USER

DATABASE_PASSWORD

DATABASE_HOST

DATABASE_PORT

REDIS_URL

TIME_ZONE

LANGUAGE_CODE

EMAIL_HOST

EMAIL_PORT

EMAIL_USERNAME

EMAIL_PASSWORD

MODEL_DIRECTORY

DATA_DIRECTORY

LOG_DIRECTORY

---

# Phase 6

Settings Structure

config/settings/

base.py

development.py

production.py

testing.py

Responsibilities

base.py

Common configuration

development.py

Development overrides

production.py

Production configuration

testing.py

Testing configuration

---

# Phase 7

Installed Applications

Django Apps

django.contrib.admin

django.contrib.auth

django.contrib.sessions

django.contrib.messages

django.contrib.staticfiles

Third Party

rest_framework

django_filters

corsheaders

Project Apps

accounts

dashboard

graph_engine

ai_engine

visualization

analytics

reports

notifications

api

common

---

# Phase 8

Logging

Configure logging

Console

Application Logs

Training Logs

Prediction Logs

Error Logs

Log Format

Timestamp

Level

Module

Message

Store logs inside

logs/

---

# Phase 9

Database Configuration

Engine

PostgreSQL

Use environment variables

Never hardcode credentials

Migration strategy

One migration per feature

---

# Phase 10

Static Configuration

Directories

static/

media/

templates/

logs/

data/

models/

Automatically create directories if missing.

---

# Phase 11

Authentication

Default

Django Authentication

Future

JWT

OAuth2

Google Login

GitHub Login

---

# Phase 12

REST Framework Configuration

Authentication

Session Authentication

Token Authentication (future)

Permissions

Authenticated users by default

Pagination

Enabled

Filtering

Enabled

API Version

v1

---

# Phase 13

Celery

Broker

Redis

Purpose

Background Tasks

Model Training

Dataset Generation

Report Generation

Email Notifications

Future

Scheduled Retraining

---

# Phase 14

Security

CSRF Enabled

Secure Cookies

Password Validation

Security Middleware

Clickjacking Protection

HTTPS Ready

Environment Variables Only

---

# Phase 15

Code Quality

Formatter

Black

Import Sorting

isort

Linting

Flake8

Static Typing

mypy

Git Hooks

pre-commit

Coverage

pytest + coverage

---

# Phase 16

Docker

Containers

Django

PostgreSQL

Redis

Nginx (Production)

Volumes

Media

Static

Logs

Models

Data

---

# Phase 17

Git Workflow

Branches

main

develop

feature/*

bugfix/*

release/*

Commit Style

feat:

fix:

docs:

refactor:

test:

style:

ci:

---

# Phase 18

Initial Django Apps

accounts

dashboard

graph_engine

ai_engine

visualization

analytics

reports

notifications

api

common

Every app must be created immediately after project initialization.

---

# Phase 19

Initial Folder Verification

Verify

config/

apps/

data/

docs/

models/

deployment/

logs/

tests/

requirements/

static/

templates/

media/

.github/

---

# Phase 20

Success Checklist

Project initializes successfully.

Virtual environment works.

Dependencies install correctly.

PostgreSQL connects successfully.

Redis connects successfully.

Django server starts.

Admin page loads.

Logging works.

Environment variables load correctly.

Docker containers start successfully.

No warnings.

No linting errors.

No migration errors.

---

# Expected Deliverables

At the end of this phase there should be

✔ Production Django Project

✔ PostgreSQL Connected

✔ Redis Connected

✔ Docker Ready

✔ Logging Configured

✔ REST Framework Installed

✔ Project Apps Created

✔ Environment Variables Configured

✔ Development Standards Established

---

# GLM-4.7 Generation Rules

When generating code for this phase:

Generate complete production-ready files.

Never use placeholder values.

Include docstrings.

Include type hints.

Include logging.

Separate development and production settings.

Follow PEP8.

Generate reusable code.

Explain every architectural decision.

After generating each file:

1. Explain its purpose.
2. Explain dependencies.
3. Explain configuration.
4. Explain how to test.
5. Wait for approval before generating the next file.

---

End of Django Project Setup Guide