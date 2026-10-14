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