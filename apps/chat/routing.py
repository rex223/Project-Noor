"""
WebSocket routing for The Last Neuron chat system.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<session_id>[0-9a-f-]{36})/$', consumers.ChatConsumer.as_asgi()),
]
