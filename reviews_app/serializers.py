from rest_framework import serializers
from .models import Review
from auth_app.models import Profile


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review.

    Ensures a customer can only review a business user once.
    Only rating and description are editable.
    """
    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Ensure the reviewer is a customer and hasn't reviewed this business before.
        """
        request = self.context.get('request')
        business_user = data.get('business_user')
        reviewer = request.user

        # Check if reviewer is a customer
        profile = Profile.objects.filter(user=reviewer, type='customer').first()
        if not profile:
            raise serializers.ValidationError("Only customer users can create reviews.")

        # Check for existing review
        if Review.objects.filter(business_user=business_user, reviewer=reviewer).exists():
            raise serializers.ValidationError(
                "You have already reviewed this business user."
            )

        return data

    def create(self, validated_data):
        """
        Set the reviewer to the authenticated user.
        """
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)