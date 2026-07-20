import pytest
from rest_framework import status


class TestBaseInfo:
    """
    Test the platform-wide statistics endpoint.
    """

    def test_base_info_success(self, api_client, review, business_user, offer):
        """
        Test the base-info endpoint.

        - GET /api/base-info/.
        - Expect 200 and correct counts/averages.
        """
        response = api_client.get('/api/base-info/')
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['review_count'] == 1
        assert data['average_rating'] == 5.0
        assert data['business_profile_count'] == 1
        assert data['offer_count'] == 1