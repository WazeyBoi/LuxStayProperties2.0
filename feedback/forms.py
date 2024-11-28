from django import forms
from .models import Feedback
from django.core.exceptions import ValidationError
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['starRating', 'comments']

    def clean_starRating(self):
        starRating = self.cleaned_data.get('starRating')
        if starRating not in range(1, 6):  # Assuming a 1-5 scale
            raise ValidationError('Invalid star rating.')
        return starRating