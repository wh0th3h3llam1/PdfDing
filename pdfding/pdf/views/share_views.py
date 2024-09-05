from core.settings import MEDIA_ROOT
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.forms import ValidationError
from django.http import FileResponse, Http404, HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.static import serve
from django_htmx.http import HttpResponseClientRedirect, HttpResponseClientRefresh
from pdf.forms import SharedDescriptionForm, SharedNameForm, ShareForm
from pdf.models import SharedPdf
from pdf.views.pdf_views import BasePdfView


class BaseSharedPdfView(BasePdfView):
    @staticmethod
    def get_shared_pdf(request: HttpRequest, shared_id: str):
        try:
            user_profile = request.user.profile
            shared_pdf = user_profile.sharedpdf_set.get(id=shared_id)
        except ValidationError:
            raise Http404("Given query not found...")
        except ObjectDoesNotExist:
            raise Http404("Given query not found...")

        return shared_pdf


class BaseSharedPdfPublicView(View):
    @staticmethod
    def get_shared_pdf_public(shared_id: str):
        try:
            shared_pdf = SharedPdf.objects.get(pk=shared_id)
        except ValidationError:
            raise Http404("Given query not found...")
        except ObjectDoesNotExist:
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

        shared_pdfs = request.user.profile.sharedpdf_set.all().order_by(sorting_dict[sorting_query])

        paginator = Paginator(shared_pdfs, per_page=request.user.profile.pdfs_per_page, allow_empty_first_page=True)
        page_object = paginator.get_page(page)

        return render(
            request,
            'shared_overview.html',
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
            else:
                return HttpResponseClientRedirect(reverse('shared_overview'))

        return redirect('shared_overview')


class Edit(BaseSharedPdfView):
    """
    The view for editing a PDshared F's name and description. The field, that is to be changed, is specified by the
    'field' argument.
    """

    form_dict = {'description': SharedDescriptionForm, 'name': SharedNameForm}

    def get(self, request: HttpRequest, shared_id: str, field_name: str):
        """Triggered by htmx. Display an inline form for editing the correct field."""

        shared_pdf = self.get_shared_pdf(request, shared_id)

        initial_dict = {
            'name': {'name': shared_pdf.name},
            'description': {'description': shared_pdf.description},
        }

        if request.htmx:
            form = self.form_dict[field_name](initial=initial_dict[field_name])

            return render(
                request,
                'partials/details_form.html',
                {
                    'action_url': reverse('edit_shared', kwargs={'field_name': field_name, 'shared_id': shared_id}),
                    'details_url': reverse('shared_details', kwargs={'shared_id': shared_id}),
                    'edit_id': f'{field_name}-edit',
                    'form': form,
                    'field_name': field_name,
                },
            )

        return redirect('shared_details', shared_id=shared_id)

    def post(self, request: HttpRequest, shared_id: str, field_name: str):
        """
        POST: Change the specified field by submitting the form.
        """

        shared_pdf = self.get_shared_pdf(request, shared_id)
        form = self.form_dict[field_name](request.POST, instance=shared_pdf)

        if form.is_valid():
            # if the name is changed we need to check that it is a unique name not used by another pdf of this user.
            if field_name == 'name':
                existing_shared_pdf = SharedPdf.objects.filter(
                    owner=request.user.profile, name__iexact=form.data['name']
                ).first()

                if existing_shared_pdf and str(existing_shared_pdf.id) != shared_id:
                    messages.warning(request, 'This name is already used by another PDF!')
                else:
                    form.save()

            # if description is changed save it
            else:
                form.save()
        else:
            messages.warning(request, 'Form not valid')
        return redirect('shared_details', shared_id=shared_id)


class Details(BaseSharedPdfView):
    def get(self, request: HttpRequest, shared_id: str):
        shared_pdf = self.get_shared_pdf(request, shared_id)

        return render(request, 'shared_pdf_details.html', {'shared_pdf': shared_pdf})


class Serve(BaseSharedPdfPublicView):
    """View used for serving shared PDF files specified by the shared PDF id"""

    def get(self, request: HttpRequest, shared_id: str):
        """Returns the specified file as a FileResponse"""

        shared_pdf = self.get_shared_pdf_public(shared_id)

        return serve(request, document_root=MEDIA_ROOT, path=shared_pdf.pdf.file.name)


class Download(BaseSharedPdfPublicView):
    """View for downloading the PDF specified by the ID."""

    def get(self, request: HttpRequest, shared_id):
        """Return the specified file as a FileResponse."""

        shared_pdf = self.get_shared_pdf_public(shared_id)
        pdf = shared_pdf.pdf
        file_name = pdf.name.replace(' ', '_').lower()
        response = FileResponse(open(pdf.file.path, 'rb'), as_attachment=True, filename=file_name)

        return response


class ViewShared(BaseSharedPdfPublicView):
    """The view responsible for displaying the shared PDF file specified by the shared PDF id in the browser."""

    def get(self, request: HttpRequest, shared_id: str):
        shared_pdf = self.get_shared_pdf_public(shared_id)

        return render(request, 'view_shared_info.html', {'shared_pdf': shared_pdf})

    def post(self, request: HttpRequest, shared_id: str):
        shared_pdf = self.get_shared_pdf_public(shared_id)
        shared_pdf.views += 1
        shared_pdf.save()

        # set theme color rgb value
        # theme_color_rgb_dict = {
        #     'Green': '74 222 128',
        #     'Blue': '71 147 204',
        #     'Gray': '151 170 189',
        #     'Red': '248 113 113',
        #     'Pink': '218 123 147',
        #     'Orange': '255 203 133',
        # }

        return render(
            request,
            'viewer.html',
            {'shared_pdf_id': shared_pdf.id, 'theme_color_rgb': '74 222 128', 'user_view_bool': False},
        )
