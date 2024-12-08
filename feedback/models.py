from django.db import models
from users.models import User

class Feedback(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('viewed', 'Viewed'),
    ]

    feedbackId = models.AutoField(primary_key=True)
    propertyId = models.ForeignKey('properties.Property', on_delete=models.CASCADE, default=1)   # Replace Lease with Property
    tenantId = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'tenant'})
    submissionDate = models.DateField(auto_now_add=True)
    starRating = models.IntegerField()  # Assuming a scale of 1-5 or 1-10
    comments = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')

    def __str__(self):
        return f'Feedback {self.feedbackId} for Property {self.propertyId} by Tenant {self.tenantId}'
