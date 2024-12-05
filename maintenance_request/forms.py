from django import forms
from .models import MaintenanceRequest  # Adjust based on your project structure

class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['subject', 'description']  # Include other necessary fields as needed

    