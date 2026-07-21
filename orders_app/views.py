from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Order
from .serializers import OrderSerializer
from .permissions import IsBusinessUserOrCustomer
from auth_app.permissions import IsBusinessUser, IsCustomerUser
from django.contrib.auth.models import User


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Order model.

    Customers can create orders; business users can update status;
    admins can delete orders.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsBusinessUserOrCustomer]
    pagination_class = None

    def get_queryset(self):
        """
        Users see orders where they are either customer or business user.
        """
        user = self.request.user
        return self.queryset.filter(Q(customer_user=user) | Q(business_user=user))

    def create(self, request, *args, **kwargs):
        """
        Create an order from an OfferDetail ID.

        Only customer users can create orders.
        """
        if not IsCustomerUser().has_permission(request, self):
            return Response(
                {"error": "Only customer users can create orders."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Update order status (PATCH).

        Only business users can update status.
        """
        if not IsBusinessUser().has_permission(request, self):
            return Response(
                {"error": "Only business users can update order status."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete an order.

        Only admin (staff) users can delete orders.
        """
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin users can delete orders."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


def _get_business_user_or_none(business_user_id):
    """
    Return the User only if it exists AND has a business profile.
    Returns None otherwise (caller responds with 404).
    """
    try:
        user = User.objects.get(id=business_user_id)
    except User.DoesNotExist:
        return None

    profile = getattr(user, 'profile', None)
    if not profile or profile.type != 'business':
        return None

    return user


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_count_view(request, business_user_id):
    """
    Return the number of in-progress orders for a business user.
    404 if no business user with this ID exists.
    """
    business_user = _get_business_user_or_none(business_user_id)
    if business_user is None:
        return Response(
            {"detail": "Business user not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    count = Order.objects.filter(
        business_user_id=business_user_id, status="in_progress"
    ).count()
    return Response({"order_count": count})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def completed_order_count_view(request, business_user_id):
    """
    Return the number of completed orders for a business user.
    404 if no business user with this ID exists.
    """
    business_user = _get_business_user_or_none(business_user_id)
    if business_user is None:
        return Response(
            {"detail": "Business user not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    count = Order.objects.filter(
        business_user_id=business_user_id, status="completed"
    ).count()
    return Response({"completed_order_count": count})