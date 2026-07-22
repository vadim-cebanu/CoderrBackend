from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from offers_app.models import OfferDetail


class Order(models.Model):
    """
    An order placed by a customer based on an OfferDetail.

    Links a customer user and a business user, and stores order details
    (title, revisions, delivery time, price, features, offer_type, status).
    """
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    customer_user = models.ForeignKey(
        User, related_name='customer_orders', on_delete=models.CASCADE
    )
    business_user = models.ForeignKey(
        User, related_name='business_orders', on_delete=models.CASCADE
    )
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=10)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.title}"
