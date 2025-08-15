# VoiceAppoint - Project Architecture

## 📋 Project Description
Multi-tenant SaaS system for automatic appointment booking via phone agent (Vapi), with customized calendars for each business.

## 🏗️ General Architecture

```
voiced-booking-system/
├── docker-compose.yml
├── docker-compose.override.yml      # Development override
├── docker-compose.prod.yml          # Production
├── .env.example
├── .gitignore
├── README.md
├── Makefile                         # Useful commands
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   ├── VAPI_INTEGRATION.md
│   └── VAPI_INTEGRATION_API_DOC.md     # Complete VAPI API documentation
├── frontend/                        # Next.js + Tailwind
│   └── Dockerfile                   # Frontend Docker image
├── backend/                         # Django REST Framework
│   └── Dockerfile                   # Backend Docker image
├── nginx/                           # Reverse Proxy
│   ├── nginx.conf                   # Nginx configuration
│   └── ssl/                         # SSL certificates (prod)
└── scripts/                         # Deployment scripts
    ├── setup.sh                     # Initial setup
    ├── deploy.sh                    # Deployment script
    └── backup.sh                    # Database backup
```

## 🛠️ Technology Stack

### **Frontend - Next.js**
- **Framework**: Next.js 14+ (App Router)
- **Package Manager**: pnpm
- **Styling**: TailwindCSS + Shadcn/ui
- **Forms**: React Hook Form + Zod validation
- **State Management**: Zustand
- **API Client**: TanStack Query (React Query)
- **Authentication**: NextAuth.js
- **TypeScript**: Full TypeScript support
- **Icons**: Lucide React
- **Date/Time**: date-fns
- **Charts**: Recharts


### **Backend - Django**
- **Framework**: Django 5.0+
- **API**: Django REST Framework
- **Database**: PostgreSQL 15
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Async Tasks**: Celery + Redis
- **Real-time**: Django Channels + WebSockets
- **Payments**: Stripe (stripe-python)
- **CORS**: django-cors-headers
- **Environment**: python-decouple
- **Media Storage**: Pillow + django-storages
- **API Documentation**: drf-spectacular (OpenAPI)

### **Infrastructure**
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **Cache/Message Broker**: Redis
- **Database**: PostgreSQL
- **File Storage**: Cloud Storage (configurable)
- **Monitoring**: Sentry
- **CI/CD**: GitHub Actions

### **External Integrations**
- **Voice Agent**: Vapi.ai (Complete API integration documented)
- **Payments**: Stripe
- **Email**: SendGrid
- **SMS**: Twilio (optional)
- **Internationalization**: Backend-Frontend i18n coordination

### **Real-time Data Flow (Vapi → Frontend)**
- **WebSocket Connections**: Django Channels for live updates
- **Message Broadcasting**: Redis channel layers
- **Vapi Webhooks**: Instant appointment creation notifications
- **Frontend Updates**: Automatic calendar refresh without page reload
- **Notification System**: Real-time alerts for new voice bookings
- **Language Coordination**: Real-time language preference synchronization
- **Multilingual Notifications**: Language-aware real-time messaging

## 📂 Detailed File Structure

### **Frontend Structure**
```
frontend/
├── Dockerfile                       # Docker image configuration
├── .dockerignore                    # Docker ignore file
├── src/
│   ├── app/                         # App Router (Next.js 13+)
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   ├── page.tsx                 # Landing page
│   │   ├── (auth)/                  # Route groups
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   ├── register/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── dashboard/               # Authenticated user
│   │   │   ├── page.tsx             # Dashboard home
│   │   │   ├── calendar/
│   │   │   │   └── page.tsx
│   │   │   ├── services/
│   │   │   │   ├── page.tsx
│   │   │   │   └── new/
│   │   │   │       └── page.tsx
│   │   │   ├── appointments/
│   │   │   │   └── page.tsx
│   │   │   ├── settings/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── business/
│   │   │   │   ├── billing/
│   │   │   │   └── vapi/
│   │   │   └── layout.tsx
│   │   ├── [username]/              # Public pages
│   │   │   ├── page.tsx             # Business landing
│   │   │   ├── book/
│   │   │   │   └── page.tsx
│   │   │   └── services/
│   │   │       └── page.tsx
│   │   ├── pricing/
│   │   │   └── page.tsx
│   │   └── api/                     # API Routes
│   │       ├── auth/
│   │       └── webhooks/
│   ├── components/
│   │   ├── ui/                      # Shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── form.tsx
│   │   │   ├── calendar.tsx
│   │   │   └── ...
│   │   ├── layout/
│   │   │   ├── header.tsx
│   │   │   ├── sidebar.tsx
│   │   │   └── footer.tsx
│   │   ├── forms/
│   │   │   ├── auth/
│   │   │   ├── service/
│   │   │   └── appointment/
│   │   ├── booking/
│   │   │   ├── calendar-widget.tsx
│   │   │   ├── service-selector.tsx
│   │   │   └── booking-form.tsx
│   │   └── dashboard/
│   │       ├── stats-cards.tsx
│   │       ├── recent-appointments.tsx
│   │       └── calendar-view.tsx
│   ├── lib/
│   │   ├── api.ts                   # API client configuration
│   │   ├── auth.ts                  # NextAuth configuration
│   │   ├── utils.ts                 # Utility functions
│   │   ├── validations.ts           # Zod schemas
│   │   ├── constants.ts
│   │   ├── websocket.ts             # WebSocket client configuration
│   │   ├── i18n.ts                  # i18n configuration
│   │   └── types.ts
│   ├── hooks/
│   │   ├── use-api.ts
│   │   ├── use-auth.ts
│   │   ├── use-booking.ts
│   │   ├── use-translations.ts         # i18n hook
│   │   ├── use-language.ts             # Language management hook
│   │   └── use-real-time.ts           # WebSocket hook for real-time updates
│   ├── stores/                      # Zustand stores
│   │   ├── auth-store.ts
│   │   ├── booking-store.ts
│   │   ├── language-store.ts        # Language state management
│   │   └── business-store.ts
│   └── styles/
│       └── globals.css
├── public/
│   ├── locales/                     # Simple translation files
│   │   ├── es.json                  # All Spanish translations
│   │   └── en.json                  # All English translations
│   ├── images/
│   └── icons/
├── package.json
├── pnpm-lock.yaml                   # pnpm lock file
├── tailwind.config.js
├── next.config.js
├── tsconfig.json
├── .env.local
├── .eslintrc.json                   # ESLint configuration
├── .prettierrc                      # Prettier configuration
├── jest.config.js                   # Jest testing configuration
└── .dockerignore                    # Docker ignore file
```

### **Backend Structure**
```
backend/
├── Dockerfile                       # Docker image configuration
├── .dockerignore                    # Docker ignore file
├── core/                            # Main configuration
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                  # Base settings
│   │   ├── development.py           # Development
│   │   ├── production.py            # Production
│   │   └── testing.py               # Tests
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py                      # For WebSockets
│   ├── celery.py                    # Celery configuration
│   └── routing.py                   # WebSocket routing configuration
├── apps/
│   ├── __init__.py
│   ├── users/                       # User management
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── managers.py
│   │   └── migrations/
│   ├── businesses/                  # Business management
│   │   ├── models.py                # Business, BusinessHours, BusinessMember
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── onboarding_models.py     # BusinessDashboardConfig, BusinessOnboardingStatus
│   │   ├── onboarding_serializers.py
│   │   └── migrations/
│   ├── services/                    # Services per business
│   │   ├── models.py                # Service, ServiceCategory
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── appointments/                # Appointment system
│   │   ├── models.py                # Appointment
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── clients/                     # Client management
│   │   ├── models.py                # Client
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── payments/                    # Payment integration
│   │   ├── models.py                # Payment records
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── vapi_integration/            # VAPI integration system
│   │   ├── models.py                # VapiConfiguration, VapiCall, VapiCallTranscript, etc.
│   │   ├── serializers.py           # VapiWebhookSerializer, VapiConfigurationSerializer
│   │   ├── views.py                 # Webhook endpoints, configuration management
│   │   ├── urls.py
│   │   ├── multi_tenant_services.py # SharedAgentManager, TenantRegistrationService
│   │   ├── event_handlers.py        # EventHandlerRegistry, function call handlers
│   │   ├── domain_services.py       # AvailabilityQueryService, AppointmentBookingDomainService
│   │   ├── processors.py            # WebhookProcessor
│   │   ├── api_client.py            # VapiAPIClient, VapiBusinessService
│   │   ├── security.py              # WebhookSecurityManager
│   │   ├── value_objects.py         # Data classes and value objects
│   │   ├── tasks.py                 # Async processing tasks
│   │   └── migrations/
│   ├── notifications/               # Notification system
│   │   ├── models.py
│   │   ├── tasks.py                 # Notification tasks
│   │   ├── utils.py
│   │   └── migrations/
│   └── analytics/                   # Reports and metrics
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       └── migrations/
├── utils/
│   ├── __init__.py
│   ├── permissions.py               # Custom permissions
│   ├── pagination.py
│   ├── exceptions.py
│   └── validators.py
├── pyproject.toml                   # Poetry configuration
├── poetry.lock                      # Auto-generated lock file
├── static/
├── media/
├── locale/                          # Django translations
│   ├── es/
│   │   └── LC_MESSAGES/
│   │       ├── django.po
│   │       └── django.mo
│   ├── en/
│   │   └── LC_MESSAGES/
│   │       ├── django.po
│   │       └── django.mo
│   └── LINGUAS
├── manage.py
├── pytest.ini
├── .env.example
├── .flake8                          # Flake8 configuration
├── .coverage                        # Coverage configuration
└── .dockerignore                    # Docker ignore file
```

## 🌍 Internationalization (i18n) System Architecture

### **Overview**
VoiceAppoint implements a comprehensive internationalization system that coordinates between backend (Django) and frontend (Next.js) to provide a seamless multilingual experience. The system supports Spanish and English with the capability to easily add more languages.

### **Architecture Components**

#### **1. Backend Internationalization (Django)**

**Translation Management:**
- **Django i18n Framework**: Utilizing Django's built-in internationalization
- **Translation Files**: `.po` and `.mo` files for each language
- **Database Content**: Multilingual content stored in database models
- **API Localization**: All API responses include localized content

**Directory Structure:**
```
backend/
├── locale/
│   ├── es/LC_MESSAGES/          # Spanish translations
│   ├── en/LC_MESSAGES/          # English translations
│   └── LINGUAS                  # Supported languages
├── apps/
│   └── core/                    # Enhanced core app (no new app needed)
│       ├── mixins.py            # Reusable translation mixin
│       ├── middleware.py        # Language detection middleware  
│       ├── utils.py             # Translation utilities
│       └── management/commands/ # Translation management commands
```

**Database Schema - No Business Data Translation:**
```
Key Approach: Business data stays in native language (no translation fields needed)
- tenants: locale (single field for system context)
- services: name, description (business owner writes in their language)  
- notification_templates: system messages only (Django i18n)
- vapi_configurations: business content in native language, locale for context
```

**Backend Features:**
- **Language Context Middleware**: Simple tenant locale detection (no complex routing)
- **System Message Translation**: Only Django system messages (errors, notifications)
- **Localized API Responses**: Headers and system messages, business data as-is
- **Single Locale per Tenant**: Each business operates in one language naturally

#### **2. Frontend Internationalization (Next.js)**

**Next.js i18n Configuration:**
- **Built-in i18n routing**: Native Next.js internationalization support
- **Domain-based routing**: Optional language-specific domains
- **Automatic locale detection**: Browser and user preference detection

**Frontend Directory Structure:**
```
frontend/
├── public/locales/             # Simple JSON for UI only
│   ├── es.json                 # UI elements: buttons, navigation, messages  
│   └── en.json                 # UI elements: buttons, navigation, messages
├── src/lib/i18n.ts            # Minimal i18n setup (UI only)
├── src/hooks/use-language.ts   # Single language hook for UI
└── src/components/ui/language-switcher.tsx # For market-specific deployments
```

**Frontend Features:**
- **Next.js Built-in i18n**: Using native Next.js internationalization (no extra libraries needed)
- **Simple Language State**: Minimal Zustand store for language preference
- **Coordinated API Calls**: Reusing existing API client with Accept-Language header
- **Component Reusability**: Single language switcher component for entire app

#### **3. API Coordination Layer**

**Language State Management:**
- **Simple Store**: Single Zustand store for current language only
- **Backend Sync**: Language preference saved in existing user model (reusing `locale` field)
- **Tenant Languages**: Stored in existing tenant model (no new entities)
- **Minimal WebSocket Updates**: Reusing existing WebSocket infrastructure

**Request/Response Flow:**
- **Accept-Language Headers**: Automatic language detection from HTTP headers
- **User Authentication**: Language preferences from user profile
- **Tenant Context**: Business-specific language settings
- **Fallback Strategy**: Graceful degradation when translations are missing

#### **4. Vapi Integration with Multilingual Support**

**Enhanced Vapi Configuration:**
- **Single Assistant per Market**: One Vapi assistant per language market (es/en)
- **Natural Language Context**: Business content remains in native language
- **Locale-Aware Routing**: Simple tenant.locale parameter for system context
- **No Content Translation**: Business writes naturally, system adapts context only

**Multilingual Features:**
- **Language Parameter**: Single `language` parameter in existing API calls (no new endpoints)
- **Smart Fallback**: Default language when translation missing (simple logic)
- **Reuse Existing Functions**: Same booking functions with language context
- **Minimal Configuration**: Language settings in existing tenant configuration

#### **5. Real-time Language Synchronization**

**WebSocket Language Updates:**
- **Reuse Existing Channels**: Add language events to current WebSocket implementation
- **Minimal Payloads**: Only send language change events when needed
- **Existing Infrastructure**: No new WebSocket connections or channels needed

### **Implementation Roadmap**

#### **Phase 1: Minimal Backend Setup (Week 1)**
- Simple locale field in existing models (single VARCHAR column)
- System message translation (Django i18n for errors/notifications only)
- Business data remains in native language (no translation needed)
- Basic Spanish/English system messages

#### **Phase 2: Simple Frontend Integration (Week 2)**  
- Configure Next.js i18n for UI elements only
- Single language hook for interface translation
- Business data displayed as-is (no translation)
- Single JSON file per language market (UI only)

#### **Phase 3: Vapi Context Integration (Week 3)**
- Add locale context to existing Vapi functions (no new endpoints)
- Business content remains in native language
- Simple system context based on tenant.locale

#### **Phase 4: Testing & Deployment (Week 4)**
- Test existing functionality with locale context
- Deploy to specific markets (Spain = Spanish, UK = English)
- Basic documentation### **Key Features**

✅ **Simple & Maintainable**: No new tables, reusing existing infrastructure (KISS)  
✅ **DRY Implementation**: Single translation mixin, unified approach  
✅ **YAGNI Compliance**: Only essential features, no over-engineering  
✅ **Modular Design**: Reusable components across backend and frontend  
✅ **Zero Breaking Changes**: Additive approach to existing codebase  
✅ **Minimal Dependencies**: Using built-in framework features where possible  
✅ **Easy Migration Path**: Can evolve to more complex system if needed

---

> **Goal**: Deliver a complete starter boilerplate so the team can start building immediately

---

## 🤖 **VAPI INTEGRATION ARCHITECTURE**

> **📖 Complete Technical Documentation**: See [VAPI System Flows](../docs/VAPI_SYSTEM_FLOWS.md) for detailed implementation patterns, API flows, and database schemas.

### **Core Architecture Decision**

**Single Shared Agent Approach:**
- One VAPI agent serves ALL businesses
- Business identification through call metadata
- Dynamic routing based on business context
- Scalable and cost-effective solution

- `POST /api/v1/vapi_integration/webhook/` - Main webhook processor
- `GET /api/v1/vapi_integration/configs/` - Configuration management
- `GET /api/v1/vapi_integration/calls/` - Call history and analytics
- `POST /api/v1/vapi_integration/business/{id}/calls/outbound/` - Outbound calls

### **📚 Documentation References**

- **[VAPI System Flows](../docs/VAPI_SYSTEM_FLOWS.md)** - Complete technical flows and patterns
- **[VAPI Integration API](../docs/VAPI_INTEGRATION_API_DOC.md)** - Detailed API reference and examples

---

### **🔁 Single Phase: Complete Boilerplate (3-5 days)**

#### **Day 1: Base Structure and Docker**
1. **✅ Create full folder structure**
   - Frontend (Next.js)
   - Backend (Django) modular apps
   - Docker configuration
   - Nginx setup
   - Scripts and docs

2. **✅ Configure full Docker Compose**
   - PostgreSQL 15
   - Redis 7
   - Backend with Poetry
   - Frontend with Node.js
   - Nginx reverse proxy
   - Celery worker

3. **✅ Config files**
   - .env.example
   - .gitignore
   - docker-compose.yml
   - Optimized Dockerfiles

#### **Day 2: Backend Boilerplate Complete**
1. **✅ Django with Poetry setup**
   - pyproject.toml with dependencies
   - Modular settings (dev/prod/test)
   - Apps created (users, businesses, services, etc.)
   - DRF configured
   - JWT authentication

2. **✅ Base models implemented**
   - Custom User
   - Business
   - Service
   - Appointment
   - Initial migrations

3. **✅ URLs and API structure**
   - URL patterns
   - API versioning (/api/v1/)
   - CORS configured
   - Admin basic

#### **Day 3: Frontend Boilerplate Complete**
1. **✅ Full Next.js 14 setup**
   - TypeScript
   - TailwindCSS + Shadcn/ui
   - Folder structure
   - Base layout

2. **✅ Tooling configuration**
   - NextAuth.js
   - TanStack Query
   - Zustand basic stores
   - API client configured

3. **✅ Base components**
   - Shadcn/ui components installed
   - Layout (Header, Sidebar, Footer)
   - Basic form components
   - Loading and error states

#### **Day 4: Integration and Testing**
1. **✅ Frontend-Backend connectivity**
   - API client working
   - Basic auth flow
   - CORS configured
   - Environment variables

2. **✅ Docker integration**
   - Docker Compose up
   - Hot reload
   - Volumes
   - Networks

3. **✅ Testing setup**
   - Pytest (backend)
   - Jest (frontend)
   - Coverage reports
   - Basic CI/CD (GitHub Actions)

#### **Day 5: Documentation and Finalization**
1. **✅ Complete documentation**
   - README.md
   - API docs
   - Setup instructions
   - Development workflow

2. **✅ Development scripts**
   - Init scripts
   - Testing scripts
   - Deployment scripts
   - Makefile

3. **✅ Final validation**
   - Everything works with `docker-compose up`
   - Tests pass
   - Linting configured
   - Formatting configured

---

## **📦 Boilerplate Deliverables**

### **🎁 The team will receive:**

#### **🔧 Backend Ready-to-Develop:**
```bash
# Immediate usage:
cd backend
poetry install
poetry shell
poetry run python manage.py runserver

# Includes:
- ✅ Django 5.0 + DRF running
- ✅ PostgreSQL connected
- ✅ Redis running
- ✅ Apps created (users, businesses, services, appointments, payments, vapi_integration)
- ✅ Base models implemented
- ✅ JWT authentication configured
- ✅ Admin interface
- ✅ Testing setup
- ✅ Linting & formatting
```

#### **💻 Frontend Ready-to-Develop:**
```bash
# Immediate usage:
cd frontend
pnpm install
pnpm dev

# Includes:
- ✅ Next.js 14 + TypeScript running
- ✅ TailwindCSS + Shadcn/ui configured
- ✅ Base layout
- ✅ Basic auth pages
- ✅ Dashboard layout
- ✅ API client configured
- ✅ State management setup
- ✅ Form validation configured
- ✅ Testing setup
```

#### **🐳 Docker Environment:**
```bash
# One command:
docker-compose up

# Includes:
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Backend API at http://localhost:8000
- ✅ Frontend at http://localhost:3000
- ✅ Nginx reverse proxy
- ✅ Hot reload
- ✅ Volumes configured
- ✅ Environment variables
```

---

## **🗂️ Delivered Structure**

### **📁 Complete Project:**
```
voiced-booking-system/
├── 📋 README.md                     # Full setup
├── 🐳 docker-compose.yml            # Ready to use
├── 🐳 docker-compose.override.yml   # Dev override
├── 🐳 docker-compose.prod.yml       # Production
├── 🔧 Makefile                      # Useful commands
├── 📝 .env.example                  # Environment variables
├── 🚫 .gitignore                    # Configured
├── 🔄 .github/
│   └── workflows/
│       ├── backend-tests.yml        # Backend CI/CD
│       └── frontend-tests.yml       # Frontend CI/CD
├── 📚 docs/
│   ├── API.md                       # API documentation
│   ├── SETUP.md                     # Setup instructions
│   └── DEVELOPMENT.md               # Dev workflow
├── 🎨 frontend/                     # Full Next.js
│   └── 🐳 Dockerfile                # Frontend Docker image
├── ⚙️ backend/                      # Full Django
│   └── 🐳 Dockerfile                # Backend Docker image
├── 🌐 nginx/                        # Proxy configuration
│   ├── nginx.conf                   # Nginx config
│   └── ssl/                         # SSL certificates
└── 📜 scripts/                      # Useful scripts
    ├── setup.sh                     # Initial setup
    ├── deploy.sh                    # Deployment script
    └── backup.sh                    # Database backup
```

### **⚙️ Delivered Backend:**
```
backend/
├── ✅ Dockerfile
├── ✅ .dockerignore
├── ✅ pyproject.toml
├── ✅ poetry.lock
├── ✅ manage.py
├── ✅ pytest.ini
├── ✅ .env.example
├── ✅ .flake8
├── ✅ .coverage
├── ✅ core/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
└── ✅ apps/
    ├── users/
    ├── businesses/
    ├── services/
    ├── appointments/
    ├── payments/
    ├── vapi_integration/
    ├── notifications/
    └── analytics/
```

### **🎨 Delivered Frontend:**
```
frontend/
├── ✅ Dockerfile
├── ✅ .dockerignore
├── ✅ package.json
├── ✅ pnpm-lock.yaml
├── ✅ next.config.js
├── ✅ tailwind.config.js
├── ✅ tsconfig.json
├── ✅ .env.local.example
├── ✅ .eslintrc.json
├── ✅ .prettierrc
├── ✅ jest.config.js
└── ✅ src/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   ├── (auth)/
    │   ├── dashboard/
    │   ├── [username]/
    │   └── api/
    ├── components/
    │   ├── ui/
    │   ├── layout/
    │   ├── forms/
    │   └── dashboard/
    ├── lib/
    │   ├── api.ts
    │   ├── auth.ts
    │   └── utils.ts
    ├── hooks/
    ├── stores/
    └── types/
```

---

## **🔥 Quick Start Commands**

### **🚀 For the development team:**
```bash
# 1. Clone and initial setup
git clone <repo>
cd voiced-booking-system
cp .env.example .env

# 2. Start everything with Docker
docker-compose up

# 3. Database setup (another terminal)
docker-compose exec backend poetry run python manage.py migrate
docker-compose exec backend poetry run python manage.py createsuperuser

# 4. Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - Admin: http://localhost:8000/admin
```

### **🛠️ Local development (without Docker):**
```bash
# Backend
cd backend
poetry install
poetry shell
poetry run python manage.py runserver

# Frontend (new terminal)
cd frontend
pnpm install
pnpm dev
```

### **🛠️ Local development (alternative without Docker):**
```bash
# Backend
cd backend
poetry install
poetry shell
poetry run python manage.py runserver

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## **✅ Delivery Checklist**

- [ ] **Docker Compose working** with one command
- [ ] **Django Backend** with base models and basic APIs
- [ ] **Next.js Frontend** with layout and basic pages
- [ ] **PostgreSQL** configured
- [ ] **Redis** running for cache/sessions
- [ ] **JWT Authentication** configured
- [ ] **Testing** setup both sides
- [ ] **Linting & formatting** configured
- [ ] **CI/CD** basic GitHub Actions
- [ ] **Documentation** complete
- [ ] **Scripts** ready
- [ ] **Environment variables** documented

**🎯 Result: The team can begin feature development immediately without setup delay.**

## 📦 Main Dependencies

### **Frontend (package.json)**
```json
{
  "name": "voiceappoint-frontend",
  "version": "0.1.0",
  "private": true,
  "packageManager": "pnpm@8.10.0",
  "engines": {
    "node": ">=18.0.0",
    "pnpm": ">=8.0.0"
  },
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:ci": "jest --ci --coverage --watchAll=false",
    "type-check": "tsc --noEmit",
    "clean": "rm -rf .next node_modules",
    "analyze": "ANALYZE=true next build"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "tailwindcss": "^3.4.0",
    "@tailwindcss/forms": "^0.5.7",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "lucide-react": "^0.300.0",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-calendar": "^1.0.0",
    "react-hook-form": "^7.48.0",
    "@hookform/resolvers": "^3.3.0",
    "zod": "^3.22.0",
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.4.0",
    "next-auth": "^4.24.0",
    "date-fns": "^2.30.0",
    "recharts": "^2.8.0",
    "@stripe/stripe-js": "^2.4.0"
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "eslint-config-next": "^14.0.0",
    "prettier": "^3.0.0",
    "prettier-plugin-tailwindcss": "^0.5.0",
    "@types/jest": "^29.5.0",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^6.1.0",
    "@next/bundle-analyzer": "^14.0.0"
  }
}
```

### **Backend (pyproject.toml)**
```toml
[tool.poetry]
name = "voiceappoint-backend"
version = "0.1.0"
description = "VoiceAppoint Backend API - SaaS appointment booking system with phone agent"
authors = ["VoiceAppoint Team <dev@voiceappoint.com>"]
readme = "README.md"
packages = [{include = "core"}, {include = "apps"}]

[tool.poetry.dependencies]
python = "^3.11"
Django = "^5.0.1"
djangorestframework = "^3.14.0"
djangorestframework-simplejwt = "^5.3.0"
django-cors-headers = "^4.3.1"
django-filter = "^23.5"
drf-spectacular = "^0.27.0"
psycopg2-binary = "^2.9.9"
redis = "^5.0.1"
celery = "^5.3.4"
django-celery-beat = "^2.5.0"
django-channels = "^4.0.0"
channels-redis = "^4.1.0"
stripe = "^7.8.0"
python-decouple = "^3.8"
Pillow = "^10.1.0"
django-storages = "^1.14.2"
sendgrid = "^6.11.0"
twilio = "^8.12.0"
sentry-sdk = "^1.39.0"

[tool.poetry.group.dev.dependencies]
django-debug-toolbar = "^4.2.0"
django-extensions = "^3.2.3"
ipython = "^8.18.1"
pytest = "^7.4.3"
pytest-django = "^4.7.0"
factory-boy = "^3.3.0"
coverage = "^7.3.2"
black = "^23.11.0"
flake8 = "^6.1.0"
isort = "^5.12.0"
mypy = "^1.7.0"
django-stubs = "^4.2.7"

[tool.poetry.group.test.dependencies]
pytest-cov = "^4.1.0"
pytest-mock = "^3.12.0"
freezegun = "^1.2.2"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
  | migrations
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_django = "django"
known_first_party = ["core", "apps"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "DJANGO", "FIRSTPARTY", "LOCALFOLDER"]

[tool.mypy]
python_version = "3.11"
check_untyped_defs = true
ignore_missing_imports = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_unused_configs = true
plugins = ["mypy_django_plugin.main"]

[tool.django-stubs]
django_settings_module = "core.settings.development"

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "core.settings.testing"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
addopts = "--tb=short --strict-markers --disable-warnings"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]

[tool.coverage.run]
source = "."
omit = [
    "*/venv/*",
    "*/migrations/*",
    "manage.py",
    "*/settings/*",
    "*/tests/*",
    "*/__pycache__/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

## 🐳 Docker Configuration

### **docker-compose.yml**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: voiceappoint
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: poetry run python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=1
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/voiceappoint
      - REDIS_URL=redis://redis:6379/0
      - LANGUAGE_CODE=es
      - LANGUAGES=es,en
      - USE_I18N=True
      - USE_L10N=True

  frontend:
    build: ./frontend
    command: pnpm dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_DEFAULT_LOCALE=es
      - NEXT_PUBLIC_SUPPORTED_LOCALES=es,en

  celery:
    build: ./backend
    command: poetry run celery -A core worker -l info
    volumes:
      - ./backend:/app
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=1
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/voiceappoint
      - REDIS_URL=redis://redis:6379/0

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
```

## 🔄 Real-time Data Flow Implementation

### **Voice-to-Frontend Flow Sequence:**

```mermaid
sequenceDiagram
    participant User as 👤 Caller
    participant Vapi as 🎙️ Vapi Agent (Multilingual)
    participant Backend as ⚙️ Django API (i18n)
    participant WS as 📡 WebSocket (Language-aware)
    participant Frontend as 💻 Dashboard (Localized)

    User->>Vapi: "Book appointment for tomorrow 3pm" (ES/EN)
    Vapi->>Backend: POST /api/v1/vapi/book-appointment/ + language
    Backend->>Backend: Create appointment in DB with locale
    Backend->>WS: Broadcast appointment_created with language
    WS->>Frontend: Real-time update (localized)
    Frontend->>Frontend: Update calendar instantly in user's language
    Backend-->>Vapi: Success response (localized)
    Vapi-->>User: "Appointment confirmed!" (ES/EN)
```



### **Backend Dockerfile**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        postgresql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.7.1

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-root \
    && rm -rf $POETRY_CACHE_DIR

COPY . .

RUN mkdir -p static media

RUN poetry run python manage.py collectstatic --noinput --clear || true

RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### **Frontend Dockerfile**
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS base

FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
RUN npm install -g pnpm
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

FROM base AS builder
WORKDIR /app
RUN npm install -g pnpm
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED 1
RUN pnpm build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
RUN mkdir .next
RUN chown nextjs:nodejs .next
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"
CMD ["node", "server.js"]
```

### **Nginx Configuration**
```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /admin/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            proxy_pass http://backend;
        }

        location /media/ {
            proxy_pass http://backend;
        }
    }
}
```

### **Development vs Production Dockerfiles**

#### **Backend Development Override (docker-compose.override.yml)**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: >
      sh -c "poetry run python manage.py migrate --noinput &&
             poetry run python manage.py runserver 0.0.0.0:8000"
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=1
      - DJANGO_SETTINGS_MODULE=core.settings.development

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: deps
    command: pnpm dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
```

#### **Production Docker Compose (docker-compose.prod.yml)**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: >
      sh -c "poetry run python manage.py migrate --noinput &&
             poetry run python manage.py collectstatic --noinput &&
             poetry run gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3"
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=0
      - DJANGO_SETTINGS_MODULE=core.settings.production
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: runner
    environment:
      - NODE_ENV=production
    restart: unless-stopped

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: poetry run celery -A core worker -l info
    depends_on:
      - db
      - redis
    environment:
      - DJANGO_SETTINGS_MODULE=core.settings.production
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

## 🔐 Environment Variables

### **Backend (.env)**
```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Internationalization
LANGUAGE_CODE=es
LANGUAGES=es,en
USE_I18N=True
USE_L10N=True
TIME_ZONE=Europe/Madrid

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/voiceappoint

# Redis
REDIS_URL=redis://localhost:6379/0

# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Vapi
VAPI_API_KEY=your-vapi-key
VAPI_WEBHOOK_SECRET=your-webhook-secret

# Email
SENDGRID_API_KEY=your-sendgrid-key
FROM_EMAIL=noreply@voiceappoint.com

# Cloud Storage (Production)
# Configure based on chosen provider (Azure, Google Cloud, etc.)
CLOUD_STORAGE_ACCESS_KEY=your-storage-key
CLOUD_STORAGE_SECRET_KEY=your-storage-secret
CLOUD_STORAGE_BUCKET_NAME=voiceappoint-media

# Sentry
SENTRY_DSN=your-sentry-dsn
```

### **Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_DEFAULT_LOCALE=es
NEXT_PUBLIC_SUPPORTED_LOCALES=es,en
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```

## 📋 Next Steps

1. **Create folder structure**
2. **Configure Docker Compose**
3. **Set up Django with Poetry**
4. **Create data models**
5. **Set up Next.js with TypeScript**
6. **Implement authentication**
7. **Develop core APIs**
8. **Integrate with Vapi**
9. **Stripe payment system**
10. **Deploy and testing**

## 🔧 Useful Poetry Commands

### **Development Commands:**
```bash
poetry install
poetry shell
poetry run python manage.py runserver
poetry run python manage.py migrate
poetry run python manage.py makemigrations
poetry run pytest
poetry run black .
poetry run isort .
poetry run flake8
# i18n commands
poetry run python manage.py makemessages -l es
poetry run python manage.py makemessages -l en
poetry run python manage.py compilemessages
poetry run python manage.py update_translations
poetry run python manage.py export_translations
poetry add django-extensions
poetry add --group dev pytest-mock
poetry update
poetry show
```

### **🔧 Useful Docker Commands**
```bash
docker-compose up
docker-compose up -d
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose up --build backend
docker-compose up --build frontend
docker-compose exec backend poetry run python manage.py migrate
docker-compose exec backend poetry run python manage.py createsuperuser
docker-compose exec backend poetry run python manage.py shell
docker-compose down -v
docker system prune -a
docker-compose -f docker-compose.prod.yml up -d
```

### **🧩 Useful pnpm Commands (Frontend)**
```bash
pnpm install
pnpm dev
pnpm build
pnpm start
pnpm test
pnpm test:watch
pnpm lint
pnpm lint:fix
pnpm format
pnpm add react-query
pnpm add -D @types/node
pnpm add -g typescript
pnpm update
pnpm list
pnpm outdated
pnpm remove lodash
pnpm clean
pnpm install
pnpm run custom-script
pnpm info
pnpm audit
pnpm audit --fix
```

### **⚙️ pnpm Configuration (.npmrc)**
```ini
shamefully-hoist=false
public-hoist-pattern[]=*eslint*
public-hoist-pattern[]=*prettier*
strict-peer-dependencies=true
auto-install-peers=true
store-dir=~/.pnpm-store
cache-dir=~/.pnpm-cache
network-timeout=60000
fetch-retries=3
fetch-retry-mintimeout=10000
fetch-retry-maxtimeout=60000
prefer-frozen-lockfile=true
save-exact=true
link-workspace-packages=true
prefer-workspace-packages=true
```

### **🔧 Modern Development Scripts**
```bash
pnpm setup:dev
pnpm dev:full
pnpm build:prod
pnpm preview
pnpm test:full
pnpm qa
pnpm analyze
pnpm clean:all
```

### **📁 Complete Delivered Docker Structure:**
```
voiced-booking-system/
├── docker-compose.yml              # Development
├── docker-compose.override.yml     # Dev override
├── docker-compose.prod.yml         # Production
├── backend/
│   └── Dockerfile                  # Backend image
├── frontend/
│   └── Dockerfile                  # Frontend image
└── nginx/
    ├── nginx.conf                  # Base configuration
    └── ssl/                        # SSL certificates (prod)
```

---
