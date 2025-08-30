"""
ASGI config for The Last Neuron project.

It exposes the ASGI callable as a module-level variable named ``application``.
This supports both HTTP and WebSocket protocols.
"""

import os
from django.core.asgi import get_asgi_application
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
from django.core.asgi import get_asgi_application

# Use only the default Django ASGI application for HTTP
application = get_asgi_application()
