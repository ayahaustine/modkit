.PHONY: help install dev build up down logs migrate migrate-create lint test

COMPOSE      = docker compose
COMPOSE_DEV  = $(COMPOSE) -f docker-compose.dev.yml
COMPOSE_PROD = $(COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml

# ── Help ──────────────────────────────────────────────────────────────────────
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ── Local dev (no Docker) ─────────────────────────────────────────────────────
install: ## Install all dependencies (uv + npm)
	cd backend && uv sync
	cd frontend && npm install
	cd docs && npm install
	cd e2e && npm install

dev-backend: ## Run backend dev server
	cd backend && uv run uvicorn main:app --reload --port 8000

dev-frontend: ## Run frontend dev server
	cd frontend && npm run dev

dev-docs: ## Run docs dev server
	cd docs && npm start

# ── Docker ────────────────────────────────────────────────────────────────────
up: ## Start all services (dev mode)
	$(COMPOSE_DEV) up -d --build

down: ## Stop all services
	$(COMPOSE_DEV) down

logs: ## Tail logs
	$(COMPOSE_DEV) logs -f

up-prod: ## Start all services (production)
	$(COMPOSE_PROD) up -d --build

down-prod: ## Stop production services
	$(COMPOSE_PROD) down

# ── Database ──────────────────────────────────────────────────────────────────
migrate: ## Run Alembic migrations
	cd backend && uv run alembic upgrade head

migrate-create: ## Create a new migration (make migrate-create msg="description")
	cd backend && uv run alembic revision --autogenerate -m "$(msg)"

migrate-down: ## Rollback one migration
	cd backend && uv run alembic downgrade -1

create-superuser: ## Create or promote a superuser account
	docker exec -it modkit-backend-1 python scripts/create_superuser.py

# ── Quality ───────────────────────────────────────────────────────────────────
lint: ## Lint backend with ruff
	cd backend && uv run ruff check . && uv run ruff format --check .

format: ## Auto-format backend
	cd backend && uv run ruff check --fix . && uv run ruff format .

test: ## Run backend tests
	cd backend && uv run pytest

lint-frontend: ## Lint frontend
	cd frontend && npm run lint

# ── Build ─────────────────────────────────────────────────────────────────────
build: ## Build all Docker images
	$(COMPOSE) build

build-docs: ## Build docs static site
	cd docs && npm run build

# ── E2E ───────────────────────────────────────────────────────────────────────
e2e: ## Run Playwright e2e tests (stack must be running)
	cd e2e && npm test

e2e-headed: ## Run e2e tests in headed mode
	cd e2e && npm run test:headed

e2e-ui: ## Open Playwright UI runner
	cd e2e && npm run test:ui

e2e-report: ## Show the last Playwright HTML report
	cd e2e && npm run test:report
