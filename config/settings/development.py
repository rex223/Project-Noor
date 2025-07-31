"""
Development settings for The Last Neuron project.
"""

from .base import *

# Development specific settings
DEBUG = True

# Use SQLite for development if PostgreSQL is not available
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Simpler password validation for development
AUTH_PASSWORD_VALIDATORS = []

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable security features in development
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Cache (use local memory for development)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Development logging
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['root']['level'] = 'DEBUG'

# Django Debug Toolbar (if installed)
if 'debug_toolbar' in INSTALLED_APPS:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
