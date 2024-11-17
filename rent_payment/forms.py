from django import forms
from .models import Payment
from django.utils.timezone import now

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['paymentDate', 'paymentMethod', 'totalAmount']
    
    paymentMethod = forms.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    paymentDate = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        initial=now().date  # Set the default to today's date
    )

