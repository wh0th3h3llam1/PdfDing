from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from users.models import Profile


class EmailForm(ModelForm):
    """The form for changing the email address."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']


class PdfsPerPageForm(ModelForm):
    """The form for setting the pdfs per page"""

    class Meta:
        model = Profile
        fields = ['pdfs_per_page']


class ThemeForm(ModelForm):
    """The form for setting dark mode"""

    class Meta:
        model = Profile
        fields = ['dark_mode', 'theme_color']
