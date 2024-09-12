from core import base_views
from django.contrib.auth.decorators import login_not_required
from django.db.models import QuerySet
from django.db.models.functions import Lower
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from pdf.forms import AddForm, DescriptionForm, NameForm, TagsForm
from pdf.models import Pdf, Tag
from pdf.service import check_object_access_allowed, get_tag_dict, process_raw_search_query, process_tag_names


class BasePdfMixin:
    obj_name = 'pdf'


class AddSharedPdfMixin(BasePdfMixin):
    form = AddForm

    def get_context_get(self, _, __):
        """Get the context needed to be passed to the template containing the form for adding a PDf."""

        context = {'form': self.form}

        return context

    @staticmethod
    def pre_obj_save(pdf, _, __):
        """Actions that need to be run before saving the PDF in the creation process"""

        return pdf

    @staticmethod
    def post_obj_save(pdf, form_data):
        """Actions that need to be run after saving the PDF in the creation process"""

        tag_string = form_data['tag_string']
        # get unique tag names
        tag_names = Tag.parse_tag_string(tag_string)
        tags = process_tag_names(tag_names, pdf.owner)

        pdf.tags.set(tags)


class OverviewMixin(BasePdfMixin):
    @staticmethod
    def get_sorting_dict():
        """Get the sorting dict which describes the sorting in the overview page."""

        sorting_dict = {
            '': '-creation_date',
            'newest': '-creation_date',
            'oldest': 'creation_date',
            'title_asc': Lower('name'),
            'title_desc': Lower('name').desc(),
            'least_viewed': 'views',
            'most_viewed': '-views',
        }

        return sorting_dict

    @staticmethod
    def filter_objects(request: HttpRequest) -> QuerySet:
        """Filter the PDFs when performing a search in the overview."""

        pdfs = Pdf.objects.filter(owner=request.user.profile).all()

        raw_search_query = request.GET.get('q', '')
        search, tags = process_raw_search_query(raw_search_query)

        for tag in tags:
            pdfs = pdfs.filter(tags__name=tag)

        if search:
            pdfs = pdfs.filter(name__icontains=search)

        return pdfs

    @staticmethod
    def get_extra_context(request: HttpRequest) -> dict:
        """get further information that needs to be passed to the template."""

        extra_context = {'raw_search_query': request.GET.get('q', ''), 'tag_dict': get_tag_dict(request.user.profile)}

        return extra_context


class PdfMixin(BasePdfMixin):
    @staticmethod
    @check_object_access_allowed
    def get_object(request: HttpRequest, pdf_id: str):
        """Get the pdf specified by the ID"""

        user_profile = request.user.profile
        pdf = user_profile.pdf_set.get(id=pdf_id)

        return pdf


class EditPdfMixin(PdfMixin):
    obj_class = Pdf
    fields_requiring_extra_processing = ['tags']

    @staticmethod
    def get_edit_form_dict():
        """Get the forms of the fields that can be edited as a dict."""

        form_dict = {'description': DescriptionForm, 'name': NameForm, 'tags': TagsForm}

        return form_dict

    def get_edit_form_get(self, field_name: str, pdf: Pdf):
        """Get the form belonging to the specified field."""

        form_dict = self.get_edit_form_dict()

        initial_dict = {
            'name': {'name': pdf.name},
            'description': {'description': pdf.description},
            'tags': {'tag_string': ' '.join(sorted([tag.name for tag in pdf.tags.all()]))},
        }

        form = form_dict[field_name](initial=initial_dict[field_name])

        return form

    @staticmethod
    def process_field(field_name, pdf, request, form_data):
        """Process fields that are not covered in the base edit view."""

        if field_name == 'tags':
            tag_string = form_data['tag_string']
            tag_names = Tag.parse_tag_string(tag_string)

            # check if tag needs to be deleted
            for tag in pdf.tags.all():
                if tag.name not in tag_names and tag.pdf_set.count() == 1:
                    tag.delete()

            tags = process_tag_names(tag_names, request.user.profile)

            pdf.tags.set(tags)


class BasePdfView(View):
    @staticmethod
    @check_object_access_allowed
    def get_pdf(request: HttpRequest, pdf_id: str):
        """Get the pdf specified by the ID"""

        user_profile = request.user.profile
        pdf = user_profile.pdf_set.get(id=pdf_id)

        return pdf


@login_not_required
def redirect_to_overview(request: HttpRequest):  # pragma: no cover
    """
    Simple view for redirecting to the pdf overview. This is used when the root url is accessed.

    GET: Redirect to the PDF overview page.
    """

    return redirect('pdf_overview')


class Overview(OverviewMixin, base_views.BaseOverview):
    """
    View for the PDF overview page. This view performs the searching and sorting of the PDFs. It's also responsible for
    paginating the PDFs.
    """


class Serve(PdfMixin, base_views.BaseServe):
    """View used for serving PDF files specified by the PDF id"""


class Add(AddSharedPdfMixin, base_views.BaseAdd):
    """View for adding new PDF files."""


class Details(PdfMixin, base_views.BaseDetails):
    """View for displaying the details page of a PDF."""


class Edit(EditPdfMixin, base_views.BaseEdit):
    """
    The view for editing a PDF's name, tags and description. The field, that is to be changed, is specified by the
    'field' argument.
    """


class Delete(PdfMixin, base_views.BaseDelete):
    """View for deleting the PDF specified by its ID."""


class Download(PdfMixin, base_views.BaseDownload):
    """View for downloading the PDF specified by the ID."""


class View(BasePdfView):
    """The view responsible for displaying the PDF file specified by the PDF id in the browser."""

    def get(self, request: HttpRequest, identifier: str):
        """Display the PDF file in the browser"""

        # increase view counter by 1
        pdf = self.get_pdf(request, identifier)
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
                'pdf_id': identifier,
                'theme_color_rgb': theme_color_rgb_dict[request.user.profile.theme_color],
                'user_view_bool': True,
            },
        )


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

    def get(self, request: HttpRequest, identifier: str):
        """Get the current page of the specified PDF."""

        pdf = self.get_pdf(request, identifier)

        return JsonResponse({'current_page': pdf.current_page}, status=200)
