from allauth.account.utils import send_email_confirmation
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .forms import EmailForm, PdfsPerPageForm, ThemeForm


class BaseUserView(LoginRequiredMixin, View):
    pass


@login_required
def settings(request):
    """View for the profile settings page"""

    uses_social = request.user.socialaccount_set.exists()

    # pragma: no cover
    return render(request, 'profile_settings.html', {'uses_social': uses_social})


class ChangeSetting(BaseUserView):
    """View for changing the theme."""

    form_dict = {'email': EmailForm, 'pdfs_per_page': PdfsPerPageForm, 'theme': ThemeForm}

    def get(self, request: HttpRequest, field_name: str):
        """For a htmx request this will load a change pdfs per page form as a partial"""

        initial_dict = {
            'email': {'email': request.user.email},
            'pdfs_per_page': {'pdfs_per_page': request.user.profile.pdfs_per_page},
            'theme': {'dark_mode': request.user.profile.dark_mode, 'theme_color': request.user.profile.theme_color},
        }

        if request.htmx:
            form = self.form_dict[field_name](initial=initial_dict[field_name])

            return render(
                request,
                'partials/settings_form.html',
                {
                    'form': form,
                    'action_url': reverse('profile-setting-change', kwargs={'field_name': field_name}),
                    'edit_id': f'{field_name}-edit',
                },
            )

        return redirect('home')

    def post(self, request: HttpRequest, field_name: str):
        """Process the submitted change settings form"""

        if field_name == 'email':
            form = self.form_dict[field_name](request.POST, instance=request.user)
        else:
            form = self.form_dict[field_name](request.POST, instance=request.user.profile)

        if form.is_valid():
            if field_name == 'email':
                email = form.cleaned_data['email']
                if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                    messages.warning(request, f'{email} is already in use.')
                    return redirect('profile-settings')
                form.save()

                # Then send confirmation email
                send_email_confirmation(request, request.user)
            else:
                form.save()

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
