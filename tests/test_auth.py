"""Authentication and user registration test suite."""

from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class TestAuthentication(APITestCase):
    """Test cases for user authentication, registration, and login functionality.
    
    This test class covers:
    - User registration with validation
    - User login with credentials
    - Token authentication
    - Profile creation during registration
    """
   
    def setUp(self):
        """Set up test data before each test method.
        
        Creates a test user with customer profile for authentication tests.
        """
        
        self.user= User.objects.create_user(
            username='customer1',
            email='customer1@example.com',
            password='test123asd'
        )
        
        if hasattr(self.user, 'profile'):
            self.user.profile.type = 'customer'
            self.user.profile.save()

    def test_registration_success(self):
        """Test successful user registration with valid data.
        
        Validates that:
        - User can register with valid username, email, and matching passwords
        - Response returns status code 201 (Created)
        - Authentication token is included in response
        - User data (username, email, user_id) is returned correctly
        - User profile is created with correct type
        
        Endpoint: POST /api/registration/
        """
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'test123asd',
            'repeated_password': 'test123asd',
            'type': 'customer'
        }
        response = self.client.post('/api/registration/', data, format='json')
        assert response.status_code == 201
        assert 'token' in response.data
        assert response.data['username'] == 'newuser'
        assert response.data['email'] == 'newuser@example.com'
        assert response.data['user_id'] is not None

        user = User.objects.get(username='newuser')
        assert user.profile.type == 'customer'

    def test_registration_passwords_mismatch(self):
        """Test registration failure when passwords don't match.
        
        Validates that:
        - Registration fails when password and repeated_password don't match
        - Response returns status code 400 (Bad Request)
        - Error message is included in response
        
        Endpoint: POST /api/registration/
        """
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'test123asd',
            'repeated_password': 'wrongpass',
            'type': 'customer'
        }
        response = self.client.post('/api/registration/', data, format='json')
        assert response.status_code == 400
        assert 'error' in response.data

    def test_login_success(self):
        """Test successful user login with valid credentials.
        
        Validates that:
        - User can login with correct username and password
        - Response returns status code 200 (OK)
        - Authentication token is included in response
        - Username is returned in response data
        
        Endpoint: POST /api/login/
        """
        data = {
            'username': 'customer1',
            'password': 'test123asd'
        }
        response = self.client.post('/api/login/', data, format='json')
        assert response.status_code == 200
        assert 'token' in response.data
        assert response.data['username'] == 'customer1'

    def test_login_invalid_credentials(self):
        """Test login failure with invalid credentials.
        
        Validates that:
        - Login fails with non-existent username or wrong password
        - Response returns status code 400 (Bad Request)
        - Error message is included in response
        
        Endpoint: POST /api/login/
        """
        data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        response = self.client.post('/api/login/', data, format='json')
        assert response.status_code == 400
        assert 'error' in response.data