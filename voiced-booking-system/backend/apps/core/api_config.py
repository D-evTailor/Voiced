"""
API endpoints configuration following RESTful conventions and best practices.

URL Structure:
- /api/v1/{resource}/ - Collection endpoints
- /api/v1/{resource}/{id}/ - Resource endpoints  
- /api/v1/{resource}/{id}/{action}/ - Action endpoints

Best Practices Applied:
1. Clear Names: Consistent collection URLs without redundant prefixes
2. Idempotency: POST operations check Idempotency-Key header
3. Paging: All list endpoints support pagination with page/page_size
4. Order and Filters: Standard search, ordering, and filtering
5. Cross-referencing: Separate endpoints instead of deep nesting
6. Rate Limiting: Applied via middleware and DRF throttling
7. Versioning: v1 prefix for all endpoints
8. Security: JWT + API key authentication, business context validation
"""

API_ENDPOINTS = {
    'auth': {
        'base': '/api/v1/auth/',
        'endpoints': [
            'token/',           # POST: Get JWT token
            'token/refresh/',   # POST: Refresh JWT token  
            'token/verify/',    # POST: Verify JWT token
            'register/',        # POST: User registration
            'me/',             # GET/PATCH: Current user info
            'change-password/', # POST: Change password
            'users/',          # GET/POST/PUT/DELETE: User management
        ]
    },
    'businesses': {
        'base': '/api/v1/businesses/',
        'endpoints': [
            '',                # GET/POST: Business list/create
            '{id}/',          # GET/PUT/PATCH/DELETE: Business detail
            '{id}/add-member/', # POST: Add business member
            'hours/',         # GET/POST/PUT/DELETE: Business hours
            'members/',       # GET/POST/PUT/DELETE: Business members
        ]
    },
    'services': {
        'base': '/api/v1/services/',
        'endpoints': [
            '',               # GET/POST: Service list/create
            '{id}/',         # GET/PUT/PATCH/DELETE: Service detail
            '{id}/toggle-active/', # PATCH: Toggle service active status
            'public/',       # GET: Public services for booking
            'categories/',   # GET/POST/PUT/DELETE: Service categories
            'providers/',    # GET/POST/PUT/DELETE: Service providers
        ]
    },
    'appointments': {
        'base': '/api/v1/appointments/',
        'endpoints': [
            '',               # GET/POST: Appointment list/create
            '{id}/',         # GET/PUT/PATCH/DELETE: Appointment detail
            '{id}/confirm/',  # PATCH: Confirm appointment
            '{id}/cancel/',   # PATCH: Cancel appointment
            '{id}/complete/', # PATCH: Complete appointment
            'today/',        # GET: Today's appointments
            'upcoming/',     # GET: Upcoming appointments
            'availability/', # GET: Check availability
        ]
    },
    'clients': {
        'base': '/api/v1/clients/',
        'endpoints': [
            '',              # GET/POST: Client list/create
            '{id}/',        # GET/PUT/PATCH/DELETE: Client detail
        ]
    },
    'payments': {
        'base': '/api/v1/payments/',
        'endpoints': [
            '',              # GET/POST: Payment list/create
            '{id}/',        # GET: Payment detail
        ]
    },
    'notifications': {
        'base': '/api/v1/notifications/',
        'endpoints': [
            '',              # GET: Notification list
            '{id}/',        # GET/PATCH: Notification detail
        ]
    },
    'analytics': {
        'base': '/api/v1/analytics/',
        'endpoints': [
            '',              # GET: Analytics dashboard
        ]
    },
    'resources': {
        'base': '/api/v1/resources/',
        'endpoints': [
            '',              # GET/POST: Resource list/create
            '{id}/',        # GET/PUT/PATCH/DELETE: Resource detail
        ]
    },
    'vapi': {
        'base': '/api/v1/vapi/',
        'endpoints': [
            'webhook/',      # POST: VAPI webhook handler
        ]
    }
}

# Standard query parameters for all endpoints
STANDARD_QUERY_PARAMS = [
    'page',          # Page number for pagination
    'page_size',     # Items per page
    'search',        # Text search
    'ordering',      # Field to order by (prefix with - for desc)
    'date_from',     # Filter from date
    'date_to',       # Filter to date
]

# Standard headers
STANDARD_HEADERS = [
    'Authorization',    # Bearer {token} or API-Key {key}
    'X-Business-ID',   # Business context
    'X-API-Key',       # API key authentication
    'Idempotency-Key', # For idempotent operations
    'Content-Type',    # application/json
    'Accept',          # application/json
]
