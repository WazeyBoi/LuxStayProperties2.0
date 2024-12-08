from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('tenant', 'Tenant'),
        ('property_owner', 'PropertyOwner'),
    ]
    
    # Role field
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')

    # Additional user attributes
    birthdate = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    zipcode = models.CharField(max_length=4, null=True, blank=True)
    contact = models.CharField(max_length=11, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
