# maintenance_request/models.py
from django.db import models
from users.models import User
from properties.models import Property  # Assuming you have a Property model in a properties app

class MaintenanceRequest(models.Model):
    requestId = models.AutoField(primary_key=True)
    propertyId = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    tenantId = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'tenant'})
    requestDate = models.DateField(auto_now_add=True)
    subject = models.TextField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')])

    def __str__(self):
        return f'Maintenance Request {self.requestId} for Property {self.propertyId}'
