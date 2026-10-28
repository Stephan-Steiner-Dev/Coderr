from rest_framework.permissions import BasePermission


class IsReviewOwner(BasePermission):
    """Allow only the review creator to modify or delete it."""

    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user


class IsCustomer(BasePermission):
    """Allow only users with a customer profile."""

    def has_permission(self, request, view):
        return (
            hasattr(request.user, 'profile')
            and request.user.profile.type == 'customer'
        )