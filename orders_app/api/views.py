"""API views for order listing, updates, and counts."""
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed

from offers_app.models import OfferDetail
from orders_app.models import Order
from .permissions import IsCustomerOrReadOnly, IsOrderBusinessOrStaff
from .serializers import OrderCreateSerializer, OrderSerializer, OrderStatusSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    """List user orders and create orders from offer details."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomerOrReadOnly]

    def get_queryset(self):
        """Return orders associated with the current user."""
        user = self.request.user
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        )

    def get_serializer_class(self):
        """Select the serializer based on the request method."""
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        """Validate input and return the created order."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        detail = get_object_or_404(
            OfferDetail, pk=serializer.validated_data["offer_detail_id"]
        )
        order = self.create_order(request.user, detail)
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def create_order(customer, detail):
        """Copy offer details into a new order."""
        return Order.objects.create(
            customer_user=customer,
            business_user=detail.offer.user,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features.copy(),
            offer_type=detail.offer_type,
        )


class OrderDetailView(generics.GenericAPIView):
    """Update order status or delete an order."""

    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializer
    permission_classes = [IsAuthenticated, IsOrderBusinessOrStaff]

    def patch(self, request, *args, **kwargs):
        """Update the status of an assigned order."""
        order = self.get_object()
        serializer = self.get_serializer(
            order, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)

    def delete(self, request, *args, **kwargs):
        """Delete an order as a staff user."""
        order = self.get_object()
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        """Disallow full order updates."""
        raise MethodNotAllowed("PUT")


class BaseOrderCountView(APIView):
    """Count orders of a specific business user."""

    permission_classes = [IsAuthenticated]
    order_status = None
    response_key = None

    def get(self, request, business_user_id):
        """Return the number of matching orders."""
        user_model = get_user_model()
        business_user = get_object_or_404(
            user_model,
            pk=business_user_id,
            profile__type="business"
        )
        count = Order.objects.filter(
            business_user=business_user,
            status=self.order_status
        ).count()
        return Response({self.response_key: count})


class OrderCountView(BaseOrderCountView):
    """Count orders currently in progress."""

    order_status = "in_progress"
    response_key = "order_count"


class CompletedOrderCountView(BaseOrderCountView):
    """Count completed orders."""

    order_status = "completed"
    response_key = "completed_order_count"