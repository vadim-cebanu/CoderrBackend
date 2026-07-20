from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Offer(models.Model):
    """
    A service offer created by a business user.

    Always has exactly 3 related OfferDetail tiers (basic/standard/premium).
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.CharField(max_length=255, blank=True, null=True)
    description= models.TextField()
    created_at= models.DateTimeField(default=timezone.now)
    updated_at= models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.title
    
    
class OfferDetail(models.Model):
    """
    A single pricing tier (basic/standard/premium) belonging to an Offer.
    """
    OFFER_TYPES = (
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )
    
    offer= models.ForeignKey(Offer,related_name='details', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    revisions=models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPES)
    
    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"