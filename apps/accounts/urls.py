"""
URL configuration for accounts app.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # URLs temporarily commented out until views are implemented
    # path('register/', views.RegisterView.as_view(), name='register'),
    # path('login/', views.LoginView.as_view(), name='login'),
    # path('logout/', views.LogoutView.as_view(), name='logout'),
    # path('profile/', views.ProfileView.as_view(), name='profile'),
    # path('onboarding/', views.OnboardingView.as_view(), name='onboarding'),
]
