# Makefile for VoiceAppoint Development

.PHONY: help dev prod build test clean format lint docs setup

# Default target
help: ## Show this help message
	@echo "VoiceAppoint Development Commands"
	@echo "================================="
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# Development Commands
setup: ## Initial project setup
	@echo "🚀 Setting up VoiceAppoint development environment..."
	@cp .env.example .env || echo ".env already exists"
	@echo "📝 Please edit .env file with your configuration"
	@echo "✅ Setup complete! Run 'make dev' to start development"

dev: ## Start development environment
	@echo "🔥 Starting development environment..."
	@docker-compose up

dev-build: ## Build and start development environment
	@echo "🔨 Building and starting development environment..."
	@docker-compose up --build

dev-bg: ## Start development environment in background
	@echo "🔄 Starting development environment in background..."
	@docker-compose up -d

stop: ## Stop all services
	@echo "⏹️  Stopping all services..."
	@docker-compose down

restart: ## Restart all services
	@echo "🔄 Restarting all services..."
	@docker-compose restart

# Production Commands
prod: ## Start production environment
	@echo "🚀 Starting production environment..."
	@docker-compose -f docker-compose.prod.yml up -d

prod-build: ## Build and start production environment
	@echo "🔨 Building production environment..."
	@docker-compose -f docker-compose.prod.yml up --build -d

prod-stop: ## Stop production environment
	@echo "⏹️  Stopping production environment..."
	@docker-compose -f docker-compose.prod.yml down

# Database Commands
db-migrate: ## Run database migrations
	@echo "📊 Running database migrations..."
	@docker-compose exec backend poetry run python manage.py migrate

db-reset: ## Reset database (WARNING: Destroys all data)
	@echo "⚠️  WARNING: This will destroy all database data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		docker-compose down -v; \
		docker-compose up -d db redis; \
		sleep 5; \
		docker-compose exec backend poetry run python manage.py migrate; \
	fi

db-shell: ## Access database shell
	@echo "🐘 Opening database shell..."
	@docker-compose exec db psql -U postgres -d voiceappoint

superuser: ## Create Django superuser
	@echo "👤 Creating Django superuser..."
	@docker-compose exec backend poetry run python manage.py createsuperuser

# Backend Commands
backend-shell: ## Access backend container shell
	@echo "🐍 Opening backend shell..."
	@docker-compose exec backend bash

backend-django-shell: ## Access Django shell
	@echo "🐍 Opening Django shell..."
	@docker-compose exec backend poetry run python manage.py shell

backend-test: ## Run backend tests
	@echo "🧪 Running backend tests..."
	@docker-compose exec backend poetry run pytest

backend-test-cov: ## Run backend tests with coverage
	@echo "🧪 Running backend tests with coverage..."
	@docker-compose exec backend poetry run pytest --cov

backend-lint: ## Lint backend code
	@echo "🔍 Linting backend code..."
	@docker-compose exec backend poetry run black .
	@docker-compose exec backend poetry run isort .
	@docker-compose exec backend poetry run flake8

# Frontend Commands
frontend-shell: ## Access frontend container shell
	@echo "⚛️  Opening frontend shell..."
	@docker-compose exec frontend sh

frontend-test: ## Run frontend tests
	@echo "🧪 Running frontend tests..."
	@docker-compose exec frontend pnpm test

frontend-test-watch: ## Run frontend tests in watch mode
	@echo "🧪 Running frontend tests in watch mode..."
	@docker-compose exec frontend pnpm test:watch

frontend-lint: ## Lint frontend code
	@echo "🔍 Linting frontend code..."
	@docker-compose exec frontend pnpm lint:fix
	@docker-compose exec frontend pnpm format

frontend-build: ## Build frontend for production
	@echo "🏗️  Building frontend..."
	@docker-compose exec frontend pnpm build

# Testing Commands
test: ## Run all tests
	@echo "🧪 Running all tests..."
	@make backend-test
	@make frontend-test

test-watch: ## Run tests in watch mode
	@echo "🧪 Running tests in watch mode..."
	@docker-compose exec -d backend poetry run pytest-watch
	@docker-compose exec frontend pnpm test:watch

# Code Quality
format: ## Format all code
	@echo "✨ Formatting code..."
	@make backend-lint
	@make frontend-lint

lint: format ## Alias for format

# Utility Commands
logs: ## Show logs for all services
	@docker-compose logs -f

logs-backend: ## Show backend logs
	@docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	@docker-compose logs -f frontend

logs-db: ## Show database logs
	@docker-compose logs -f db

build: ## Build all Docker images
	@echo "🔨 Building all Docker images..."
	@docker-compose build

rebuild: ## Rebuild all Docker images from scratch
	@echo "🔨 Rebuilding all Docker images..."
	@docker-compose build --no-cache

clean: ## Clean up Docker resources
	@echo "🧹 Cleaning up Docker resources..."
	@docker-compose down -v
	@docker system prune -f
	@docker volume prune -f

clean-all: ## Clean up everything (images, containers, volumes)
	@echo "🧹 Cleaning up everything..."
	@docker-compose down -v --rmi all
	@docker system prune -a -f
	@docker volume prune -f

# Documentation
docs: ## Generate API documentation
	@echo "📚 Generating API documentation..."
	@docker-compose exec backend poetry run python manage.py spectacular --file schema.yml

# Health Checks
health: ## Check health of all services
	@echo "🏥 Checking service health..."
	@docker-compose ps

status: health ## Alias for health

# Development Tools
install-tools: ## Install development tools locally
	@echo "🛠️  Installing development tools..."
	@poetry install
	@cd frontend && pnpm install

update-deps: ## Update dependencies
	@echo "📦 Updating dependencies..."
	@docker-compose exec backend poetry update
	@docker-compose exec frontend pnpm update

# Backup and Restore
backup-db: ## Backup database
	@echo "💾 Backing up database..."
	@mkdir -p backups
	@docker-compose exec db pg_dump -U postgres voiceappoint > backups/db_backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restore database from backup (specify BACKUP_FILE)
	@echo "📥 Restoring database from backup..."
	@docker-compose exec -T db psql -U postgres voiceappoint < $(BACKUP_FILE)

# SSL and Security
generate-ssl: ## Generate self-signed SSL certificates
	@echo "🔒 Generating SSL certificates..."
	@mkdir -p nginx/ssl
	@openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout nginx/ssl/cert.key \
		-out nginx/ssl/cert.crt \
		-subj "/C=ES/ST=Madrid/L=Madrid/O=VoiceAppoint/CN=localhost"

# Monitoring
monitor: ## Start monitoring tools
	@echo "📊 Starting monitoring tools..."
	@docker-compose -f docker-compose.monitoring.yml up -d

# Quick Actions
quick-start: setup dev-build db-migrate superuser ## Complete quick start setup
	@echo "🎉 VoiceAppoint is ready!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "Admin: http://localhost:8000/admin"

fresh-start: clean quick-start ## Clean start from scratch
