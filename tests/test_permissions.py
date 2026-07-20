"""Unit tests for custom permission classes not yet wired into any view."""

from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory

from auth_app.models import Profile
from auth_app.permissions import IsCustomerUser, IsReviewer


class FakeReviewedObject:
    """Minimal stand-in for a model instance with a `reviewer` attribute."""

    def __init__(self, reviewer):
        self.reviewer = reviewer


class TestIsCustomerUser:
    """Test cases for the IsCustomerUser permission."""

    def test_allows_customer_user(self, db):
        user = User.objects.create_user(username='cust1', password='test123asd')
        Profile.objects.create(user=user, type='customer')
        request = APIRequestFactory().get('/')
        request.user = user
        assert IsCustomerUser().has_permission(request, None)

    def test_denies_business_user(self, db):
        user = User.objects.create_user(username='biz1', password='test123asd')
        Profile.objects.create(user=user, type='business')
        request = APIRequestFactory().get('/')
        request.user = user
        assert not IsCustomerUser().has_permission(request, None)


class TestIsReviewer:
    """Test cases for the IsReviewer permission."""

    def test_safe_method_always_allowed(self, db):
        user = User.objects.create_user(username='u1', password='test123asd')
        other = User.objects.create_user(username='u2', password='test123asd')
        request = APIRequestFactory().get('/')
        request.user = user
        obj = FakeReviewedObject(reviewer=other)
        assert IsReviewer().has_object_permission(request, None, obj)

    def test_unsafe_method_allowed_for_reviewer(self, db):
        user = User.objects.create_user(username='u3', password='test123asd')
        request = APIRequestFactory().patch('/')
        request.user = user
        obj = FakeReviewedObject(reviewer=user)
        assert IsReviewer().has_object_permission(request, None, obj)

    def test_unsafe_method_denied_for_non_reviewer(self, db):
        owner = User.objects.create_user(username='owner1', password='test123asd')
        other = User.objects.create_user(username='other1', password='test123asd')
        request = APIRequestFactory().patch('/')
        request.user = other
        obj = FakeReviewedObject(reviewer=owner)
        assert not IsReviewer().has_object_permission(request, None, obj)
