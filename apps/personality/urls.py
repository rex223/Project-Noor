"""
URL configuration for personality app.
"""
from django.urls import path
from . import views

app_name = 'personality'

urlpatterns = [
    # Assessment views
    path('assessment/', views.PersonalityAssessmentView.as_view(), name='assessment'),
    path('dashboard/', views.PersonalityDashboardView.as_view(), name='dashboard'),
    
    # API endpoints
    path('api/assessment/', views.PersonalityAssessmentAPIView.as_view(), name='api_assessment'),
    path('api/insights/', views.PersonalityInsightsAPIView.as_view(), name='api_insights'),
    path('api/game-data/', views.PersonalityGameDataView.as_view(), name='api_game_data'),
]
