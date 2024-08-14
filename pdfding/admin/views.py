from admin.service import get_latest_version
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest
from django.shortcuts import redirect, render
from django.views import View
from django_htmx.http import HttpResponseClientRefresh
from pdf.models import Pdf


class BaseAdminView(UserPassesTestMixin, View):
    def test_func(self):
        if self.request.user.is_superuser and self.request.user.is_staff:
            return True
        else:
            raise Http404("Given query not found...")


class Overview(BaseAdminView):
    """
    View for the PDF overview page. This view performs the searching and sorting of the PDFs. It's also responsible for
    paginating the PDFs.
    """

    def get(self, request: HttpRequest, page: int = 1):
        """
        Display the PDF overview.
        """

        sorting_query = request.GET.get('sort', '')
        sorting_dict = {
            '': 'date_joined',
            'newest': '-date_joined',
            'oldest': 'date_joined',
            'title_asc': 'email',
            'title_desc': '-email',
        }

        users = User.objects.all().order_by(sorting_dict[sorting_query])

        # filter users
        raw_search_query = request.GET.get('q', '')

        if raw_search_query:
            search_words = raw_search_query.split()

            if '#admins' in search_words:
                users = users.filter(is_superuser=True)
                search_words.remove('#admins')

            search_query = ' '.join(search_words)
            users = users.filter(email__icontains=search_query)

        paginator = Paginator(users, per_page=request.user.profile.pdfs_per_page, allow_empty_first_page=True)
        page_object = paginator.get_page(page)

        number_of_users = User.objects.all().count()
        number_of_pdfs = Pdf.objects.all().count()
        latest_version = get_latest_version()

        return render(
            request,
            'admin_overview.html',
            {
                'page_obj': page_object,
                'raw_search_query': raw_search_query,
                'sorting_query': sorting_query,
                'number_of_users': number_of_users,
                'number_of_pdfs': number_of_pdfs,
                'current_version': settings.VERSION,
                'latest_version': latest_version,
            },
        )


class AdjustAdminRights(BaseAdminView):
    """View for adjusting the admin rights"""

    def post(self, request: HttpRequest, user_id: str):
        """Delete the user"""

        if request.htmx:
            user = User.objects.get(id=user_id)

            if user.is_staff and user.is_superuser:
                user.is_staff = False
                user.is_superuser = False
            else:
                user.is_staff = True
                user.is_superuser = True

            user.save()

            return HttpResponseClientRefresh()

        return redirect('admin_overview')


class DeleteProfile(BaseAdminView):
    """View for deleting a user profile"""

    def delete(self, request: HttpRequest, user_id: str):
        """Delete the user"""

        if request.htmx:
            user = User.objects.get(id=user_id)
            user.delete()

            return HttpResponseClientRefresh()

        return redirect('admin_overview')
