from django import forms
from .models import Payment
from django.utils.timezone import now

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['paymentDate', 'paymentMethod', 'totalAmount']

    paymentDate = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        initial=now().date()
    )

    paymentMethod = forms.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    totalAmount = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        })
    )


