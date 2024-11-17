# maintenance_request/models.py
from django.db import models
from users.models import User
from leases.models import Lease  # Assuming there's a Lease model in leases app

class MaintenanceRequest(models.Model):
    requestId = models.AutoField(primary_key=True)
    leaseId = models.ForeignKey(Lease, on_delete=models.CASCADE)
    tenantId = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'tenant'})
    requestDate = models.DateField(auto_now_add=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')])

    def __str__(self):
        return f'Maintenance Request {self.requestId} by Tenant {self.tenantId}'
