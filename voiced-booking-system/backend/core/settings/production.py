"""
Production settings for VoiceAppoint project.

This module contains settings specific to production environment.
Security, performance, and monitoring configurations.
"""

from .base import *

# Security settings for production
DEBUG = False

# Security headers and HTTPS
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', default=True, cast=bool)
SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session security
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
SESSION_COOKIE_HTTPONLY = config('SESSION_COOKIE_HTTPONLY', default=True, cast=bool)
SESSION_COOKIE_SAMESITE = config('SESSION_COOKIE_SAMESITE', default='Lax')
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=1209600, cast=int)  # 2 weeks

# CSRF protection
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_HTTPONLY = config('CSRF_COOKIE_HTTPONLY', default=True, cast=bool)
CSRF_COOKIE_SAMESITE = config('CSRF_COOKIE_SAMESITE', default='Lax')

# Database configuration for production
if config('DATABASE_URL', default=None):
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(config('DATABASE_URL'))
    DATABASES['default']['CONN_MAX_AGE'] = config('DB_CONN_MAX_AGE', default=600, cast=int)
    DATABASES['default']['OPTIONS'] = {
        'sslmode': config('DB_SSLMODE', default='require'),
    }

# Cache configuration for production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': config('REDIS_MAX_CONNECTIONS', default=50, cast=int),
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': config('CACHE_KEY_PREFIX', default='voiceappoint'),
        'TIMEOUT': config('CACHE_TIMEOUT', default=3600, cast=int),  # 1 hour
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Email configuration for production
if SENDGRID_API_KEY:
    EMAIL_BACKEND = 'sendgrid.django.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST', default='localhost')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Static and Media files for production
if config('USE_CLOUD_STORAGE', default=False, cast=bool):
    # Cloud storage configuration (can be customized for different providers)
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticS3Boto3Storage'
    
    AWS_ACCESS_KEY_ID = config('CLOUD_STORAGE_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = config('CLOUD_STORAGE_SECRET_KEY')
    AWS_STORAGE_BUCKET_NAME = config('CLOUD_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('CLOUD_STORAGE_REGION', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = config('CLOUD_STORAGE_CUSTOM_DOMAIN', default=None)
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_STATIC_LOCATION = 'static'
    AWS_MEDIA_LOCATION = 'media'
    
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN or f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"}/{AWS_STATIC_LOCATION}/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN or f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"}/{AWS_MEDIA_LOCATION}/'

# CORS settings for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGIN_REGEXES = config(
    'CORS_ALLOWED_ORIGIN_REGEXES',
    default='',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
)

# Celery settings for production
CELERY_TASK_ALWAYS_EAGER = False
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': config('CELERY_VISIBILITY_TIMEOUT', default=3600, cast=int),
}
CELERY_WORKER_PREFETCH_MULTIPLIER = config('CELERY_WORKER_PREFETCH_MULTIPLIER', default=1, cast=int)
CELERY_TASK_ACKS_LATE = config('CELERY_TASK_ACKS_LATE', default=True, cast=bool)
CELERY_WORKER_MAX_TASKS_PER_CHILD = config('CELERY_WORKER_MAX_TASKS_PER_CHILD', default=1000, cast=int)

# Logging configuration for production
LOGGING['handlers']['file']['filename'] = config('DJANGO_LOG_FILE', default='/var/log/django/django.log')
LOGGING['loggers']['django']['level'] = config('DJANGO_LOG_LEVEL', default='WARNING')
LOGGING['loggers']['apps']['level'] = config('APPS_LOG_LEVEL', default='INFO')

# Performance settings
X_FRAME_OPTIONS = 'DENY'
USE_ETAGS = config('USE_ETAGS', default=True, cast=bool)

# JWT settings for production
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=30, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=1, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
})

# Rate limiting (if using django-ratelimit)
RATELIMIT_ENABLE = config('RATELIMIT_ENABLE', default=True, cast=bool)

# Monitoring and health checks
HEALTH_CHECK = {
    'DISK_USAGE_MAX': config('HEALTH_CHECK_DISK_USAGE_MAX', default=90, cast=int),  # percentage
    'MEMORY_MIN': config('HEALTH_CHECK_MEMORY_MIN', default=100, cast=int),  # MB
}

# Application performance monitoring
if config('APM_SERVICE_NAME', default=None):
    INSTALLED_APPS += ['elasticapm.contrib.django']
    ELASTIC_APM = {
        'SERVICE_NAME': config('APM_SERVICE_NAME'),
        'SECRET_TOKEN': config('APM_SECRET_TOKEN', default=''),
        'SERVER_URL': config('APM_SERVER_URL', default='http://localhost:8200'),
        'ENVIRONMENT': config('APM_ENVIRONMENT', default='production'),
    }
    MIDDLEWARE = ['elasticapm.contrib.django.middleware.TracingMiddleware'] + MIDDLEWARE

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = config('FILE_UPLOAD_MAX_MEMORY_SIZE', default=5242880, cast=int)  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = config('DATA_UPLOAD_MAX_MEMORY_SIZE', default=5242880, cast=int)  # 5MB
