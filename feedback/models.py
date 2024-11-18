# feedback/models.py
from django.db import models
from users.models import User
from leases.models import Lease  # Assuming there's a Lease model in leases app

class Feedback(models.Model):
    feedbackId = models.AutoField(primary_key=True)
    leaseId = models.ForeignKey(Lease, on_delete=models.CASCADE)
    tenantId = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'tenant'})
    submissionDate = models.DateField(auto_now_add=True)
    starRating = models.IntegerField()  # Assuming a scale of 1-5 or 1-10
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Feedback {self.feedbackId} by Tenant {self.tenantId}'