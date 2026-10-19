from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db.models import Min

from offers_app.models import Offer, OfferDetail


class OfferUserSerializer(serializers.ModelSerializer):
    """Serialize basic information about an offer creator."""

    class Meta:
        model = get_user_model()
        fields = [
            "first_name",
            "last_name",
            "username",
        ]
        read_only_fields = fields


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Serialize links to offer details."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/"



class OfferListSerializer(serializers.ModelSerializer):
    """Serialize offers for the offer list endpoint."""

    details = OfferDetailLinkSerializer(
        many=True, read_only=True
    )
    user_details = OfferUserSerializer(
        source="user", read_only=True
    )
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False
    )
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]
