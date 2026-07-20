from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django's built-in User model.

    Used in registration and login responses.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.

    Ensures that string fields are never null; they return empty strings.
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    type = serializers.ChoiceField(choices=Profile.USER_TYPES)

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'email', 'type',
            'first_name', 'last_name', 'file', 'location', 'tel',
            'description', 'working_hours', 'created_at'
        ]
        read_only_fields = ['user', 'username', 'email', 'created_at']

    def to_representation(self, instance):
        """
        Ensure string fields are never null in the response.
        """
        data = super().to_representation(instance)
        for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
            data[field] = data.get(field, '')
        return data