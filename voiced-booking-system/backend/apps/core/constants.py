from django.utils.translation import gettext_lazy as _

DEFAULT_PAGINATION_SIZE = 20
MAX_PAGINATION_SIZE = 100

APPOINTMENT_DURATION_LIMITS = {
    'min': 5,
    'max': 480,
}

BUSINESS_HOURS_LIMITS = {
    'earliest': 6,
    'latest': 23,
}

RATE_LIMIT_CONFIG = {
    'email_attempts': 5,
    'ip_attempts': 10,
    'window_minutes': 15,
}

CACHE_TIMEOUTS = {
    'default': 300,
    'short': 60,
    'medium': 600,
    'long': 3600,
}

USER_AGENT_MAX_LENGTH = 500
PHONE_MAX_LENGTH = 17
SLUG_MAX_LENGTH = 50

SERVICE_TYPES = {
    'personal': _('Personal Service'),
    'group': _('Group Service'),
    'consultation': _('Consultation'),
}

NOTIFICATION_TYPES = {
    'email': _('Email'),
    'sms': _('SMS'),
    'push': _('Push Notification'),
}

STATUS_TRANSITIONS = {
    'appointment': {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['in_progress', 'cancelled', 'no_show'],
        'in_progress': ['completed', 'cancelled'],
        'completed': [],
        'cancelled': [],
        'no_show': [],
    }
}
