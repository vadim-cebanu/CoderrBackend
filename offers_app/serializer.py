from rest_framework import serializers
from .models import OfferDetail, Offer
from auth_app.models import Profile

class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for OfferDetail model.

    Represents a single pricing tier (basic/standard/premium) of an offer.
    """
    class Meta:
        model = OfferDetail
        fields= [
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type'
        ]


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for Offer model.

    Nests all three OfferDetail tiers and exposes computed fields
    (min_price, min_delivery_time) plus a summary of the creator's profile.
    """

    details = OfferDetailSerializer(many=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        
    def get_min_price(self,obj):
        """
        Return the lowest price among the offer's details, or 0 if none exist.
        """
        details = obj.details.all()
        return min(detail.price for detail in details) if details else 0

    def get_min_delivery_time(self,obj):
        """
        Return the shortest delivery time among the offer's details, or 0 if none exist.
        """
        details=obj.details.all()
        return min(detail.delivery_time_in_days for detail in details) if details else 0

    def get_user_details(self, obj):
        """
        Return a summary (first name, last name, username) of the offer's creator.
        """
        profile = Profile.objects.filter(user=obj.user).first()
        if profile:
            return {
                'first_name': profile.first_name or '',
                'last_name': profile.last_name or '',
                'username': obj.user.username,
            }
        return {}

    def validate_details(self, value):
        """
        Ensure an offer has exactly 3 details, one per unique offer_type.
        """
        if len(value) != 3:
            raise serializers.ValidationError("An offer must have exactly 3 details.")
        offer_types = [detail['offer_type'] for detail in value]
        if len(set(offer_types)) != 3:
            raise serializers.ValidationError("Each detail must have a unique offer_type.")
        return value

    def create(self, validated_data):
        """
        Create an Offer along with its nested OfferDetail records.
        """
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        """
        Update an Offer's fields and, for any detail whose offer_type matches
        an existing one, update that detail in place.
        """
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data:
            for detail_data in details_data:
                offer_type = detail_data['offer_type']
                detail = instance.details.filter(offer_type=offer_type).first()
                if detail:
                    for attr, value in detail_data.items():
                        setattr(detail, attr, value)
                    detail.save()
        return instance
