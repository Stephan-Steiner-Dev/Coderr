from rest_framework.permissions import BasePermission


class IsCustomerOrReadOnly(BasePermission):
    """Allow authenticated users to read and customers to create."""

    def has_permission(self, request, view):
        if request.method == "GET":
            return True

        return (
            hasattr(request.user, "profile")
            and request.user.profile.type == "customer"
        )


class IsOrderBusinessOrStaff(BasePermission):
    """Allow assigned business users to update and staff to delete."""

    def has_permission(self, request, view):
        if request.method == "DELETE":
            return request.user.is_staff

        return (
            hasattr(request.user, "profile")
            and request.user.profile.type == "business"
        )

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return request.user.is_staff

        return obj.business_user == request.user