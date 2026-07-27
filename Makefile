.PHONY: help dev up down build logs migrate seed test lint clean

# =============================================================================
# Sentinel AI — Developer Commands
# =============================================================================

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Docker ---
up: ## Start all services in detached mode
	docker compose up -d

down: ## Stop all services
	docker compose down

build: ## Build all Docker images
	docker compose build

logs: ## Tail logs from all services
	docker compose logs -f

logs-backend: ## Tail backend logs
	docker compose logs -f backend

logs-frontend: ## Tail frontend logs
	docker compose logs -f frontend

# --- Database ---
migrate: ## Run Alembic migrations
	cd backend && alembic upgrade head

migrate-generate: ## Auto-generate a new migration (usage: make migrate-generate msg="add users table")
	cd backend && alembic revision --autogenerate -m "$(msg)"

migrate-rollback: ## Rollback last migration
	cd backend && alembic downgrade -1

seed: ## Seed initial admin user
	cd backend && python -m app.db.init_db

# --- Development ---
dev-backend: ## Run backend dev server
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend dev server
	cd frontend && npm run dev

# --- Testing ---
test: ## Run all backend tests
	cd backend && pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage report
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

# --- Utilities ---
lint: ## Lint backend code
	cd backend && ruff check app/ tests/

clean: ## Remove all containers, volumes, and cached files
	docker compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
