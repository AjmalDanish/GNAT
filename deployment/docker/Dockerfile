# ============================================================================
# Global Network Anomaly Tracker - Dockerfile
# ============================================================================
#
# Multi-stage build for production-ready Docker image
#
# Build stages:
# 1. builder - Install build dependencies
# 2. runtime - Runtime environment only
#
# Build:
#   docker build -f deployment/docker/Dockerfile -t gnat:latest .
#
# Run:
#   docker run -p 8000:8000 gnat:latest
#
# ============================================================================

# --------------------------------------------------------------------------
# Base Stage
# --------------------------------------------------------------------------
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build dependencies
    build-essential \
    gcc \
    g++ \
    # Dependencies for PostgreSQL
    libpq-dev \
    # Dependencies for some Python packages
    libssl-dev \
    libffi-dev \
    # Dependencies for geospatial (if needed)
    binutils \
    libproj-dev \
    gdal-bin \
    # Dependencies for graph libraries
    libgomp1 \
    # Utilities
    curl \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# --------------------------------------------------------------------------
# Builder Stage
# --------------------------------------------------------------------------
FROM base as builder

# Install Python dependencies
COPY requirements/ ./requirements/
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements/base.txt

# --------------------------------------------------------------------------
# Runtime Stage
# --------------------------------------------------------------------------
FROM base as runtime

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user
RUN useradd -m -u 1000 gnat && \
    mkdir -p /app /app/staticfiles /app/media /app/models /app/logs /app/data && \
    chown -R gnat:gnat /app

# Copy application code
COPY --chown=gnat:gnat . /app/

# Install production dependencies
RUN pip install --no-cache-dir -r requirements/production.txt || true

# Switch to non-root user
USER gnat
WORKDIR /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Default command
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--threads", "4", \
     "--worker-class", "gthread", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]