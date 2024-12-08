from django import forms
from .models import Payment
from django.utils.timezone import now

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['paymentDate', 'paymentMethod', 'totalAmount', 'cardNumber', 'cardExpiration', 'cardCVV']
        labels = {
            'paymentDate': 'Payment Date',
            'paymentMethod': 'Payment Method',
            'totalAmount': 'Total Amount',
            'cardNumber': 'Card Number',
            'cardExpiration': 'Expiration Date',
            'cardCVV': 'CVV'
        }

    paymentDate = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        initial=now().date()
    )

    paymentMethod = forms.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    totalAmount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    cardNumber = forms.CharField(
        max_length=19, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234 5678 9012 3456'}),
        required=True
    )

    cardExpiration = forms.CharField(
        max_length=5, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'}),
        required=True
    )

    cardCVV = forms.CharField(
        max_length=3, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CVV'}),
        required=True
    )
