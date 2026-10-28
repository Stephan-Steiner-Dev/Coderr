"""Pagination settings for the offer list API."""
from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """Set pagination limits for offer-list responses."""
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100