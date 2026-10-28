"""URL routes for the authentication API."""
from django.urls import path

from .views import LoginView, RegistrationView


# URL patterns for user registration and authentication.
urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
]
