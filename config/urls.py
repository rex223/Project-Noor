"""
URL configuration for The Last Neuron project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.main.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('apps.accounts.urls')),
    path('chat/', include('apps.chat.urls')),
    path('games/', include('apps.games.urls')),
    path('personality/', include('apps.personality.urls')),
    path('api/', include('apps.api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
