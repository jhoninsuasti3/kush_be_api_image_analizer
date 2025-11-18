# Multi-stage build for Kush Image Analyzer API
# Optimized for development and production

# ============================================================================
# Stage 1: Base Python Image
# ============================================================================
FROM python:3.11-slim AS python-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR="/tmp/poetry_cache" \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# ============================================================================
# Stage 2: Builder - Install Dependencies
# ============================================================================
FROM python-base AS python-builder

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    chmod +x $POETRY_HOME/bin/poetry

WORKDIR $PYSETUP_PATH

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry install --no-root --only main

# ============================================================================
# Stage 3: Development Image
# ============================================================================
FROM python-base AS development

# Install curl for healthchecks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=python-builder $VENV_PATH $VENV_PATH

# Create app user
RUN useradd -m -u 1000 app && \
    mkdir -p /app && \
    chown -R app:app /app

USER app
WORKDIR /app

# Copy application code
COPY --chown=app:app . .

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command (can be overridden by docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================================================
# Stage 4: Production Image
# ============================================================================
FROM python-base AS production

# Install only runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=python-builder $VENV_PATH $VENV_PATH

# Create app user
RUN useradd -m -u 1000 app && \
    mkdir -p /app && \
    chown -R app:app /app

USER app
WORKDIR /app

# Copy only necessary files
COPY --chown=app:app app ./app
COPY --chown=app:app pyproject.toml poetry.lock ./

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Production command (no reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]