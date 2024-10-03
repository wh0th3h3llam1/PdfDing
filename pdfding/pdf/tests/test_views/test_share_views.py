from io import BytesIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from pdf.forms import SharedDescriptionForm, SharedNameForm, ShareForm
from pdf.models import Pdf, SharedPdf
from pdf.views.share_views import (
    AddSharedPdfMixin,
    BaseSharedPdfPublicView,
    EditSharedPdfMixin,
    OverviewMixin,
    PdfPublicMixin,
    SharedPdfMixin,
)


def set_up(self):
    self.client = Client()
    self.user = User.objects.create_user(username=self.username, password=self.password, email='a@a.com')
    self.pdf = Pdf.objects.create(owner=self.user.profile, name='pdf')


class TestAddSharedPdfMixin(TestCase):
    username = 'user'
    password = '12345'

    def setUp(self):
        self.user = None
        self.pdf = None
        set_up(self)
        self.client.login(username=self.username, password=self.password)

    def test_get_context_get(self):
        # we need to create a request so get_pdf can access the user profile
        response = self.client.get(reverse('pdf_overview'))

        add_pdf_mixin = AddSharedPdfMixin()
        generated_context = add_pdf_mixin.get_context_get(response.wsgi_request, self.pdf.id)

        self.assertEqual({'form': ShareForm, 'pdf_name': self.pdf.name}, generated_context)

    @patch('pdf.views.share_views.AddSharedPdfMixin.generate_qr_code', return_value=BytesIO())
    def test_pre_obj_save(self, mock_generate_qr_code):

        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='share')
        other_pdf = Pdf.objects.create(owner=self.user.profile, name='other_pdf')
        # we need to create a request so get_pdf can access the user profile
        response = self.client.get(reverse('pdf_overview'))

        adjusted_shared_pdf = AddSharedPdfMixin.pre_obj_save(shared_pdf, response.wsgi_request, other_pdf.id)

        self.assertEqual(other_pdf, adjusted_shared_pdf.pdf)
        mock_generate_qr_code.assert_called_with(f'http://testserver/pdf/shared/{shared_pdf.id}')


class TestOverviewMixin(TestCase):
    username = 'user'
    password = '12345'

    def setUp(self):
        self.user = None
        self.pdf = None
        set_up(self)

        # create some pdfs
        for i in range(1, 4):
            SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name=f'shared_{i}')

    def test_filter_objects(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(f'{reverse('shared_pdf_overview')}?q=pdf_2+%23tag_2')
        filtered_shares = OverviewMixin.filter_objects(response.wsgi_request)
        shared_names = [shared.name for shared in filtered_shares]

        self.assertEqual(shared_names, ['shared_1', 'shared_2', 'shared_3'])


class TestSharedPdfMixin(TestCase):
    username = 'user'
    password = '12345'

    def setUp(self):
        self.user = None
        self.pdf = None
        set_up(self)

    def test_get_object(self):
        self.client.login(username=self.username, password=self.password)
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='share')
        # we need to create a request so get_pdf can access the user profile
        response = self.client.get(reverse('pdf_overview'))

        self.assertEqual(shared_pdf, SharedPdfMixin.get_object(response.wsgi_request, shared_pdf.id))


class TestEditSharedPdfMixin(TestCase):
    username = 'user'
    password = '12345'

    def setUp(self):
        self.user = None
        self.pdf = None
        set_up(self)

    def test_get_edit_form_get(self):
        shared_pdf = SharedPdf.objects.create(
            owner=self.user.profile, pdf=self.pdf, name='share', description='some_description'
        )

        edit_pdf_mixin_object = EditSharedPdfMixin()

        for field, form_class, field_value in zip(
            ['name', 'description'],
            [SharedNameForm, SharedDescriptionForm],
            ['share', 'some_description'],
        ):
            form = edit_pdf_mixin_object.get_edit_form_get(field, shared_pdf)
            self.assertIsInstance(form, form_class)
            self.assertEqual(form.initial, {field: field_value})


class TestPdfPublicMixin(TestCase):
    username = 'user'
    password = '12345'

    def setUp(self):
        self.user = None
        self.pdf = None
        set_up(self)

    def test_get_object(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='share')

        self.assertEqual(shared_pdf.pdf, PdfPublicMixin.get_object(None, shared_pdf.id))


class TestBaseSharedPdfPublicView(TestCase):
    username = 'user'
    password = '12345'

    def setUp(self):
        self.user = None
        self.pdf = None
        set_up(self)

    def test_get_object(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='share')

        self.assertEqual(shared_pdf, BaseSharedPdfPublicView.get_shared_pdf_public(None, shared_pdf.id))


class TestLoginNotRequiredViews(TestCase):
    username = 'user'
    password = '12345'

    def setUp(self):
        self.user = None
        self.pdf = None
        set_up(self)
        self.shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')

    def test_view_get(self):
        # test without http referer
        response = self.client.get(reverse('view_shared_pdf', kwargs={'identifier': self.shared_pdf.id}))

        self.assertEqual(response.context['shared_pdf'], self.shared_pdf)

    def test_view_post(self):
        self.assertEqual(self.shared_pdf.views, 0)

        response = self.client.post(reverse('view_shared_pdf', kwargs={'identifier': self.shared_pdf.id}))
        self.assertEqual(response.context['shared_pdf_id'], self.shared_pdf.id)
        self.assertEqual(response.context['theme_color_rgb'], '74 222 128')
        self.assertEqual(response.context['user_view_bool'], False)

        shared_pdf = SharedPdf.objects.get(pk=self.shared_pdf.id)
        self.assertEqual(shared_pdf.views, 1)
