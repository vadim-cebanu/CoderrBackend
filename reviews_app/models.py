from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Review(models.Model):
    """
    A review left by a customer for a business user.

    Each customer can review a business user only once.
    """
    business_user = models.ForeignKey(
        User, related_name='business_reviews', on_delete=models.CASCADE
    )
    reviewer = models.ForeignKey(
        User, related_name='reviews_given', on_delete=models.CASCADE
    )
    rating = models.PositiveIntegerField()  # e.g., 1-5
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['business_user', 'reviewer']
        ordering = ['id']

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.business_user.username}"
