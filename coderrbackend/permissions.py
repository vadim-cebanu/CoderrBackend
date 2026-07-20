from rest_framework import permissions


class IsBusinessUser(permissions.BasePermission):
    """
    Permission to allow only business users.
    """
    def has_permission(self, request, view):
        profile = getattr(request.user, 'profile', None)
        return profile and profile.type == 'business'


class IsCustomerUser(permissions.BasePermission):
    """
    Permission to allow only customer users.
    """
    def has_permission(self, request, view):
        profile = getattr(request.user, 'profile', None)
        return profile and profile.type == 'customer'


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to allow only the owner to modify an object.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsReviewer(permissions.BasePermission):
    """
    Permission to allow only the reviewer to modify a review.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.reviewer == request.user