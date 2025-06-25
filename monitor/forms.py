from django import forms
from .models import RegistrationInfo

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = RegistrationInfo
        fields = ['school_name', 'city', 'pc_count']



