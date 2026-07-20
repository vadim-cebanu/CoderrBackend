from django.db import models
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from auth_app.permissions import IsBusinessUser, IsOwnerOrReadOnly
from .models import Offer
from .serializer import OfferSerializer


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Offer model.

    Supports listing, creating, retrieving, updating, and deleting offers.
    Business users can create offers; owners can update/delete.
    """
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated, IsBusinessUser | IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Optionally filter by creator_id, min_price, max_delivery_time, etc.
        """
        queryset = self.queryset
        creator_id = self.request.query_params.get('creator_id')
        min_price = self.request.query_params.get('min_price')
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        search = self.request.query_params.get('search')
        ordering = self.request.query_params.get('ordering')

        if creator_id:
            queryset = queryset.filter(user_id=creator_id)
        if min_price:
            queryset = queryset.filter(details__price__gte=min_price)
        if max_delivery_time:
            queryset = queryset.filter(details__delivery_time_in_days__lte=max_delivery_time)
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search)
            )
        if ordering in ['updated_at', 'min_price']:
            queryset = queryset.order_by(ordering)

        return queryset.distinct()

    def perform_create(self, serializer):
        """
        Set the offer's user to the authenticated user.
        """
        serializer.save(user=self.request.user)