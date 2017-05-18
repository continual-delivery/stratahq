from django import forms
from .models import StrataServer

class ServerForm(forms.ModelForm):
    class Meta:
        model = StrataServer
        fields = ['override_puppet_role', 'override_puppet_environment', 'status']