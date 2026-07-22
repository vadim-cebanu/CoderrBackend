from django.contrib.auth.models import User
from rest_framework import status

from offers_app.models import Offer, OfferDetail


class TestOfferEndpoints:
    """
    Test offer-related endpoints: list, create, retrieve, update, delete.
    """

    def test_list_offers_success(self, api_client, offer):
        """
        Test listing offers.

        - GET /api/offers/.
        - Expect 200 and paginated list containing the offer.
        """
        response = api_client.get('/api/offers/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'Website Design'

    def test_create_offer_success(self, api_client, business_user):
        """
        Test creating an offer as a business user.

        - POST /api/offers/ with valid data and 3 details.
        - Expect 201 and the created offer.
        """
        api_client.force_authenticate(user=business_user)
        data = {
            'title': 'Logo Design',
            'description': 'Professional logo design.',
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': 100,
                    'features': ['Logo'],
                    'offer_type': 'basic'
                },
                {
                    'title': 'Standard',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': 200,
                    'features': ['Logo', 'Brand Guide'],
                    'offer_type': 'standard'
                },
                {
                    'title': 'Premium',
                    'revisions': 10,
                    'delivery_time_in_days': 10,
                    'price': 500,
                    'features': ['Logo', 'Brand Guide', 'Social Media Kit'],
                    'offer_type': 'premium'
                }
            ]
        }
        response = api_client.post('/api/offers/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Logo Design'
        assert len(response.data['details']) == 3

    def test_create_offer_not_business_user(self, api_client, customer_user):
        """
        Test creating an offer as a customer (should fail).

        - Expect 403.
        """
        api_client.force_authenticate(user=customer_user)
        data = {'title': 'Test Offer', 'description': 'Test'}
        response = api_client.post('/api/offers/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_offer_invalid_details(self, api_client, business_user):
        """
        Test creating an offer with wrong number of details.

        - Expect 400.
        """
        api_client.force_authenticate(user=business_user)
        data = {
            'title': 'Test',
            'description': 'Test',
            'details': [{'title': 'Only One'}]
        }
        response = api_client.post('/api/offers/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_offer_success(self, api_client, customer_user, offer):
        """
        Test retrieving a specific offer.

        - GET /api/offers/{id}/.
        - Expect 200 and offer details.
        """
        api_client.force_authenticate(user=customer_user)
        response = api_client.get(f'/api/offers/{offer.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Website Design'
        assert 'details' in response.data

    def test_update_offer_success(self, api_client, business_user, offer):
        """
        Test updating an offer as the owner.

        - PATCH /api/offers/{id}/ with new title.
        - Expect 200 and updated offer.
        """
        api_client.force_authenticate(user=business_user)
        data = {'title': 'Updated Website Design'}
        response = api_client.patch(
            f'/api/offers/{offer.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Website Design'

    def test_update_offer_unauthorized(self, api_client, customer_user, offer):
        """
        Test updating an offer as a non-owner.

        - Expect 403.
        """
        api_client.force_authenticate(user=customer_user)
        data = {'title': 'Hacked Title'}
        response = api_client.patch(
            f'/api/offers/{offer.id}/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_offer_success(self, api_client, business_user, offer):
        """
        Test deleting an offer as the owner.

        - DELETE /api/offers/{id}/.
        - Expect 204.
        """
        api_client.force_authenticate(user=business_user)
        response = api_client.delete(f'/api/offers/{offer.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Offer.objects.filter(id=offer.id).exists()

    def test_delete_offer_unauthorized(self, api_client, customer_user, offer):
        """
        Test deleting an offer as a non-owner.

        - Expect 403.
        """
        api_client.force_authenticate(user=customer_user)
        response = api_client.delete(f'/api/offers/{offer.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_offer_and_detail_str_representation(self, offer):
        """
        Test Offer.__str__ and OfferDetail.__str__.
        """
        assert str(offer) == 'Website Design'
        detail = offer.details.get(offer_type='basic')
        assert str(detail) == 'Website Design - basic'

    def test_offer_user_details_missing_profile(self, api_client, customer_user):
        """
        Test that user_details falls back to {} when the offer's creator has no Profile.
        """
        orphan_user = User.objects.create_user(
            username='noprofile', password='test123asd')
        orphan_offer = Offer.objects.create(
            user=orphan_user, title='Orphan Offer', description='No profile owner.'
        )
        api_client.force_authenticate(user=customer_user)
        response = api_client.get(f'/api/offers/{orphan_offer.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user_details'] == {}

    def test_create_offer_wrong_number_of_details(self, api_client, business_user):
        """
        Test creating an offer with only 2 (valid) details instead of 3.

        - Expect 400 from the custom validate_details count check.
        """
        api_client.force_authenticate(user=business_user)
        data = {
            'title': 'Test',
            'description': 'Test',
            'details': [
                {
                    'title': 'Basic', 'revisions': 2, 'delivery_time_in_days': 5,
                    'price': 100, 'offer_type': 'basic'
                },
                {
                    'title': 'Standard', 'revisions': 5, 'delivery_time_in_days': 7,
                    'price': 200, 'offer_type': 'standard'
                },
            ]
        }
        response = api_client.post('/api/offers/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_offer_duplicate_offer_type(self, api_client, business_user):
        """
        Test creating an offer with 3 details but a duplicated offer_type.

        - Expect 400 from the custom validate_details uniqueness check.
        """
        api_client.force_authenticate(user=business_user)
        data = {
            'title': 'Test',
            'description': 'Test',
            'details': [
                {
                    'title': 'Basic', 'revisions': 2, 'delivery_time_in_days': 5,
                    'price': 100, 'offer_type': 'basic'
                },
                {
                    'title': 'Basic Again', 'revisions': 2, 'delivery_time_in_days': 5,
                    'price': 100, 'offer_type': 'basic'
                },
                {
                    'title': 'Premium', 'revisions': 10, 'delivery_time_in_days': 10,
                    'price': 500, 'offer_type': 'premium'
                },
            ]
        }
        response = api_client.post('/api/offers/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_offer_with_details(self, api_client, business_user, offer):
        """
        Test PATCHing an offer's nested details updates the matching OfferDetail rows.
        """
        api_client.force_authenticate(user=business_user)
        data = {
            'details': [
                {
                    'title': 'Basic', 'revisions': 3, 'delivery_time_in_days': 4,
                    'price': 150, 'offer_type': 'basic'
                },
                {
                    'title': 'Standard', 'revisions': 5, 'delivery_time_in_days': 7,
                    'price': 200, 'offer_type': 'standard'
                },
                {
                    'title': 'Premium', 'revisions': 10, 'delivery_time_in_days': 10,
                    'price': 500, 'offer_type': 'premium'
                },
            ]
        }
        response = api_client.patch(
            f'/api/offers/{offer.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        updated_basic = OfferDetail.objects.get(
            offer=offer, offer_type='basic')
        assert float(updated_basic.price) == 150
        assert updated_basic.revisions == 3

    def test_list_offers_filter_by_creator_id(self, api_client, offer, business_user):
        """
        Test filtering offers by creator_id query param.
        """
        response = api_client.get(
            f'/api/offers/?creator_id={business_user.id}')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_list_offers_filter_by_min_price(self, api_client, offer):
        """
        Test filtering offers by min_price excludes offers below the threshold.
        """
        response = api_client.get('/api/offers/?min_price=1000')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_list_offers_filter_by_max_delivery_time(self, api_client, offer):
        """
        Test filtering offers by max_delivery_time excludes offers slower than the threshold.
        """
        response = api_client.get('/api/offers/?max_delivery_time=1')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_list_offers_filter_by_search(self, api_client, offer):
        """
        Test filtering offers by search matches the title.
        """
        response = api_client.get('/api/offers/?search=Website')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_list_offers_ordering(self, api_client, offer):
        """
        Test ordering offers by a real model field (updated_at).
        """
        response = api_client.get('/api/offers/?ordering=updated_at')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_list_offers_ordering_by_min_price(self, api_client, business_user, offer):
        """
        Test ordering offers by the annotated min_price (cheapest first).
        """
        expensive = Offer.objects.create(
            user=business_user, title='Expensive Offer', description='Pricey.'
        )
        OfferDetail.objects.create(
            offer=expensive, title='Basic', revisions=1, delivery_time_in_days=3,
            price=500, offer_type='basic'
        )
        OfferDetail.objects.create(
            offer=expensive, title='Standard', revisions=2, delivery_time_in_days=4,
            price=600, offer_type='standard'
        )
        OfferDetail.objects.create(
            offer=expensive, title='Premium', revisions=3, delivery_time_in_days=5,
            price=700, offer_type='premium'
        )

        response = api_client.get('/api/offers/?ordering=min_price')
        assert response.status_code == status.HTTP_200_OK
        titles = [item['title'] for item in response.data['results']]
        assert titles == ['Website Design', 'Expensive Offer']

    def test_list_offers_page_size(self, api_client, business_user, offer):
        """
        Test that the page_size query param overrides the default page size.
        """
        for i in range(3):
            extra = Offer.objects.create(
                user=business_user, title=f'Extra {i}', description='x'
            )
            for offer_type, price in [('basic', 10), ('standard', 20), ('premium', 30)]:
                OfferDetail.objects.create(
                    offer=extra, title=offer_type, revisions=1, delivery_time_in_days=2,
                    price=price, offer_type=offer_type
                )

        response = api_client.get('/api/offers/?page_size=2')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 4
        assert len(response.data['results']) == 2

    def test_offer_details_are_hyperlinked_in_list(self, api_client, offer):
        """
        Test that list/retrieve represent details as {id, url} links, not full objects.
        """
        response = api_client.get('/api/offers/')
        assert response.status_code == status.HTTP_200_OK
        detail_entry = response.data['results'][0]['details'][0]
        assert set(detail_entry.keys()) == {'id', 'url'}
        assert '/api/offerdetails/' in detail_entry['url']

    def test_retrieve_offer_requires_authentication(self, api_client, offer):
        """
        Test that retrieving a single offer requires authentication (unlike listing).
        """
        response = api_client.get(f'/api/offers/{offer.id}/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_offer_with_single_detail(self, api_client, business_user, offer):
        """
        Test that PATCH accepts a single detail (not all 3), matching only by offer_type.
        """
        api_client.force_authenticate(user=business_user)
        data = {
            'details': [
                {
                    'title': 'Basic Updated', 'revisions': 3, 'delivery_time_in_days': 6,
                    'price': 120, 'offer_type': 'basic'
                }
            ]
        }
        response = api_client.patch(
            f'/api/offers/{offer.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK

        updated_basic = OfferDetail.objects.get(
            offer=offer, offer_type='basic')
        assert float(updated_basic.price) == 120
        untouched_standard = OfferDetail.objects.get(
            offer=offer, offer_type='standard')
        assert float(untouched_standard.price) == 200

    def test_offerdetail_retrieve_success(self, api_client, customer_user, offer):
        """
        Test GET /api/offerdetails/{id}/ returns the full detail.
        """
        detail = offer.details.get(offer_type='basic')
        api_client.force_authenticate(user=customer_user)
        response = api_client.get(f'/api/offerdetails/{detail.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['offer_type'] == 'basic'
        assert float(response.data['price']) == 100

    def test_offerdetail_retrieve_unauthenticated(self, api_client, offer):
        """
        Test GET /api/offerdetails/{id}/ requires authentication.
        """
        detail = offer.details.get(offer_type='basic')
        response = api_client.get(f'/api/offerdetails/{detail.id}/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_offerdetail_retrieve_not_found(self, api_client, customer_user):
        """
        Test GET /api/offerdetails/{id}/ returns 404 for a non-existent detail.
        """
        api_client.force_authenticate(user=customer_user)
        response = api_client.get('/api/offerdetails/999999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
