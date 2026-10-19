
from django.db.models import Min
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from offers_app.models import Offer
from .filters import OfferFilters
from .pagination import OfferPagination
from .serializers import OfferListSerializer


class OfferListView(generics.ListAPIView):
    """Return a filtered and paginated offer list."""

    serializer_class = OfferListSerializer
    permission_classes = [AllowAny]
    pagination_class = OfferPagination

    def get_queryset(self):
        queryset = Offer.objects.select_related("user")
        queryset = queryset.prefetch_related("details")
        queryset = queryset.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min(
                "details__delivery_time_in_days"
            )
        )
        return OfferFilters(self.request.query_params).apply(queryset)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        ordering = self.request.query_params.get(
            "ordering", "-created_at"
        )
        return queryset.order_by(ordering, "-id")
