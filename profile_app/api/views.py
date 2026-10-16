from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profile_app.models import UserProfile

from .permissions import IsProfileOwnerOrReadOnly
from .serializers import (
    BusinessProfileSerializer,
    CustomerProfileSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
)

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve profiles and allow owners to update their own profile."""

    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    lookup_field = 'user_id'
    lookup_url_kwarg = 'pk'
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_serializer_class(self):
        """Select the serializer based on the request method."""
        if self.request.method == 'PATCH':
            return ProfileUpdateSerializer

        return ProfileSerializer


class BusinessProfileListView(generics.ListAPIView):
    """Return all business user profiles."""

    queryset = UserProfile.objects.filter(
        type='business'
    ).select_related('user')

    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]


class CustomerProfileListView(generics.ListAPIView):
    """Return all customer user profiles."""

    queryset = UserProfile.objects.filter(
        type='customer'
    ).select_related('user')

    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]