from rest_framework import serializers
from .models import Order
from offers_app.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order.

    Handles creation of orders from OfferDetail IDs and status updates.
    """
    offer_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=OfferDetail.objects.all(), source='offer_detail', write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'offer_detail_id',
            'title', 'revisions', 'delivery_time_in_days', 'price',
            'features', 'offer_type', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer_user', 'business_user', 'title',
            'revisions', 'delivery_time_in_days', 'price',
            'features', 'offer_type', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        """
        Create an order from an OfferDetail ID.

        The customer_user is the authenticated user.
        The business_user and order details are taken from the OfferDetail.
        """
        offer_detail = validated_data['offer_detail']
        customer_user = self.context['request'].user

        order = Order.objects.create(
            customer_user=customer_user,
            business_user=offer_detail.offer.user,
            offer_detail=offer_detail,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status='in_progress',
        )
        return order