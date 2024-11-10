from django.contrib.auth.decorators import login_not_required
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View


@method_decorator(login_not_required, name="dispatch")
class AboutView(View):
    """The view for displaying the about page"""

    def get(self, request: HttpRequest):
        """Display the about page"""

        return render(request, 'about.html')
