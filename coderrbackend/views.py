from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Profile
from .serializers import (
    UserSerializer, 
)

@api_view(['POST'])
@permission_classes([AllowAny])
def registration_view(request):
    """
    Register a new user (customer or business).

    Creates a User and Profile, and returns an authentication token.
    """
    serializer = UserSerializer(data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    repeated_password = request.data.get('repeated_password')
    user_type = request.data.get('type', 'customer')

    if password != repeated_password:
        return Response(
            {"error": "Passwords do not match."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create user
    user = User.objects.create_user(username=username, email=email, password=password)
    # Create profile
    Profile.objects.create(user=user, type=user_type)

    # Create token
    token, _ = Token.objects.get_or_create(user=user)

    response_data = {
        "token": token.key,
        "username": user.username,
        "email": user.email,
        "user_id": user.id,
    }
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticate a user and return a token.

    Uses username and password from request body.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        response_data = {
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response(
            {"error": "Invalid credentials."},
            status=status.HTTP_400_BAD_REQUEST
        )