from django.urls import path

from .views import OfferDetailView, OfferListView, OfferDetailItemView


urlpatterns = [
    path("offers/", OfferListView.as_view(), name="offer-list"),
    path("offers/<int:pk>/", OfferDetailView.as_view(), name="offer-detail"),
    path("offerdetails/<int:pk>/", OfferDetailItemView.as_view(), name="offer-detail-item"),
]