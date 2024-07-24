from django.shortcuts import render, redirect
from allauth.account.utils import send_email_confirmation
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.views import View

from .forms import ThemeForm, EmailForm


class BaseUserView(LoginRequiredMixin, View):
    pass


@login_required
def settings(request):
    """View for the profile settings page"""

    uses_social = request.user.socialaccount_set.exists()

    # pragma: no cover
    return render(request, 'profile_settings.html', {'uses_social': uses_social})


class ChangeEmail(BaseUserView):
    """View for changing the email address."""

    def get(self, request: HttpRequest):
        """For a htmx request this will load an email change form as a partial"""

        if request.htmx:
            form = EmailForm(instance=request.user)
            return render(request, 'partials/email_form.html', {'form': form})

        return redirect('home')

    def post(self, request: HttpRequest):
        """Process the submitted email form"""

        form = EmailForm(request.POST, instance=request.user)

        if form.is_valid():
            # Check if the email already exists
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.warning(request, f'{email} is already in use.')
                return redirect('profile-settings')

            form.save()

            # Then send confirmation email
            send_email_confirmation(request, request.user)

            return redirect('profile-settings')
        else:
            messages.warning(request, 'Form not valid')
            return redirect('profile-settings')


class ChangeTheme(BaseUserView):
    """View for changing the theme."""

    def get(self, request: HttpRequest):
        """For a htmx request this will load a change theme form as a partial"""

        if request.htmx:
            form = ThemeForm(
                instance=request.user,
                initial={'dark_mode': request.user.profile.dark_mode, 'theme_color': request.user.profile.theme_color},
            )
            return render(request, 'partials/theme_form.html', {'form': form})

        return redirect('home')

    def post(self, request: HttpRequest):
        """Process the submitted change theme form"""

        form = ThemeForm(request.POST, instance=request.user)

        if form.is_valid():
            # for some reason form.save has no effect, so we do it manually...
            profile = request.user.profile
            profile.dark_mode = form.cleaned_data['dark_mode']
            profile.theme_color = form.cleaned_data['theme_color']
            profile.save()

            return redirect('profile-settings')
        else:
            messages.warning(request, 'Form not valid')
            return redirect('profile-settings')


class Delete(BaseUserView):
    """View for deleting a user profile."""

    def get(self, request: HttpRequest):  # pragma: no cover
        """Display the page for deleting the user"""

        return render(request, 'profile_delete.html')

    def post(self, request: HttpRequest):
        """Delete the user"""

        user = request.user

        logout(request)
        user.delete()
        messages.success(request, 'Your Account was successfully deleted.')

        return redirect('home')
