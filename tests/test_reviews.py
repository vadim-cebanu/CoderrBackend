import pytest
from rest_framework import status

from reviews_app.models import Review


class TestReviewEndpoints:
    """
    Test review-related endpoints: list, create, update, delete.
    """

    def test_list_reviews_success(self, api_client, customer_user, review):
        """
        Test listing reviews.

        - GET /api/reviews/.
        - Expect 200 and a list containing the review.
        """
        api_client.force_authenticate(user=customer_user)
        response = api_client.get('/api/reviews/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['rating'] == 5

    def test_create_review_success(self, api_client, customer_user, business_user):
        """
        Test creating a review as a customer.

        - POST /api/reviews/ with valid data.
        - Expect 201 and the created review.
        """
        api_client.force_authenticate(user=customer_user)
        data = {
            'business_user': business_user.id,
            'rating': 4,
            'description': 'Good service.'
        }
        response = api_client.post('/api/reviews/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['rating'] == 4
        assert response.data['reviewer'] == customer_user.id

    def test_create_review_not_customer(self, api_client, business_user):
        """
        Test creating a review as a business user (should fail).

        - Expect 403.
        """
        api_client.force_authenticate(user=business_user)
        data = {'business_user': business_user.id, 'rating': 5}
        response = api_client.post('/api/reviews/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_duplicate_review(self, api_client, customer_user, review):
        """
        Test creating a second review for the same business user.

        - Expect 400 or 403 (depending on implementation).
        """
        api_client.force_authenticate(user=customer_user)
        data = {
            'business_user': review.business_user.id,
            'rating': 3,
            'description': 'Another review'
        }
        response = api_client.post('/api/reviews/', data, format='json')
        assert response.status_code in [400, 403]

    def test_update_review_success(self, api_client, customer_user, review):
        """
        Test updating a review as the reviewer.

        - PATCH /api/reviews/{id}/ with new rating/description.
        - Expect 200 and updated review.
        """
        api_client.force_authenticate(user=customer_user)
        data = {'rating': 3, 'description': 'Updated review'}
        response = api_client.patch(f'/api/reviews/{review.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['rating'] == 3
        assert response.data['description'] == 'Updated review'

    def test_update_review_unauthorized(self, api_client, business_user, review):
        """
        Test updating a review as a non-reviewer.

        - Expect 403.
        """
        api_client.force_authenticate(user=business_user)
        data = {'rating': 1}
        response = api_client.patch(f'/api/reviews/{review.id}/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_review_success(self, api_client, customer_user, review):
        """
        Test deleting a review as the reviewer.

        - DELETE /api/reviews/{id}/.
        - Expect 204.
        """
        api_client.force_authenticate(user=customer_user)
        response = api_client.delete(f'/api/reviews/{review.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Review.objects.filter(id=review.id).exists()

    def test_delete_review_unauthorized(self, api_client, business_user, review):
        """
        Test deleting a review as a non-reviewer.

        - Expect 403.
        """
        api_client.force_authenticate(user=business_user)
        response = api_client.delete(f'/api/reviews/{review.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN