from core.settings import MEDIA_ROOT
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.forms import ValidationError
from django.http import FileResponse, Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.static import serve
from django_htmx.http import HttpResponseClientRedirect, HttpResponseClientRefresh
from pdf.forms import AddForm, DescriptionForm, NameForm, TagsForm
from pdf.models import Pdf, Tag
from pdf.service import get_tag_dict, process_raw_search_query, process_tag_names


class BasePdfView(LoginRequiredMixin, View):
    @staticmethod
    def get_pdf(request: HttpRequest, pdf_id: str):
        try:
            user_profile = request.user.profile
            pdf = user_profile.pdf_set.get(id=pdf_id)
        except ValidationError:
            raise Http404("Given query not found...")
        except ObjectDoesNotExist:
            raise Http404("Given query not found...")

        return pdf


def redirect_overview(request: HttpRequest):  # pragma: no cover
    """
    Simple view for redirecting to the pdf overview. This is used when the root url is accessed.

    GET: Redirect to the PDF overview page.
    """

    return redirect('pdf_overview')


class Overview(BasePdfView):
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
            '': '-creation_date',
            'newest': '-creation_date',
            'oldest': 'creation_date',
            'title_asc': Lower('name'),
            'title_desc': Lower('name').desc(),
            'least_viewed': 'views',
            'most_viewed': '-views',
        }

        pdfs = request.user.profile.pdf_set.all().order_by(sorting_dict[sorting_query])

        # filter pdfs
        raw_search_query = request.GET.get('q', '')
        search, tags = process_raw_search_query(raw_search_query)

        for tag in tags:
            pdfs = pdfs.filter(tags__name=tag)

        if search:
            pdfs = pdfs.filter(name__icontains=search)

        paginator = Paginator(pdfs, per_page=request.user.profile.pdfs_per_page, allow_empty_first_page=True)
        page_object = paginator.get_page(page)
        tag_dict = get_tag_dict(request.user.profile)

        return render(
            request,
            'pdf_overview.html',
            {
                'page_obj': page_object,
                'raw_search_query': raw_search_query,
                'sorting_query': sorting_query,
                'tag_dict': tag_dict,
            },
        )


class Serve(BasePdfView):
    """View used for serving PDF files specified by the PDF id"""

    def get(self, request: HttpRequest, pdf_id: str):
        """Returns the specified file as a FileResponse"""

        pdf = self.get_pdf(request, pdf_id)

        return serve(request, document_root=MEDIA_ROOT, path=pdf.file.name)


class View(BasePdfView):
    """The view responsible for displaying the PDF file specified by the PDF id in the browser."""

    def get(self, request: HttpRequest, pdf_id: str):
        """Display the PDF file in the browser"""

        # increase view counter by 1
        pdf = self.get_pdf(request, pdf_id)
        pdf.views += 1
        pdf.save()

        # set theme color rgb value
        theme_color_rgb_dict = {
            'Green': '74 222 128',
            'Blue': '71 147 204',
            'Gray': '151 170 189',
            'Red': '248 113 113',
            'Pink': '218 123 147',
            'Orange': '255 203 133',
        }

        return render(
            request,
            'viewer.html',
            {
                'pdf_id': pdf_id,
                'theme_color_rgb': theme_color_rgb_dict[request.user.profile.theme_color],
                'user_view_bool': True,
            },
        )


class Add(BasePdfView):
    """View for adding new PDF files."""

    def get(self, request: HttpRequest):
        """Display the form for adding a PDF file."""

        form = AddForm()

        return render(request, 'add_pdf.html', {'form': form})

    def post(self, request: HttpRequest):
        """Create the new PDF object."""

        form = AddForm(request.POST, request.FILES, owner=request.user.profile)

        if form.is_valid():
            pdf = form.save(commit=False)
            pdf.owner = request.user.profile
            pdf.save()

            tag_string = form.data['tag_string']
            # get unique tag names
            tag_names = Tag.parse_tag_string(tag_string)
            tags = process_tag_names(tag_names, pdf.owner)

            pdf.tags.set(tags)

            return redirect('pdf_overview')

        return render(request, 'add_pdf.html', {'form': form})


class Details(BasePdfView):
    """View for displaying the details page of a PDF."""

    def get(self, request: HttpRequest, pdf_id: str):
        """Display the details page."""

        pdf = self.get_pdf(request, pdf_id)

        sort_query = request.META.get('HTTP_REFERER', '').split('sort=')

        if len(sort_query) > 1:
            sort_query = sort_query[-1]
        else:
            sort_query = ''

        return render(request, 'pdf_details.html', {'pdf': pdf, 'sort_query': sort_query})


class Edit(BasePdfView):
    """
    The view for editing a PDF's name, tags and description. The field, that is to be changed, is specified by the
    'field' argument.
    """

    form_dict = {'description': DescriptionForm, 'name': NameForm, 'tags': TagsForm}

    def get(self, request: HttpRequest, pdf_id: str, field_name: str):
        """Triggered by htmx. Display an inline form for editing the correct field."""

        pdf = self.get_pdf(request, pdf_id)

        initial_dict = {
            'name': {'name': pdf.name},
            'description': {'description': pdf.description},
            'tags': {'tag_string': ' '.join(sorted([tag.name for tag in pdf.tags.all()]))},
        }

        if request.htmx:
            form = self.form_dict[field_name](initial=initial_dict[field_name])

            return render(
                request,
                'partials/details_form.html',
                {
                    'action_url': reverse('edit_pdf', kwargs={'field_name': field_name, 'pdf_id': pdf_id}),
                    'edit_id': f'{field_name}-edit',
                    'form': form,
                    'field_name': field_name,
                    'pdf_id': pdf_id,
                },
            )

        return redirect('pdf_details', pdf_id=pdf_id)

    def post(self, request: HttpRequest, pdf_id: str, field_name: str):
        """
        POST: Change the specified field by submitting the form.
        """

        pdf = self.get_pdf(request, pdf_id)
        form = self.form_dict[field_name](request.POST, instance=pdf)

        if form.is_valid():
            # if tags are changed the provided tag string needs to processed, the PDF's tags need updating and orphaned
            # tags need to be deleted.
            if field_name == 'tags':
                tag_string = form.data['tag_string']
                tag_names = Tag.parse_tag_string(tag_string)

                # check if tag needs to be deleted
                for tag in pdf.tags.all():
                    if tag.name not in tag_names and tag.pdf_set.count() == 1:
                        tag.delete()

                tags = process_tag_names(tag_names, request.user.profile)

                pdf.tags.set(tags)

            # if the name is changed we need to check that it is a unique name not used by another pdf of this user.
            elif field_name == 'name':
                existing_pdf = Pdf.objects.filter(owner=request.user.profile, name__iexact=form.data['name']).first()

                if existing_pdf and str(existing_pdf.id) != pdf_id:
                    messages.warning(request, 'This name is already used by another PDF!')
                else:
                    form.save()

            # if description is changed save it
            else:
                form.save()
        else:
            messages.warning(request, 'Form not valid')
        return redirect('pdf_details', pdf_id=pdf_id)


class Delete(BasePdfView):
    """View for deleting the PDF specified by its ID."""

    def delete(self, request: HttpRequest, pdf_id: str):
        """Delete the specified PDF."""

        if request.htmx:
            pdf = self.get_pdf(request, pdf_id)
            pdf.delete()

            # try to redirect to current page
            if 'details' not in request.META.get('HTTP_REFERER', ''):
                return HttpResponseClientRefresh()
            # if deleted from the details page the details page will no longer exist
            else:  # pragma: no cover
                return HttpResponseClientRedirect(reverse('pdf_overview'))

        return redirect('pdf_overview')


class Download(BasePdfView):
    """View for downloading the PDF specified by the ID."""

    def get(self, request: HttpRequest, pdf_id):
        """Return the specified file as a FileResponse."""

        pdf = self.get_pdf(request, pdf_id)
        file_name = pdf.name.replace(' ', '_').lower()
        response = FileResponse(open(pdf.file.path, 'rb'), as_attachment=True, filename=file_name)

        return response


class UpdatePage(BasePdfView):
    """
    View for updating the current page of the viewed PDF. This is triggered everytime the page the user changes the
    displayed page in the browser.
    """

    def post(self, request: HttpRequest):
        """Change the current page."""

        pdf_id = request.POST.get('pdf_id')
        pdf = self.get_pdf(request, pdf_id)

        # update current page
        current_page = request.POST.get('current_page')
        pdf.current_page = current_page
        pdf.save()

        return HttpResponse(status=200)


class CurrentPage(BasePdfView):
    """View for getting the current page of a PDF."""

    def get(self, request: HttpRequest, pdf_id: str):
        """Get the current page of the specified PDF."""

        pdf = self.get_pdf(request, pdf_id)

        return JsonResponse({'current_page': pdf.current_page}, status=200)
