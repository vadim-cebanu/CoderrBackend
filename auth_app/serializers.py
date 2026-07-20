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
    user = serializers.PrimaryKeyRelatedField(read_only=True, source='user.id')
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True, allow_null=True)
    type = serializers.ChoiceField(choices=Profile.USER_TYPES)

    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'email', 'type',
            'first_name', 'last_name', 'file', 'location', 'tel',
            'description', 'working_hours', 'created_at'
        ]
        read_only_fields = ['user', 'username', 'email', 'created_at']
        
    def update(self, instance, validated_data):
       
        user_data = validated_data.pop('user',None)
        
        user_instance = instance.user

        if 'first_name' in user_data:
            user_instance.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user_instance.last_name = user_data['last_name']
        
        if 'first_name' in user_data or 'last_name' in user_data:
            user_instance.save()

        return super().update(instance, validated_data)


    def to_representation(self, instance):
        """
        Ensure string fields are never null in the response.
        """
        data = super().to_representation(instance)
        fields_to_check = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        
        for field in fields_to_check:
            if data.get(field) is None:
                data[field] = ''
        return data