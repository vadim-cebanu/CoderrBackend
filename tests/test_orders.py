import pytest
from rest_framework import status


class TestOrderEndpoints:
    """
    Test order-related endpoints: list, create, update status, delete (admin).
    """

    def test_list_orders_success(self, api_client, customer_user, order):
        """
        Test listing orders for the authenticated user.

        - GET /api/orders/.
        - Expect 200 and a list containing the user's order.
        """
        api_client.force_authenticate(user=customer_user)
        response = api_client.get('/api/orders/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == order.title

    def test_create_order_success(self, api_client, customer_user, offer):
        """
        Test creating an order as a customer.

        - POST /api/orders/ with offer_detail_id.
        - Expect 201 and the created order.
        """
        api_client.force_authenticate(user=customer_user)
        detail = offer.details.first()
        data = {'offer_detail_id': detail.id}
        response = api_client.post('/api/orders/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == detail.title
        assert response.data['customer_user'] == customer_user.id
        assert response.data['business_user'] == offer.user.id

    def test_create_order_not_customer(self, api_client, business_user, offer):
        """
        Test creating an order as a business user (should fail).

        - Expect 403.
        """
        api_client.force_authenticate(user=business_user)
        detail = offer.details.first()
        data = {'offer_detail_id': detail.id}
        response = api_client.post('/api/orders/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_order_status_success(self, api_client, business_user, order):
        """
        Test updating order status as the business user.

        - PATCH /api/orders/{id}/ with new status.
        - Expect 200 and updated order.
        """
        api_client.force_authenticate(user=business_user)
        data = {'status': 'completed'}
        response = api_client.patch(f'/api/orders/{order.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'completed'

    def test_update_order_status_unauthorized(self, api_client, customer_user, order):
        """
        Test updating order status as the customer (should fail).

        - Expect 403.
        """
        api_client.force_authenticate(user=customer_user)
        data = {'status': 'completed'}
        response = api_client.patch(f'/api/orders/{order.id}/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_order_admin_only(self, api_client, customer_user, order):
        """
        Test deleting an order as a non-admin (should fail).

        - Expect 403.
        """
        api_client.force_authenticate(user=customer_user)
        response = api_client.delete(f'/api/orders/{order.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_order_count_endpoint(self, api_client, business_user, order):
        """
        Test the order-count endpoint.

        - GET /api/order-count/{business_user_id}/.
        - Expect 200 and correct count.
        """
        api_client.force_authenticate(user=business_user)
        response = api_client.get(f'/api/order-count/{business_user.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['order_count'] == 1

    def test_completed_order_count_endpoint(self, api_client, business_user, order):
        """
        Test the completed-order-count endpoint.

        - Initially 0 completed orders.
        - After updating status, count should be 1.
        """
        api_client.force_authenticate(user=business_user)

        # Initially 0 completed
        response = api_client.get(f'/api/completed-order-count/{business_user.id}/')
        assert response.data['completed_order_count'] == 0

        # Update status to completed
        order.status = 'completed'
        order.save()

        response = api_client.get(f'/api/completed-order-count/{business_user.id}/')
        assert response.data['completed_order_count'] == 1