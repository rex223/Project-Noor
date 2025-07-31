"""
URL configuration for games app.
"""
from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('personality-quest/', views.personality_quest, name='personality_quest'),
    path('mood-dungeon/', views.mood_dungeon, name='mood_dungeon'),
    path('social-arena/', views.social_arena, name='social_arena'),
    path('stress-survival/', views.stress_survival, name='stress_survival'),
    path('mindfulness-mystery/', views.mindfulness_mystery, name='mindfulness_mystery'),
    path('emotion-explorer/', views.emotion_explorer, name='emotion_explorer'),
]
