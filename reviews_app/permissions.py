from rest_framework import permissions


class IsReviewer(permissions.BasePermission):
    """
    Permission to allow only the reviewer to modify a review.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.reviewer == request.user