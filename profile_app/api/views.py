from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profile_app.models import UserProfile

from .serializers import ProfileSerializer


class ProfileDetailView(generics.RetrieveAPIView):
    """Retrieve a user profile by its associated user ID."""

    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_id'
    lookup_url_kwarg = 'pk'
    