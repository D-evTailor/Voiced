# VoiceAppoint Backend Makefile
# Useful commands for development and deployment

.PHONY: help install dev test lint format clean migrations migrate shell superuser collect-static

# Default target
help:
	@echo "VoiceAppoint Backend - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     - Install dependencies with Poetry"
	@echo "  dev         - Run development server"
	@echo "  shell       - Open Django shell"
	@echo "  superuser   - Create superuser"
	@echo ""
	@echo "Database:"
	@echo "  migrations  - Create migrations"
	@echo "  migrate     - Apply migrations"
	@echo "  reset-db    - Reset database (development only)"
	@echo ""
	@echo "Testing:"
	@echo "  test        - Run all tests"
	@echo "  test-unit   - Run unit tests only"
	@echo "  test-cov    - Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint        - Run linting (flake8)"
	@echo "  format      - Format code (black + isort)"
	@echo "  type-check  - Run type checking (mypy)"
	@echo ""
	@echo "Internationalization:"
	@echo "  makemessages - Extract translatable strings"
	@echo "  compilemessages - Compile translation files"
	@echo ""
	@echo "Deployment:"
	@echo "  collect-static - Collect static files"
	@echo "  check       - Run Django system checks"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       - Clean cache and temporary files"
	@echo "  requirements - Export requirements.txt"

# Development commands
install:
	poetry install

dev:
	poetry run python manage.py runserver

shell:
	poetry run python manage.py shell

superuser:
	poetry run python manage.py createsuperuser

# Database commands
migrations:
	poetry run python manage.py makemigrations

migrate:
	poetry run python manage.py migrate

reset-db:
	poetry run python manage.py flush --noinput
	poetry run python manage.py migrate

# Testing commands
test:
	poetry run pytest

test-unit:
	poetry run pytest -m "not integration and not slow"

test-cov:
	poetry run pytest --cov=. --cov-report=html --cov-report=term

# Code quality commands
lint:
	poetry run flake8 .

format:
	poetry run black .
	poetry run isort .

type-check:
	poetry run mypy .

# Internationalization commands
makemessages:
	poetry run python manage.py makemessages -l es
	poetry run python manage.py makemessages -l en

compilemessages:
	poetry run python manage.py compilemessages

# Deployment commands
collect-static:
	poetry run python manage.py collectstatic --noinput

check:
	poetry run python manage.py check

# Utility commands
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

# Docker commands
docker-build:
	docker build -t voiceappoint-backend .

docker-run:
	docker run -p 8000:8000 voiceappoint-backend

# Celery commands
celery-worker:
	poetry run celery -A core worker -l info

celery-beat:
	poetry run celery -A core beat -l info

celery-flower:
	poetry run celery -A core flower
