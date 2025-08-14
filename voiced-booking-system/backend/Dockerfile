# Multi-stage Dockerfile for Django Backend
# ===========================================

# Development stage
FROM python:3.11-slim as development

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        postgresql-client \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.3

# Set work directory
WORKDIR /app

# Copy Poetry configuration
COPY pyproject.toml poetry.lock* ./

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-root \
    && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY . .

# Create static and media directories
RUN mkdir -p static media

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Default command for development
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

# Production stage
FROM development as production

# Switch back to root for production setup
USER root

# Install production dependencies only
RUN poetry install --only=main --no-dev

# Collect static files (will run in CMD if needed)
RUN poetry run python manage.py collectstatic --noinput --clear || echo "Collectstatic will run at startup"

# Switch back to app user
USER appuser

# Production command
CMD ["sh", "-c", "poetry run python manage.py migrate --noinput && poetry run python manage.py collectstatic --noinput && poetry run gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2 --timeout 60"]
