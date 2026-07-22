from rest_framework import serializers
from .models import OfferDetail, Offer
from auth_app.models import Profile


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for OfferDetail model.

    Represents a single pricing tier (basic/standard/premium) of an offer.
    Used both for the standalone /api/offerdetails/{id}/ endpoint and as the
    writable nested representation when creating/updating an Offer.
    """
    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type'
        ]


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """
    Minimal {id, url} representation of an OfferDetail.

    Used when an Offer is read (list/retrieve) so clients follow the link
    to /api/offerdetails/{id}/ instead of receiving the full nested object.
    """
    url = serializers.HyperlinkedIdentityField(view_name='offerdetail-detail')

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']


class OfferSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for Offer model (list/retrieve).

    Links (not full objects) to each OfferDetail, plus computed fields
    (min_price, min_delivery_time) and a summary of the creator's profile.
    """

    details = OfferDetailLinkSerializer(many=True, read_only=True)
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

    def get_min_price(self, obj):
        """
        Return the lowest price among the offer's details, or 0 if none exist.
        """
        details = obj.details.all()
        return min(detail.price for detail in details) if details else 0

    def get_min_delivery_time(self, obj):
        """
        Return the shortest delivery time among the offer's details, or 0 if none exist.
        """
        details = obj.details.all()
        return min(detail.delivery_time_in_days for detail in details) if details else 0

    def get_user_details(self, obj):
        """
        Return a summary (first name, last name, username) of the offer's creator.
        """
        profile = Profile.objects.filter(user=obj.user).first()
        if profile:
            return {
                'first_name': profile.user.first_name or '',
                'last_name': profile.user.last_name or '',
                'username': obj.user.username,
            }
        return {}


class OfferWriteSerializer(serializers.ModelSerializer):
    """
    Writable serializer for Offer model (create/update).

    On create, exactly 3 details (one per offer_type) are required. On
    (partial) update, only the details being changed need to be sent,
    matched to existing rows by offer_type.
    """

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def validate_details(self, value):
        """
        Ensure details have unique offer_types; require exactly 3 on creation.
        """
        required_fields = {'title', 'revisions',
                           'delivery_time_in_days', 'price', 'offer_type'}
        for detail in value:
            missing = required_fields - set(detail.keys())
            if missing:
                raise serializers.ValidationError(
                    f"Each detail must include: {', '.join(sorted(missing))}."
                )

        offer_types = [detail['offer_type'] for detail in value]
        if len(set(offer_types)) != len(offer_types):
            raise serializers.ValidationError(
                "Each detail must have a unique offer_type.")
        if self.instance is None and len(value) != 3:
            raise serializers.ValidationError(
                "An offer must have exactly 3 details.")
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
