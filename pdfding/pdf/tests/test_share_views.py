from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from core.settings import MEDIA_ROOT
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http.response import Http404, HttpResponse
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from django_htmx.http import HttpResponseClientRedirect, HttpResponseClientRefresh
from pdf.forms import ShareForm
from pdf.models import Pdf, SharedPdf
from pdf.views.share_views import BaseSharedPdfPublicView, BaseSharedPdfView


def set_up(self):
    self.client = Client()
    self.user = User.objects.create_user(username=self.username, password=self.password, email='a@a.com')
    self.pdf = Pdf.objects.create(owner=self.user.profile, name='pdf')


class TestLoginRequiredViews(TestCase):
    username = 'user'
    password = '12345'

    def setUp(self):
        self.user = None
        self.pdf = None
        set_up(self)
        self.client.login(username=self.username, password=self.password)

    def test_get_shared_pdf_existing(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='share')
        # we need to create a request so get_pdf can access the user profile
        response = self.client.get(reverse('pdf_overview'))
        request = response.wsgi_request

        self.assertEqual(shared_pdf, BaseSharedPdfView.get_shared_pdf(request, shared_pdf.id))

    def test_get_shared_pdf_validation(self):
        # we need to create a request so get_pdf can access the user profile
        response = self.client.get(reverse('pdf_overview'))
        request = response.wsgi_request

        with self.assertRaises(Http404):
            BaseSharedPdfView.get_shared_pdf(request, '12345')

    def test_get_shared_pdf_object_does_not_exist(self):
        # we need to create a request so get_pdf can access the user profile
        response = self.client.get(reverse('pdf_overview'))
        request = response.wsgi_request

        with self.assertRaises(Http404):
            BaseSharedPdfView.get_shared_pdf(request, str(uuid4()))

    def test_get_shared_pdf_public_existing(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='share')

        self.assertEqual(shared_pdf, BaseSharedPdfPublicView.get_shared_pdf_public(shared_pdf.id))

    def test_get_shared_pdf_public_validation(self):
        with self.assertRaises(Http404):
            BaseSharedPdfPublicView.get_shared_pdf_public('12345')

    def test_get_shared_pdf_public_object_does_not_exist(self):
        with self.assertRaises(Http404):
            BaseSharedPdfPublicView.get_shared_pdf_public(str(uuid4()))

    def test_share_get(self):
        response = self.client.get(reverse('share_pdf', kwargs={'pdf_id': self.pdf.id}))

        self.assertIsInstance(response.context['form'], ShareForm)

    def test_share_post_invalid_form(self):
        response = self.client.post(reverse('share_pdf', kwargs={'pdf_id': self.pdf.id}), data={'dummy': 'pdf'})

        self.assertIsInstance(response.context['form'], ShareForm)

    def test_share_post(self):
        self.client.post(
            reverse('share_pdf', kwargs={'pdf_id': self.pdf.id}),
            data={'name': 'share', 'description': 'something'},
        )

        shared_pdf = self.user.profile.sharedpdf_set.get(name='share')
        self.assertEqual(shared_pdf.description, 'something')

    def test_overview_get(self):
        # create some shares
        for name in ['orange', 'banana', 'Apple', 'Raspberry']:
            SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name=name)

        # sort by descending title
        response = self.client.get(f'{reverse('shared_pdf_overview')}?sort=title_desc')

        shared_pdf_names = [shared_pdf.name for shared_pdf in response.context['page_obj']]

        self.assertEqual(shared_pdf_names, ['Raspberry', 'orange', 'banana', 'Apple'])
        self.assertEqual(response.context['sorting_query'], 'title_desc')

    def test_details_get(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')

        # test without http referer
        response = self.client.get(reverse('shared_details', kwargs={'shared_id': shared_pdf.id}))

        self.assertEqual(response.context['shared_pdf'], shared_pdf)

    def test_edit_get_no_htmx(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')

        response = self.client.get(
            reverse('edit_shared', kwargs={'shared_id': shared_pdf.id, 'field_name': 'description'})
        )
        self.assertRedirects(response, reverse('shared_details', kwargs={'shared_id': shared_pdf.id}), status_code=302)

    def test_edit_get_htmx(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')
        headers = {'HTTP_HX-Request': 'true'}

        response = self.client.get(
            reverse('edit_shared', kwargs={'shared_id': shared_pdf.id, 'field_name': 'description'}), **headers
        )

        self.assertEqual(
            response.context['details_url'], reverse('shared_details', kwargs={'shared_id': shared_pdf.id})
        )
        self.assertEqual(
            response.context['action_url'],
            reverse('edit_shared', kwargs={'field_name': 'description', 'shared_id': shared_pdf.id}),
        )
        self.assertEqual(response.context['edit_id'], 'description-edit')
        self.assertEqual(response.context['field_name'], 'description')

    def test_edit_post_invalid_form(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')

        # post is invalid because data is missing
        # follow=True is needed for getting the message
        response = self.client.post(
            reverse('edit_shared', kwargs={'shared_id': shared_pdf.id, 'field_name': 'name'}),
            follow=True,
        )
        message = list(response.context['messages'])[0]

        self.assertEqual(message.message, 'Form not valid')
        self.assertEqual(message.tags, 'warning')

    def test_edit_post_description(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')

        self.client.post(
            reverse('edit_shared', kwargs={'shared_id': shared_pdf.id, 'field_name': 'description'}),
            data={'description': 'new'},
        )

        # get pdf again with the changes
        shared_pdf = self.user.profile.sharedpdf_set.get(id=shared_pdf.id)

        self.assertEqual(shared_pdf.description, 'new')

    def test_edit_post_name(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')

        self.client.post(
            reverse('edit_shared', kwargs={'shared_id': shared_pdf.id, 'field_name': 'name'}),
            data={'name': 'new'},
        )

        # get pdf again with the changes
        shared_pdf = self.user.profile.sharedpdf_set.get(id=shared_pdf.id)

        self.assertEqual(shared_pdf.name, 'new')

    def test_edit_post_name_existing(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')
        SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf_2', description='something')

        # follow=True is needed for getting the message
        response = self.client.post(
            reverse('edit_shared', kwargs={'shared_id': shared_pdf.id, 'field_name': 'name'}),
            data={'name': 'shared_pdf_2'},
            follow=True,
        )

        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, 'This name is already used by another PDF!')


class TestDelete(TransactionTestCase):
    # use TransactionTestCase as the qr code image needs to be deleted

    username = 'user'
    password = '12345'

    def setUp(self):
        self.user = None
        self.pdf = None
        set_up(self)
        self.client.login(username=self.username, password=self.password)

    def test_delete_htmx_not_from_details(self):
        # create a file for the test, so we can check that it was deleted by django_cleanup
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')

        headers = {'HTTP_HX-Request': 'true'}
        response = self.client.delete(reverse('delete_shared', kwargs={'shared_id': shared_pdf.id}), **headers)

        self.assertEqual(type(response), HttpResponseClientRefresh)
        self.assertFalse(self.user.profile.sharedpdf_set.filter(id=shared_pdf.id).exists())

    def test_delete_htmx_from_details(self):
        # create a file for the test, so we can check that it was deleted by django_cleanup
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')

        headers = {'HTTP_HX-Request': 'true'}
        response = self.client.delete(
            reverse('delete_shared', kwargs={'shared_id': shared_pdf.id}),
            HTTP_REFERER='pdfding.com/details/xx',
            **headers,
        )

        self.assertEqual(type(response), HttpResponseClientRedirect)
        self.assertFalse(self.user.profile.sharedpdf_set.filter(id=shared_pdf.id).exists())

    def test_delete_no_htmx(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')

        response = self.client.delete(reverse('delete_shared', kwargs={'shared_id': shared_pdf.id}))
        self.assertRedirects(response, reverse('shared_pdf_overview'), status_code=302)


class TestLoginNotRequiredViews(TestCase):
    username = 'user'
    password = '12345'

    def setUp(self):
        self.user = None
        self.pdf = None
        set_up(self)

    def test_view_get(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')

        # test without http referer
        response = self.client.get(reverse('view_shared', kwargs={'shared_id': shared_pdf.id}))

        self.assertEqual(response.context['shared_pdf'], shared_pdf)

    def test_view_post(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')

        self.assertEqual(shared_pdf.views, 0)

        response = self.client.post(reverse('view_shared', kwargs={'shared_id': shared_pdf.id}))
        self.assertEqual(response.context['shared_pdf_id'], shared_pdf.id)
        self.assertEqual(response.context['theme_color_rgb'], '74 222 128')
        self.assertEqual(response.context['user_view_bool'], False)

        shared_pdf = SharedPdf.objects.get(pk=shared_pdf.id)
        self.assertEqual(shared_pdf.views, 1)

    @patch('pdf.views.share_views.serve')
    def test_serve_get(self, mock_serve):
        self.pdf.file.name = f'{self.user}/pdf_name'
        self.pdf.save()
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=self.pdf, name='shared_pdf')
        mock_serve.return_value = HttpResponse('some response')

        response = self.client.get(reverse('serve_shared', kwargs={'shared_id': shared_pdf.id}))

        mock_serve.assert_called_with(response.wsgi_request, document_root=MEDIA_ROOT, path=f'{self.user}/pdf_name')

    def test_download_get(self):
        simple_file = SimpleUploadedFile("simple.pdf", b"these are the file contents!")
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf_with_file', file=simple_file)
        pdf_path = Path(pdf.file.path)
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, pdf=pdf, name='shared_pdf')

        response = self.client.get(reverse('download_shared', kwargs={'shared_id': shared_pdf.id}))

        pdf_path.unlink()

        self.assertEqual(response.filename, pdf.name)
        self.assertTrue(response.as_attachment)
