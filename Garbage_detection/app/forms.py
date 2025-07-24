from django import forms
from .models import GarbageDetection

class GarbageDetectionForm(forms.ModelForm):
    class Meta:
        model = GarbageDetection
        fields = ['image']