from rest_framework import serializers

from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serialize and validate reviews."""

    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'reviewer',
            'created_at',
            'updated_at',
        ]

    def validate_rating(self, value):
        """Ensure rating is between 1 and 5."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError(
                'Rating must be between 1 and 5.'
            )
        return value

    def validate_business_user(self, value):
        """Ensure the reviewed user has a business profile."""
        if not hasattr(value, 'profile') or value.profile.type != 'business':
            raise serializers.ValidationError(
                'User must have a business profile.'
            )
        return value


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Allow updating only rating and description."""

    class Meta:
        model = Review
        fields = ['rating', 'description']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError(
                'Rating must be between 1 and 5.'
            )
        return value