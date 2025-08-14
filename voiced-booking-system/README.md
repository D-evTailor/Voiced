# VoiceAppoint - Appointment Booking SaaS Platform

## 🎯 Overview

VoiceAppoint is a modern multi-tenant SaaS system for automatic appointment booking via intelligent phone agents powered by Vapi.ai. The platform enables businesses to automate their appointment scheduling process while providing customers with a natural voice interface.

## 🏗️ Architecture

- **Frontend**: Next.js 14 with TypeScript, TailwindCSS, and Shadcn/ui
- **Backend**: Django 5.0+ with Django REST Framework
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Task Queue**: Celery
- **Real-time**: Django Channels + WebSockets
- **Voice AI**: Vapi.ai integration
- **Payments**: Stripe
- **Containerization**: Docker + Docker Compose

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git
- Make (optional, for convenience commands)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd voiced-booking-system
```

### 2. Quick Start (Recomendado)

```bash
# Script automático que configura todo
./scripts/start-dev.sh
```

### 3. Manual Setup

```bash
# Crear archivos de configuración
cp .env.example .env
cp backend/.env.example backend/.env

# Iniciar servicios
docker-compose up --build
```

### 4. Verificar Instalación

```bash
# Run migrations
docker-compose exec backend poetry run python manage.py migrate

# Create superuser
docker-compose exec backend poetry run python manage.py createsuperuser

# Load sample data (optional)
docker-compose exec backend poetry run python manage.py loaddata sample_data.json
```

### 4. Access Applications

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/docs
- **PgAdmin** (dev): http://localhost:8080
- **Redis Commander** (dev): http://localhost:8081

## 🛠️ Development

### Local Development (without Docker)

#### Backend Setup

```bash
cd backend
poetry install
poetry shell
poetry run python manage.py migrate
poetry run python manage.py runserver
```

#### Frontend Setup

```bash
cd frontend
pnpm install
pnpm dev
```

### Useful Commands

#### Docker Commands

```bash
# Start development environment
make dev

# Start production environment
make prod

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Rebuild services
docker-compose up --build backend
docker-compose up --build frontend

# Run tests
make test

# Clean everything
make clean
```

#### Backend Commands

```bash
# Enter backend container
docker-compose exec backend bash

# Run migrations
docker-compose exec backend poetry run python manage.py migrate

# Create migrations
docker-compose exec backend poetry run python manage.py makemigrations

# Run tests
docker-compose exec backend poetry run pytest

# Django shell
docker-compose exec backend poetry run python manage.py shell

# Collect static files
docker-compose exec backend poetry run python manage.py collectstatic
```

#### Frontend Commands

```bash
# Enter frontend container
docker-compose exec frontend sh

# Install dependencies
docker-compose exec frontend pnpm install

# Run tests
docker-compose exec frontend pnpm test

# Build for production
docker-compose exec frontend pnpm build
```

## 📂 Project Structure

```
voiced-booking-system/
├── 📋 README.md
├── 🐳 docker-compose.yml
├── 🐳 docker-compose.override.yml    # Development overrides
├── 🐳 docker-compose.prod.yml        # Production configuration
├── 🔧 Makefile
├── 📝 .env.example
├── 🚫 .gitignore
├── 📚 docs/
├── 🎨 frontend/                       # Next.js application
├── ⚙️ backend/                        # Django application
├── 🌐 nginx/                          # Nginx configuration
├── 📜 scripts/                        # Utility scripts
└── 🔄 .github/workflows/              # CI/CD workflows
```

## 🧪 Testing

### Run All Tests

```bash
make test
```

### Backend Tests

```bash
docker-compose exec backend poetry run pytest
docker-compose exec backend poetry run pytest --cov
```

### Frontend Tests

```bash
docker-compose exec frontend pnpm test
docker-compose exec frontend pnpm test:coverage
```

## 🌍 Internationalization

The platform supports multiple languages (Spanish and English by default):

- **Backend**: Django i18n framework
- **Frontend**: Next.js built-in i18n support
- **Database**: Locale-aware content management

### Add New Language

1. Add language code to `LANGUAGES` in Django settings
2. Run `python manage.py makemessages -l <language_code>`
3. Translate messages in `.po` files
4. Run `python manage.py compilemessages`
5. Add translations to frontend `locales/` directory

## 🔒 Security

- JWT authentication
- CORS configuration
- Environment-based secrets
- Rate limiting
- Input validation
- SQL injection protection
- XSS protection

## 🚀 Deployment

### Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Initialize production database
docker-compose -f docker-compose.prod.yml exec backend poetry run python manage.py migrate
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required for production
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@host:port/db
STRIPE_SECRET_KEY=sk_live_...
VAPI_API_KEY=your-vapi-key
```

## 🔧 API Documentation

### Endpoints

- **Authentication**: `/api/v1/auth/`
- **Users**: `/api/v1/users/`
- **Businesses**: `/api/v1/businesses/`
- **Services**: `/api/v1/services/`
- **Appointments**: `/api/v1/appointments/`
- **Vapi Integration**: `/api/v1/vapi/`
- **Payments**: `/api/v1/payments/`

### Swagger Documentation

Access interactive API documentation at: http://localhost:8000/api/docs


### Development Workflow

1. Create `.env` from `.env.example`
2. Start development environment: `make dev`
3. Make changes
4. Run tests: `make test`
5. Format code: `make format`
6. Commit and push

## 📊 Monitoring

- **Backend**: Django logging + Sentry
- **Frontend**: Vercel Analytics (optional)
- **Infrastructure**: Docker health checks
- **Database**: PostgreSQL logging
- **Queue**: Celery monitoring

## 🆘 Troubleshooting

### Common Issues

#### Docker Issues

```bash
# Reset everything
docker-compose down -v
docker system prune -a
docker-compose up --build
```

#### Database Issues

```bash
# Reset database
docker-compose down -v
docker-compose up db
docker-compose exec backend poetry run python manage.py migrate
```

#### Frontend Issues

```bash
# Clear Next.js cache
docker-compose exec frontend rm -rf .next
docker-compose restart frontend
```

#### Permission Issues

```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```
