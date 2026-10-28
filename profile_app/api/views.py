"""API views for user profiles and platform statistics."""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from reviews_app.models import Review
from offers_app.models import Offer
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


class BaseInfoView(APIView):
    """Return general platform statistics."""

    permission_classes = [AllowAny]

    def get(self, request):
        """Return review, business-profile, and offer statistics."""
        review_stats = Review.objects.aggregate(
            average_rating=Avg('rating')
        )
        data = {
            'review_count': Review.objects.count(),
            'average_rating': round(review_stats['average_rating'] or 0, 1),
            'business_profile_count': UserProfile.objects.filter(
                type='business'
            ).count(),
            'offer_count': Offer.objects.count(),
        }
        return Response(data)