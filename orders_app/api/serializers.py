from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serialize order details."""

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.ModelSerializer):
    """Validate the offer detail for a new order."""

    offer_detail_id = serializers.IntegerField(min_value=1)

    class Meta:
        model = Order
        fields = ["offer_detail_id"]


class OrderStatusSerializer(serializers.ModelSerializer):
    """Validate order status updates."""

    class Meta:
        model = Order
        fields = ["status"]

    def validate(self, attrs):
        """Reject fields other than status."""
        extra_fields = set(self.initial_data) - {"status"}
        if extra_fields:
            raise serializers.ValidationError(
                "Only the status field can be updated."
            )
        return attrs
    