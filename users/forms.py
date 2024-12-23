from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import User

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
        help_text="Enter a strong password."
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}),
        help_text="Enter the same password for verification."
    )

    class Meta:
        model = User
        fields = [
            'username', 
            'password1', 
            'password2', 
            'first_name', 
            'last_name', 
            'email', 
            'contact',
            'birthdate', 
            'address', 
            'province',
            'city', 
            'zipcode'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter username'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter last name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email address'}),
            'contact': forms.TextInput(attrs={'placeholder': 'Enter contact number'}),
            'birthdate': forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD', 'type': 'date'}),
            'address': forms.TextInput(attrs={'placeholder': 'Enter street address'}),
            'province': forms.TextInput(attrs={'placeholder': 'Enter province'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter city'}),
            'zipcode': forms.TextInput(attrs={'placeholder': 'Enter ZIP code'}),
        }

        help_texts = {
            'username': None,
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")

        # Check if the username already exists in the database
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different one.")
        
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Check if passwords match and modify error message
        
        return cleaned_data
