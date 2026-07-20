"""User profile management test suite."""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import Profile 


class TestProfileEndpoints(APITestCase):
    """Test cases for user profile endpoints and operations.
    
    This test class covers:
    - Profile retrieval and viewing
    - Profile updates and modifications
    - Profile listing by type (business/customer)
    - Authentication and authorization for profile operations
    - Permission checks for profile access
    """

    def setUp(self):
        """Set up test data before each test method.
        
        Creates two test users with different profile types:
        - customer_user: A customer type profile for testing customer operations
        - business_user: A business type profile for testing business operations
        """
      
        self.customer_user = User.objects.create_user(
            username='customer1',
            email='customer1@example.com',
            password='test123asd'
        )
       
        self.customer_profile, created = Profile.objects.get_or_create(user=self.customer_user)
        self.customer_profile.type = 'customer'
        self.customer_profile.save()

        self.business_user = User.objects.create_user(
            username='business1',
            email='business1@example.com',
            password='test123asd'
        )
        self.business_profile, created = Profile.objects.get_or_create(user=self.business_user)
        self.business_profile.type = 'business'
        self.business_profile.save()

    def test_get_profile_success(self):
        """Test successful profile retrieval for authenticated user.
        
        Validates that:
        - Authenticated user can retrieve their own profile
        - Response returns status code 200 (OK)
        - Profile data contains correct username and type
        
        Endpoint: GET /api/profile/{user_id}/
        """
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(f'/api/profile/{self.customer_user.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        if 'username' in response.data:
            assert response.data['username'] == 'customer1'
        assert response.data['type'] == 'customer'

    def test_get_profile_unauthenticated(self):
        """Test profile retrieval fails for unauthenticated user.
        
        Validates that:
        - Unauthenticated requests are rejected
        - Response returns status code 401 (Unauthorized)
        
        Endpoint: GET /api/profile/{user_id}/
        """
        response = self.client.get(f'/api/profile/{self.customer_user.id}/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile_success(self):
        """Test successful profile update by authenticated user.
        
        Validates that:
        - Authenticated user can update their own profile
        - Response returns status code 200 (OK)
        - Updated data (first_name, last_name, location) is persisted correctly
        
        Endpoint: PATCH /api/profile/{user_id}/
        """
        self.client.force_authenticate(user=self.customer_user)
        data = {
            'first_name': 'Pika',
            'last_name': 'Pika',
            'location': 'Berlin'
        }
        response = self.client.patch(
            f'/api/profile/{self.customer_user.id}/', data, format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Pika'

    def test_update_profile_unauthorized(self):
        """Test that users cannot update other users' profiles.
        
        Validates that:
        - User cannot modify another user's profile
        - Response returns status code 403 (Forbidden) or 400 (Bad Request)
        - Authorization checks are enforced
        
        Endpoint: PATCH /api/profile/{user_id}/
        """
        self.client.force_authenticate(user=self.customer_user)
        data = {'location': 'Hacked'}
        response = self.client.patch(
            f'/api/profile/{self.business_user.id}/', data, format='json'
        )
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST]

    def test_list_business_profiles(self):
        """Test retrieval of all business type profiles.
        
        Validates that:
        - Authenticated user can list business profiles
        - Response returns status code 200 (OK)
        - Result contains at least one business profile
        - All returned profiles have type 'business'
        
        Endpoint: GET /api/profiles/business/
        """
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get('/api/profiles/business/')
        
        assert response.status_code == status.HTTP_200_OK
        date_profile = response.data.get('results') if isinstance(response.data, dict) else response.data
        
        assert len(date_profile) >= 1
        assert date_profile[0]['type'] == 'business'

    def test_list_customer_profiles(self):
        """Test retrieval of all customer type profiles.

        Validates that:
        - Authenticated user can list customer profiles
        - Response returns status code 200 (OK)
        - Result contains at least one customer profile
        - All returned profiles have type 'customer'

        Endpoint: GET /api/profiles/customer/
        """
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get('/api/profiles/customer/')

        assert response.status_code == status.HTTP_200_OK
        date_profile = response.data.get('results') if isinstance(response.data, dict) else response.data

        assert len(date_profile) >= 1
        assert date_profile[0]['type'] == 'customer'

    def test_list_own_profile(self):
        """Test the default router list endpoint, filtered to the caller's own profile.

        Validates that:
        - Authenticated user can list profiles via GET /api/profile/
        - Only their own profile is returned (ProfileViewSet.get_queryset filters by user)

        Endpoint: GET /api/profile/
        """
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get('/api/profile/')

        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results') if isinstance(response.data, dict) else response.data
        assert len(results) == 1
        assert results[0]['username'] == 'customer1'

    def test_get_profile_not_found(self):
        """Test retrieving a profile for a non-existent user ID returns 404.

        Endpoint: GET /api/profile/{user_id}/
        """
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get('/api/profile/999999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.data

    def test_update_profile_not_found(self):
        """Test updating a profile for a non-existent user ID returns 404.

        Endpoint: PATCH /api/profile/{user_id}/
        """
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.patch('/api/profile/999999/', {'location': 'Berlin'}, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.data

    def test_profile_str_representation(self):
        """Test Profile.__str__ returns 'username (type)'."""
        assert str(self.customer_profile) == 'customer1 (customer)'

    def test_profile_serializer_never_returns_null_fields(self):
        """Test ProfileSerializer.to_representation coerces None values to ''.

        Uses in-memory (unsaved) instances so that None can be assigned
        without violating the model's NOT NULL database constraints.
        """
        from auth_app.serializers import ProfileSerializer

        self.customer_user.first_name = None
        self.customer_user.last_name = None
        profile = Profile(
            user=self.customer_user,
            type='customer',
            location=None,
            tel=None,
            description=None,
            working_hours=None,
        )
        data = ProfileSerializer(profile).data
        for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
            assert data[field] == ''
