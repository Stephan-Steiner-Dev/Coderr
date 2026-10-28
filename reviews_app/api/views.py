from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from reviews_app.models import Review
from .serializers import ReviewSerializer, ReviewUpdateSerializer
from .permissions import IsCustomer, IsReviewOwner


class ReviewListCreateView(generics.ListCreateAPIView):
    """List reviews and allow customers to create reviews."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['updated_at', 'rating']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomer()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Review.objects.all()

        for field in ['business_user_id', 'reviewer_id']:
            value = self.request.query_params.get(field)

            if value is not None:
                if not value.isdecimal() or int(value) == 0:
                    raise ValidationError({
                        field: 'Must be a valid positive integer.'
                    })

                queryset = queryset.filter(**{field: int(value)})

        return queryset

    def perform_create(self, serializer):
        business_user = serializer.validated_data['business_user']

        if Review.objects.filter(
            business_user=business_user,
            reviewer=self.request.user
        ).exists():
            raise PermissionDenied(
                'You have already reviewed this business user.'
            )

        serializer.save(reviewer=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Allow review owners to update or delete their reviews."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewOwner]
    http_method_names = ['patch', 'delete', 'options', 'head']

    def get_serializer_class(self):
        return ReviewUpdateSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = ReviewUpdateSerializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(ReviewSerializer(instance).data)