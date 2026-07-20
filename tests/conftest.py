import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from auth_app.models import Profile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def business_user(db):
    user = User.objects.create_user(
        username='business1', email='business1@example.com', password='test123asd'
    )
    Profile.objects.create(user=user, type='business')
    return user


@pytest.fixture
def customer_user(db):
    user = User.objects.create_user(
        username='customer1', email='customer1@example.com', password='test123asd'
    )
    Profile.objects.create(user=user, type='customer')
    return user


@pytest.fixture
def offer(business_user):
    offer = Offer.objects.create(
        user=business_user,
        title='Website Design',
        description='A professional website design service.',
    )
    OfferDetail.objects.create(
        offer=offer, title='Basic', revisions=2, delivery_time_in_days=5,
        price=100, features=['Logo'], offer_type='basic'
    )
    OfferDetail.objects.create(
        offer=offer, title='Standard', revisions=5, delivery_time_in_days=7,
        price=200, features=['Logo', 'Brand Guide'], offer_type='standard'
    )
    OfferDetail.objects.create(
        offer=offer, title='Premium', revisions=10, delivery_time_in_days=10,
        price=500, features=['Logo', 'Brand Guide', 'Social Media Kit'], offer_type='premium'
    )
    return offer


@pytest.fixture
def order(customer_user, offer):
    detail = offer.details.first()
    return Order.objects.create(
        customer_user=customer_user,
        business_user=offer.user,
        offer_detail=detail,
        title=detail.title,
        revisions=detail.revisions,
        delivery_time_in_days=detail.delivery_time_in_days,
        price=detail.price,
        features=detail.features,
        offer_type=detail.offer_type,
        status='in_progress',
    )
