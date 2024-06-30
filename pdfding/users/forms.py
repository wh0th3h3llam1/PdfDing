from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User


class EmailForm(ModelForm):
    """The form for changing the email address."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']
