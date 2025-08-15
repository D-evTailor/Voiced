"""
Testing settings for VoiceAppoint project.

This module contains settings specific to running tests.
Optimized for speed and reliability during test execution.
"""

from .base import *

# Debug and testing
DEBUG = False
TESTING = True

# Test database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 60,
        }
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Password hashers for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Cache configuration for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Celery settings for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

# Media files for testing
MEDIA_ROOT = BASE_DIR / 'test_media'

# Static files for testing
STATIC_ROOT = BASE_DIR / 'test_static'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Security settings for testing
SECRET_KEY = 'test-secret-key-not-for-production'
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Logging configuration for testing
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['null'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Channels configuration for testing
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# JWT settings for testing
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=2),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
})

# External services for testing
STRIPE_PUBLISHABLE_KEY = 'pk_test_testing'
STRIPE_SECRET_KEY = 'sk_test_testing'
STRIPE_WEBHOOK_SECRET = 'whsec_test_testing'

VAPI_API_KEY = 'test_vapi_key'
VAPI_WEBHOOK_SECRET = 'test_vapi_webhook_secret'

TWILIO_ACCOUNT_SID = 'test_twilio_sid'
TWILIO_AUTH_TOKEN = 'test_twilio_token'
TWILIO_PHONE_NUMBER = '+15551234567'

SENDGRID_API_KEY = 'test_sendgrid_key'

# Disable Sentry for testing
SENTRY_DSN = ''

# File upload settings for testing
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024  # 1MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024  # 1MB

# API rate limiting disabled for testing
RATELIMIT_ENABLE = False

# Performance settings for testing
USE_ETAGS = False

# Timezone for testing
TIME_ZONE = 'UTC'
USE_TZ = True

# CORS settings for testing
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# REST Framework settings for testing
REST_FRAMEWORK.update({
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
})

# Pytest configuration
PYTEST_TIMEOUT = 300  # 5 minutes per test
