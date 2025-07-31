"""
URL configuration for chat app.
"""
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat, name='chat'),
    path('api/', views.chat_api, name='chat_api'),
]
