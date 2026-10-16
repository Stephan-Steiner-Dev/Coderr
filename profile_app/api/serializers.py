from django.db import transaction
from rest_framework import serializers

from profile_app.models import UserProfile


class ProfileSerializer(serializers.ModelSerializer):
    """Serialize user profile details."""

    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(
        source='user.username', read_only=True
    )
    first_name = serializers.CharField(
        source='user.first_name', read_only=True
    )
    last_name = serializers.CharField(
        source='user.last_name', read_only=True
    )
    email = serializers.EmailField(
        source='user.email', read_only=True
    )

    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
        ]
        read_only_fields = fields


class ProfileUpdateSerializer(ProfileSerializer):
    """Validate and update editable user profile information."""

    first_name = serializers.CharField(
        source='user.first_name', required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        source='user.last_name', required=False, allow_blank=True
    )
    email = serializers.EmailField(
        source='user.email', required=False
    )

    class Meta(ProfileSerializer.Meta):
        read_only_fields = [
            'user',
            'username',
            'type',
            'created_at',
        ]

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        for field, value in user_data.items():
            setattr(instance.user, field, value)

        instance.user.save()

        return super().update(instance, validated_data)


class BusinessProfileSerializer(ProfileSerializer):
    """Serialize public business profile information."""

    class Meta(ProfileSerializer.Meta):
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
        ]


class CustomerProfileSerializer(ProfileSerializer):
    """Serialize public customer profile information."""

    class Meta(ProfileSerializer.Meta):
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'uploaded_at',
            'type',
        ]