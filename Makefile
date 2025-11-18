.PHONY: install install-all lint format test test-cov test-watch run dev docker-build docker-up docker-down create-tables deploy-dev deploy-staging deploy-prod logs-dev logs-staging logs-prod clean help

# ============================================================================
# INSTALLATION
# ============================================================================

## install: Install production dependencies only
install:
	poetry install --only main

## install-all: Install all dependencies (production + development)
install-all:
	poetry install --with code-quality,test

## install-pre-commit: Install pre-commit hooks
install-pre-commit:
	poetry run pre-commit install

# ============================================================================
# CODE QUALITY
# ============================================================================

## lint: Run linters (ruff check + format check + mypy)
lint:
	@echo "🔍 Running Ruff linter..."
	poetry run ruff check .
	@echo "✨ Checking code formatting..."
	poetry run ruff format --check .
	@echo "🔬 Running mypy type checker..."
	poetry run mypy app/

## format: Auto-format code with ruff
format:
	@echo "✨ Formatting code with Ruff..."
	poetry run ruff format .
	@echo "🔧 Auto-fixing linting issues..."
	poetry run ruff check --fix .

## pre-commit: Run pre-commit hooks on all files
pre-commit:
	poetry run pre-commit run --all-files

# ============================================================================
# TESTING
# ============================================================================

## test: Run all tests
test:
	@echo "🧪 Running tests..."
	poetry run pytest tests/ -v

## test-cov: Run tests with coverage report
test-cov:
	@echo "🧪 Running tests with coverage..."
	poetry run pytest tests/ --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml

## test-unit: Run only unit tests
test-unit:
	poetry run pytest tests/unit/ -v

## test-integration: Run only integration tests
test-integration:
	poetry run pytest tests/integration/ -v

## test-e2e: Run only end-to-end tests
test-e2e:
	poetry run pytest tests/e2e/ -v

## test-fast: Run tests without coverage (faster)
test-fast:
	@echo "🧪 Running tests (fast mode)..."
	poetry run pytest tests/ -v -x --ff

## test-watch: Run tests in watch mode (requires pytest-watch)
test-watch:
	poetry run ptw tests/ -v

## test-failed: Re-run only failed tests
test-failed:
	poetry run pytest tests/ --lf -v

## test-summary: Run tests with summary report
test-summary:
	@echo "🧪 Running tests with summary..."
	poetry run pytest tests/ -v --tb=short --cov=app --cov-report=term-missing:skip-covered

# ============================================================================
# DEVELOPMENT SERVER
# ============================================================================

## run: Run FastAPI development server
run:
	@echo "🚀 Starting FastAPI development server..."
	poetry run fastapi dev app/main.py

## dev: Alias for run
dev: run

# ============================================================================
# DOCKER
# ============================================================================

## docker-build: Build Docker image
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t kush-image-analyzer:latest .

## docker-up: Start all services with docker-compose
docker-up:
	@echo "🐳 Starting Docker services..."
	docker-compose up --build

## docker-down: Stop all Docker services
docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose down -v

## docker-logs: View Docker logs
docker-logs:
	docker-compose logs -f

# ============================================================================
# AWS / DATABASE
# ============================================================================

## create-tables: Create DynamoDB tables (local or AWS)
create-tables:
	@echo "📊 Creating DynamoDB tables..."
	poetry run python scripts/create_tables.py

# ============================================================================
# DEPLOYMENT
# ============================================================================

## sam-build: Build SAM application
sam-build:
	@echo "🏗️  Building SAM application..."
	sam build

## sam-local: Run SAM application locally
sam-local: sam-build
	@echo "🏃 Running SAM application locally..."
	sam local start-api

## deploy-dev: Deploy to development environment
deploy-dev: sam-build
	@echo "🚀 Deploying to development..."
	sam deploy --config-env dev

## deploy-staging: Deploy to staging environment
deploy-staging: sam-build
	@echo "🚀 Deploying to staging..."
	sam deploy --config-env staging

## deploy-prod: Deploy to production environment
deploy-prod: sam-build
	@echo "🚀 Deploying to production..."
	sam deploy --config-env prod

# ============================================================================
# LOGS
# ============================================================================

## logs-dev: Tail development logs
logs-dev:
	sam logs --stack-name kush-image-analyzer-dev --tail

## logs-staging: Tail staging logs
logs-staging:
	sam logs --stack-name kush-image-analyzer-staging --tail

## logs-prod: Tail production logs
logs-prod:
	sam logs --stack-name kush-image-analyzer-prod --tail

# ============================================================================
# CLEANUP
# ============================================================================

## clean: Remove Python artifacts and cache files
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	rm -rf dist build *.egg-info
	@echo "✨ Cleanup complete!"

## clean-all: Remove all generated files including venv
clean-all: clean
	rm -rf .venv poetry.lock

# ============================================================================
# UTILITIES
# ============================================================================

## env: Create .env file from .env.example
env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file from .env.example"; \
		echo "⚠️  Please update .env with your actual values"; \
	else \
		echo "⚠️  .env file already exists"; \
	fi

## check: Run all quality checks (lint + test + coverage)
check: lint test-cov
	@echo "✅ All checks passed!"

## ci: Run CI pipeline locally (same as GitHub Actions)
ci: install-all lint test-cov
	@echo "✅ CI pipeline completed successfully!"

# ============================================================================
# HELP
# ============================================================================

## help: Show this help message
help:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Kush Image Analyzer API - Makefile Commands"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "📦 Installation:"
	@grep -E '^## install' Makefile | sed 's/## /  make /'
	@echo ""
	@echo "🔍 Code Quality:"
	@grep -E '^## (lint|format|pre-commit)' Makefile | sed 's/## /  make /'
	@echo ""
	@echo "🧪 Testing:"
	@grep -E '^## test' Makefile | sed 's/## /  make /'
	@echo ""
	@echo "🚀 Development:"
	@grep -E '^## (run|dev)' Makefile | sed 's/## /  make /'
	@echo ""
	@echo "🐳 Docker:"
	@grep -E '^## docker' Makefile | sed 's/## /  make /'
	@echo ""
	@echo "☁️  Deployment:"
	@grep -E '^## (sam|deploy|logs)' Makefile | sed 's/## /  make /'
	@echo ""
	@echo "🛠️  Utilities:"
	@grep -E '^## (env|check|ci|clean|help)' Makefile | sed 's/## /  make /'
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Default target
.DEFAULT_GOAL := help