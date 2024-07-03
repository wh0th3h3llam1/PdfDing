from django.shortcuts import render, redirect
from allauth.account.utils import send_email_confirmation
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import EmailForm


@login_required
def settings(request):
    """View for the profile settings page"""

    uses_social = request.user.socialaccount_set.exists()

    return render(request, 'profile_settings.html', {'uses_social': uses_social})


@login_required
def change_email(request):
    """
    View for changing the email address. For a htmx request this will load an email chage form as a partial. In case
    of a post request the submitted email form will be processed.
    """

    if request.htmx:
        form = EmailForm(instance=request.user)
        return render(request, 'partials/email_form.html', {'form': form})

    if request.method == 'POST':
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

    return redirect('home')


@login_required
def delete(request):
    """View for deleting a user profile."""

    user = request.user
    if request.method == "POST":
        logout(request)
        user.delete()
        messages.success(request, 'Your Account was successfully deleted.')
        return redirect('home')

    return render(request, 'profile_delete.html')
