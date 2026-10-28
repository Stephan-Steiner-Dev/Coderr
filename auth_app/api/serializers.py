"""Serializers for registration and login data."""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from rest_framework import serializers

from profile_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration data and create a user with a profile."""

    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=['customer', 'business'],
        write_only=True
    )

    class Meta:
        """Define the user model and registration fields."""

        model = User
        fields = [
            'username',
            'email',
            'password',
            'repeated_password',
            'type'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        """Validate the password using Django's password validators."""
        try:
            validate_password(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages) from error

        return value

    def validate(self, attrs):
        """Ensure that the password and repeated password match."""
        password = attrs.get('password')
        repeated_password = attrs.get('repeated_password')

        if password != repeated_password:
            raise serializers.ValidationError({
                'repeated_password': 'Passwords do not match.'
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create a user and its profile within a database transaction."""
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')

        user = User.objects.create_user(**validated_data)

        UserProfile.objects.create(
            user=user,
            type=user_type
        )

        return user


class LoginSerializer(serializers.Serializer):
    """Validate user credentials for authentication."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the user using their username and password."""
        user = authenticate(
            username=attrs['username'],
            password=attrs['password']
        )
        if user is None:
            raise serializers.ValidationError(
                'Invalid username or password.'
            )
        attrs['user'] = user
        return attrs
