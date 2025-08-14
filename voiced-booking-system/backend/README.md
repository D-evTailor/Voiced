# VoiceAppoint Backend

Django REST API backend for the VoiceAppoint multi-tenant appointment booking system with voice agent integration.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Install dependencies:**
   ```bash
   make install
   # or
   poetry install
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run migrations:**
   ```bash
   make migrate
   # or
   poetry run python manage.py migrate
   ```

4. **Create superuser:**
   ```bash
   make superuser
   # or
   poetry run python manage.py createsuperuser
   ```

5. **Start development server:**
   ```bash
   make dev
   # or
   poetry run python manage.py runserver
   ```

## 🐳 Docker Development

```bash
# Start all services
docker-compose up

# Run migrations
docker-compose exec backend poetry run python manage.py migrate

# Create superuser
docker-compose exec backend poetry run python manage.py createsuperuser
```

## 📚 API Documentation

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

## 🏗️ Architecture

### Apps Structure

- **users:** User management and authentication
- **businesses:** Multi-tenant business configuration
- **services:** Service definitions and providers
- **appointments:** Core appointment booking system
- **payments:** Stripe payment integration
- **vapi_integration:** Voice agent integration
- **notifications:** Email/SMS notifications
- **analytics:** Business metrics and reporting

### Key Features

- **Multi-tenant SaaS:** Each business is isolated
- **JWT Authentication:** Secure API access
- **Internationalization:** Spanish/English support
- **Real-time Updates:** WebSocket integration
- **Async Tasks:** Celery for background processing
- **API Documentation:** Auto-generated OpenAPI docs

## 🧪 Testing

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run with coverage
make test-cov
```

## 🔧 Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make type-check
```

## 🌍 Internationalization

```bash
# Extract translatable strings
make makemessages

# Compile translations
make compilemessages
```

## 📊 Background Tasks

```bash
# Start Celery worker
make celery-worker

# Start Celery beat scheduler
make celery-beat

# Monitor with Flower
make celery-flower
```

## 🔑 Environment Variables

See `.env.example` for all available configuration options.

### Required Settings

- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `VAPI_API_KEY`: Vapi.ai API key
- `STRIPE_SECRET_KEY`: Stripe secret key

## 📈 Monitoring

- **Health Checks:** Built-in health monitoring
- **Logging:** Structured logging with file rotation
- **Sentry:** Error tracking (production)
- **Metrics:** Business analytics and reporting

## 🚀 Deployment

```bash
# Production checks
make check

# Collect static files
make collect-static

# Export requirements
make requirements
```

## 📄 API Endpoints

### Authentication
- `POST /api/v1/auth/token/` - Obtain JWT token
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token
- `POST /api/v1/auth/register/` - User registration

### Business Management
- `GET /api/v1/businesses/` - List businesses
- `POST /api/v1/businesses/` - Create business
- `GET /api/v1/businesses/{id}/` - Business details

### Appointments
- `GET /api/v1/appointments/` - List appointments
- `POST /api/v1/appointments/` - Create appointment
- `GET /api/v1/appointments/availability/` - Check availability

### Vapi Integration
- `POST /api/v1/vapi/tools/book-appointment/` - Book via voice
- `POST /api/v1/vapi/webhooks/appointment/` - Appointment webhook

## 🤝 Contributing

1. Follow PEP 8 style guide
2. Write tests for new features
3. Update documentation
4. Use conventional commits

## 📞 Support

For technical support and questions:
- Documentation: `/api/docs/`
- Issues: Create GitHub issues
- Email: dev@voiceappoint.com
