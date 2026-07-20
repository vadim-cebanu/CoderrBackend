from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'profile', views.ProfileViewSet, basename='profile')


urlpatterns = [
    path('registration/', views.registration_view, name='registration'),
    path('login/', views.login_view, name='login'),
    path('profiles/business/', views.business_profiles_view, name='business-profiles'),
    path('profiles/customer/', views.customer_profiles_view, name='customer-profiles'),

    path('', include(router.urls)),
]