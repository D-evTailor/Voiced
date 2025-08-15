# VoiceAppoint VAPI System Flows & Architecture

## System Overview

VoiceAppoint implements a multi-tenant SaaS platform where a single VAPI agent serves multiple businesses through metadata-based routing. The system handles user registration, business creation, and appointment booking via voice interactions.

## Core Architecture Principles

- **Single Shared Agent**: One VAPI agent serves all businesses
- **Metadata Routing**: Business identification through call metadata
- **Multi-Tenant Database**: Flexible schema supporting any business type
- **Modular API Design**: Reusable endpoints across business contexts

## VAPI Agent Architecture

### Shared Agent Manager

```python
class SharedAgentManager:
    def create_call_with_metadata(self, business_slug: str, phone_number: str) -> VapiCall
    def get_business_context(self, business_slug: str) -> dict
    def extract_business_from_metadata(self, webhook_data: dict) -> str
```

### Event Handling System

```python
class EventHandlerRegistry:
    def process_vapi_webhook(self, webhook_data: dict) -> dict
    def route_to_business_handler(self, business_slug: str, event_data: dict) -> dict
```

### Function Call Handlers

| Function | Purpose | Parameters |
|----------|---------|------------|
| `get_business_services` | Retrieve available services | `business_slug` |
| `check_service_availability` | Check time slot availability | `business_slug, service_id, datetime` |
| `book_appointment` | Create appointment booking | `business_slug, service_id, datetime, client_data` |
| `get_business_hours` | Retrieve business operating hours | `business_slug, date_range` |

## User Registration Flow

### Single Registration Endpoint

**Endpoint**: `POST /api/v1/auth/register/`

**Process**:
1. Validate user data + business data
2. Create User instance
3. Create Business instance with auto-generated slug
4. Create BusinessMember relationship (owner role)
5. Initialize BusinessDashboardConfig
6. Initialize BusinessOnboardingStatus

**Response Data**:
```json
{
  "user": { "id": 1, "email": "user@example.com" },
  "business_slug": "auto-generated-slug",
  "business_name": "Business Name"
}
```

## Database Schema Design

### Business Model

```python
class Business:
    owner = ForeignKey(User)
    name = CharField(max_length=200)
    slug = SlugField(unique=True)
    business_type = CharField(choices=BUSINESS_TYPE_CHOICES)
    locale = CharField(choices=LANGUAGE_CHOICES)
    timezone = CharField(max_length=50)
    currency = CharField(choices=CURRENCY_CHOICES)
    allow_voice_booking = BooleanField(default=True)
```

### Service Model

```python
class Service:
    business = ForeignKey(Business)
    category = ForeignKey(ServiceCategory, null=True)
    name = CharField(max_length=200)
    duration = PositiveIntegerField()
    price = DecimalField(max_digits=10, decimal_places=2)
    voice_booking_enabled = BooleanField(default=True)
```

### Appointment Model

```python
class Appointment:
    business = ForeignKey(Business)
    service = ForeignKey(Service)
    client = ForeignKey(Client)
    provider = ForeignKey(User)
    start_time = DateTimeField()
    status = CharField(choices=STATUS_CHOICES)
```

## API Endpoints Structure

### Authentication & User Management
- `POST /api/v1/auth/register/` - User + Business registration
- `POST /api/v1/auth/token/` - JWT token authentication
- `GET /api/v1/auth/me/` - Current user profile

### Business Management
- `GET /api/v1/businesses/` - List user businesses
- `POST /api/v1/businesses/` - Create additional business
- `GET /api/v1/businesses/{id}/` - Business details
- `PATCH /api/v1/businesses/{id}/` - Update business

### Service Management
- `GET /api/v1/services/?business={id}` - List business services
- `POST /api/v1/services/` - Create service
- `PATCH /api/v1/services/{id}/` - Update service

### Appointment Management
- `GET /api/v1/appointments/?business={id}` - List appointments
- `POST /api/v1/appointments/` - Create appointment
- `GET /api/v1/appointments/availability/` - Check availability

### VAPI Integration
- `POST /api/v1/vapi/webhook/` - VAPI webhook processor
- `GET /api/v1/vapi/calls/?business={id}` - List VAPI calls
- `GET /api/v1/vapi/transcripts/{call_id}/` - Call transcript

## Frontend Routing Architecture

### Public Routes
- `/` - Landing page with registration form
- `/[username]` - Public business page
- `/[username]/book` - Public booking interface

### Authentication Routes
- `/login` - User login
- `/register` - User + business registration

### Dashboard Routes
- `/dashboard/select` - Business selection (multi-business users)
- `/dashboard/[username]` - Business dashboard
- `/dashboard/[username]/services` - Service management
- `/dashboard/[username]/appointments` - Appointment management
- `/dashboard/[username]/settings` - Business settings

## VAPI Call Flow

### 1. Call Initiation
```
Client calls business number → VAPI Agent → Extract business_slug from metadata
```

### 2. Business Context Loading
```
SharedAgentManager.get_business_context(business_slug) → Load business data + services
```

### 3. Service Discovery
```
VAPI Agent calls get_business_services(business_slug) → Return available services
```

### 4. Availability Check
```
VAPI Agent calls check_service_availability(business_slug, service_id, datetime)
```

### 5. Appointment Booking
```
VAPI Agent calls book_appointment(business_slug, service_id, datetime, client_data)
```

### 6. Confirmation
```
Return appointment confirmation → VAPI Agent confirms with client
```

## Data Flow Patterns

### Registration Pattern
```
User Input → Validation → User Creation → Business Creation → Member Assignment → Response
```

### Booking Pattern
```
VAPI Webhook → Business Extraction → Function Call Routing → Database Operation → Response
```

### Multi-Tenant Query Pattern
```
Request → Business Context → Filtered Query → Business-Scoped Results
```

## Security & Authentication

### JWT Token Flow
1. User login with email/password
2. Server validates credentials
3. JWT token issued with user + business context
4. Frontend stores token
5. API requests include Authorization header

### Business Access Control
- Users can only access businesses where they are members
- Role-based permissions (owner, admin, manager, staff, viewer)
- Business-scoped queries prevent cross-tenant data access

### VAPI Security
- Webhook signature validation
- Business slug validation against database
- Rate limiting on function calls

## Performance Optimizations

### Database Optimizations
- Indexed fields: business_slug, user_id, service_id
- Select_related for business queries
- Prefetch_related for service lists

### Caching Strategy
- Business context caching (Redis)
- Service availability caching
- User session caching

### Query Optimization
- Business-scoped managers
- Bulk operations for appointments
- Optimized serializers with minimal fields

## Error Handling

### VAPI Function Call Errors
- Business not found → Return "Business unavailable"
- Service not available → Return alternative suggestions
- Booking conflict → Return alternative time slots

### API Error Responses
- Standardized error format across all endpoints
- Business context errors
- Validation error details

### Frontend Error Handling
- Network error fallbacks
- Business selection validation
- Form validation with real-time feedback

## Monitoring & Analytics

### VAPI Call Metrics
- Call duration tracking
- Success/failure rates per business
- Popular services identification

### Business Analytics
- Appointment conversion rates
- Revenue tracking per business
- Service performance metrics

### System Health Monitoring
- API response times
- Database query performance
- VAPI webhook processing times
