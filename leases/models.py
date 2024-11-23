from django.db import models
from users.models import User
from properties.models import Property
from datetime import date

class Lease(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
        ('pending', 'Pending'),  # Added Pending status
    ]

    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ]
    
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'tenant'})
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='unpaid')  # New field
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def is_active(self):
        return self.status == 'active' and self.end_date >= date.today()

    def __str__(self):
        return f"Lease {self.id} - {self.property.address} by {self.tenant.username}"
