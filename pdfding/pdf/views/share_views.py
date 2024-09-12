from core import base_views
from django.contrib.auth.decorators import login_not_required
from django.db.models import QuerySet
from django.db.models.functions import Lower
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from pdf.forms import SharedDescriptionForm, SharedNameForm, ShareForm
from pdf.models import SharedPdf
from pdf.service import check_object_access_allowed
from pdf.views.pdf_views import BasePdfView, PdfMixin


class BaseShareMixin:
    obj_name = 'shared_pdf'


class AddSharedPdfMixin(BaseShareMixin):
    form = ShareForm

    @staticmethod
    def get_pdf(request, pdf_id):
        """
        Get the PDF specified by the ID.
        """

        return PdfMixin.get_object(request, pdf_id)

    def get_context_get(self, request, pdf_id):
        """Get the context needed to be passed to the template containing the form for adding a shared PDf."""

        pdf = self.get_pdf(request, pdf_id)
        form = ShareForm()

        context = {'form': form, 'pdf_name': pdf.name}

        return context

    def pre_obj_save(self, shared_pdf, request, identifier):
        """Actions that need to be run before saving the shared PDF in the creation process"""

        pdf = self.get_pdf(request, identifier)
        shared_pdf.pdf = pdf

        return shared_pdf

    @staticmethod
    def post_obj_save(shared_pdf, form_data):
        """Actions that need to be run after saving the sharing PDF in the creation process"""

        pass


class OverviewMixin(BaseShareMixin):
    @staticmethod
    def get_sorting_dict():
        """
        Get the sorting dict which describes the sorting in the overview page.
        """

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
        """
        Filter the shared PDFs when performing a search in the overview.
        """

        shared_pdfs = SharedPdf.objects.filter(owner=request.user.profile).all()

        return shared_pdfs

    @staticmethod
    def get_extra_context(_) -> dict:
        """get further information that needs to be passed to the template."""

        extra_context = dict()

        return extra_context


class SharedPdfMixin(BaseShareMixin):
    obj_class = SharedPdf
    fields_requiring_extra_processing = []

    @staticmethod
    @check_object_access_allowed
    def get_object(request: HttpRequest, identifier: str):
        """Get the shered pdf specified by the ID"""

        user_profile = request.user.profile
        shared_pdf = user_profile.sharedpdf_set.get(id=identifier)

        return shared_pdf


class EditPdfMixin(SharedPdfMixin):
    @staticmethod
    def get_edit_form_dict():
        """Get the forms of the fields that can be edited as a dict."""

        form_dict = {'description': SharedDescriptionForm, 'name': SharedNameForm}

        return form_dict

    def get_edit_form_get(self, field_name: str, shared_pdf: SharedPdf):
        """Get the form belonging to the specified field."""

        form_dict = self.get_edit_form_dict()

        initial_dict = {
            'name': {'name': shared_pdf.name},
            'description': {'description': shared_pdf.description},
        }

        form = form_dict[field_name](initial=initial_dict[field_name])

        return form


class PdfPublicMixin:
    @staticmethod
    @check_object_access_allowed
    def get_object(_, shared_id: str):
        """Get the shared pdf specified by the ID"""

        shared_pdf = SharedPdf.objects.get(pk=shared_id)

        return shared_pdf.pdf


class BaseSharedPdfPublicView(BasePdfView):
    @staticmethod
    @check_object_access_allowed
    # first parameter needed because of the decorator
    def get_shared_pdf_public(_, shared_id: str):
        """Get the shared pdf specified by the ID without being logged in."""

        shared_pdf = SharedPdf.objects.get(pk=shared_id)

        return shared_pdf


class Share(AddSharedPdfMixin, base_views.BaseAdd):
    """View for new shared PDF files."""


class Overview(OverviewMixin, base_views.BaseOverview):
    """
    View for the shared PDF overview page. It's also responsible for paginating the shared PDFs.
    """


class Delete(SharedPdfMixin, base_views.BaseDelete):
    """View for deleting the shared PDF specified by its ID."""


class Edit(EditPdfMixin, base_views.BaseEdit):
    """
    The view for editing a shared PDF's name and description. The field, that is to be changed, is specified by the
    'field' argument.
    """


class Details(SharedPdfMixin, base_views.BaseDetails):
    """View for displaying the details page of a shared PDF."""


@method_decorator(login_not_required, name="dispatch")
class Serve(PdfPublicMixin, base_views.BaseServe):
    """View used for serving shared PDF files specified by the shared PDF id"""


@method_decorator(login_not_required, name="dispatch")
class Download(PdfPublicMixin, base_views.BaseDownload):
    """View for downloading the PDF specified by the ID."""


@method_decorator(login_not_required, name="dispatch")
class ViewShared(BaseSharedPdfPublicView):
    """The view responsible for displaying the shared PDF file specified by the shared PDF id in the browser."""

    def get(self, request: HttpRequest, identifier: str):
        shared_pdf = self.get_shared_pdf_public(request, identifier)

        return render(request, 'view_shared_info.html', {'shared_pdf': shared_pdf})

    def post(self, request: HttpRequest, identifier: str):
        shared_pdf = self.get_shared_pdf_public(request, identifier)
        shared_pdf.views += 1
        shared_pdf.save()

        return render(
            request,
            'viewer.html',
            {'shared_pdf_id': shared_pdf.id, 'theme_color_rgb': '74 222 128', 'user_view_bool': False},
        )
