from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('order-count/<int:business_user_id>/', views.order_count_view, name='order-count'),
    path('completed-order-count/<int:business_user_id>/', views.completed_order_count_view, name='completed-order-count'),
    path('', include(router.urls)),
]