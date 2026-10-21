from django.db.models import Min
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from offers_app.models import Offer
from .filters import OfferFilters
from .pagination import OfferPagination
from .permissions import IsBusinessUser, IsOfferOwner
from .serializers import (
    OfferListSerializer,
    OfferCreateSerializer,
    OfferRetrieveSerializer,
    OfferUpdateSerializer,
)


class OfferListView(generics.ListCreateAPIView):
    """List offers and allow business users to create offers."""

    pagination_class = OfferPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OfferCreateSerializer
        return OfferListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsBusinessUser()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = Offer.objects.select_related("user")
        queryset = queryset.prefetch_related("details")
        queryset = queryset.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days")
        )
        return OfferFilters(self.request.query_params).apply(queryset)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        ordering = self.request.query_params.get(
            "ordering", "-created_at"
        )
        return queryset.order_by(ordering, "-id")


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a single offer."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Offer.objects.select_related("user").prefetch_related(
            "details"
        ).annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days")
        )

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return OfferUpdateSerializer
        return OfferRetrieveSerializer

    def get_object(self):
        offer = super().get_object()
        if self.request.method in ("PATCH", "PUT", "DELETE"):
            if not IsOfferOwner().has_object_permission(
                self.request, self, offer
            ):
                raise PermissionDenied(
                    "Only the offer owner can modify this offer."
                )
        return offer