from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()

urlpatterns = [
    path('registration/', views.registration_view, name='registration'),
    path('login/', views.login_view, name='login'),
    path('', include(router.urls)),
]