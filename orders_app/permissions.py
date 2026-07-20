from rest_framework import permissions
from auth_app.permissions import IsBusinessUser, IsCustomerUser


class IsBusinessUserOrCustomer(permissions.BasePermission):
    """
    Permission to allow only business or customer users to view orders.
    """
    def has_permission(self, request, view):
        return IsBusinessUser().has_permission(request, view) or \
               IsCustomerUser().has_permission(request, view)