from django.db import models
from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from auth_app.permissions import IsBusinessUser, IsOwnerOrReadOnly
from .models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferWriteSerializer, OfferDetailSerializer
from .pagination import OfferPagination


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Offer model.

    Supports listing, creating, retrieving, updating, and deleting offers.
    Business users can create offers; owners can update/delete.
    """
    queryset = Offer.objects.all()
    pagination_class = OfferPagination

    def get_serializer_class(self):
        """
        Use the writable serializer for create/update, the read serializer otherwise.
        """
        if self.action in ('create', 'update', 'partial_update'):
            return OfferWriteSerializer
        return OfferSerializer

    def get_permissions(self):
        """
        Listing is public; creation requires a business user; everything
        else (retrieve/update/destroy) requires authentication, with
        modification restricted to the offer's owner.
        """
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsBusinessUser()]
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]

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
        if ordering == 'updated_at':
            queryset = queryset.order_by('updated_at')
        elif ordering == 'min_price':
            queryset = queryset.annotate(min_price=models.Min('details__price')).order_by('min_price')

        return queryset.distinct()

    def perform_create(self, serializer):
        """
        Set the offer's user to the authenticated user.
        """
        serializer.save(user=self.request.user)


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """
    Retrieve a single OfferDetail (pricing tier) by ID.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
