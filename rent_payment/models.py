# rent_payment/models.py
from django.db import models

from users.models import User

class Payment(models.Model):
    # Define choices for paymentMethod
    CASH = 'cash'
    CREDIT_CARD = 'credit_card'
    DEBIT_CARD = 'debit_card'

    PAYMENT_METHOD_CHOICES = [
        (CASH, 'Cash'),
        (CREDIT_CARD, 'Credit Card'),
        (DEBIT_CARD, 'Debit Card'),
    ]

    # Define choices for status
    PAID = 'paid'
    UNPAID = 'unpaid'

    STATUS_CHOICES = [
        (PAID, 'Paid'),
        (UNPAID, 'Unpaid'),
    ]

    paymentId = models.AutoField(primary_key=True)
    leaseId = models.ForeignKey('leases.Lease', on_delete=models.CASCADE)
    tenantId = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'tenant'})  # Foreign key to User model
    paymentDate = models.DateField()
    paymentMethod = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=CASH  # Default to 'Cash' if nothing is selected
    )
    totalAmount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,  # Adjusted max_length based on your choices
        choices=STATUS_CHOICES,
        default=UNPAID  # Default to 'Unpaid' if nothing is selected
    )

    def __str__(self):
        return f'Payment {self.paymentId} for Tenant {self.tenantId}'
