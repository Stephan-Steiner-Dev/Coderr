"""URL routes for the profile API."""
from django.urls import path

from .views import (
    BusinessProfileListView,
    CustomerProfileListView,
    ProfileDetailView,
    BaseInfoView
)


urlpatterns = [
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessProfileListView.as_view(), name='business-profile-list'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='customer-profile-list'),
    path('base-info/', BaseInfoView.as_view(), name='base-info')
]