from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.forms import ValidationError
from django.http import Http404, HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django_htmx.http import HttpResponseClientRedirect, HttpResponseClientRefresh
from pdf.forms import ShareForm
from pdf.views.pdf_views import BasePdfView


class BaseSharedPdfView(BasePdfView):
    @staticmethod
    def get_shared_pdf(request: HttpRequest, shared_id: str):
        try:
            user_profile = request.user.profile
            shared_pdf = user_profile.sharedpdf_set.get(id=shared_id)
        except ValidationError:
            raise Http404("Given query not found...")

        return shared_pdf


class Share(BaseSharedPdfView):
    """View for  new PDF files."""

    def get(self, request: HttpRequest, pdf_id: str):
        """Display the form for sharing a PDF file."""

        pdf = self.get_pdf(request, pdf_id)
        form = ShareForm()

        return render(request, 'share_pdf.html', {'form': form, 'pdf_name': pdf.name})

    def post(self, request: HttpRequest, pdf_id: str):
        """Create the new Shared PDF object."""

        pdf = self.get_pdf(request, pdf_id)
        form = ShareForm(request.POST, request.FILES, owner=request.user.profile)

        if form.is_valid():
            shared_pdf = form.save(commit=False)
            shared_pdf.owner = request.user.profile
            shared_pdf.pdf = pdf
            shared_pdf.save()

            return redirect('shared_overview')

        return render(request, 'share_pdf.html', {'form': form})


class Overview(BaseSharedPdfView):
    def get(self, request: HttpRequest, page: int = 1):
        sorting_query = request.GET.get('sort', '')
        sorting_dict = {
            '': '-creation_date',
            'newest': '-creation_date',
            'oldest': 'creation_date',
            'title_asc': Lower('name'),
            'title_desc': Lower('name').desc(),
        }
        print(sorting_query)

        shared_pdfs = request.user.profile.sharedpdf_set.all().order_by(sorting_dict[sorting_query])
        for item in shared_pdfs:
            print(item)
            print(item.name)

        paginator = Paginator(shared_pdfs, per_page=request.user.profile.pdfs_per_page, allow_empty_first_page=True)
        page_object = paginator.get_page(page)

        return render(
            request,
            'share_overview.html',
            {
                'page_obj': page_object,
                'sorting_query': sorting_query,
            },
        )


class Delete(BaseSharedPdfView):
    """View for deleting the shared PDF specified by its ID."""

    def delete(self, request: HttpRequest, shared_id: str):
        """Delete the specified shared PDF."""

        if request.htmx:
            shared_pdf = self.get_shared_pdf(request, shared_id)
            shared_pdf.delete()

            # try to redirect to current page
            if 'details' not in request.META.get('HTTP_REFERER', ''):
                return HttpResponseClientRefresh()
            # if deleted from the details page the details page will no longer exist
            else:  # pragma: no cover
                return HttpResponseClientRedirect(reverse('shared_overview'))

        return redirect('shared_overview')


class Present(View):
    def get(self, request: HttpRequest, share_id: str):
        pass


class View(View):
    pass
