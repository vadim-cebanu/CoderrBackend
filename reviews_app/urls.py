from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('base-info/', views.base_info_view, name='base-info'),
    path('', include(router.urls)),
]