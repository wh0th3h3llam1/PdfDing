from unittest import mock

from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from pdf import forms
from pdf.models import Pdf, SharedPdf


class TestPdfForms(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user', password='12345', email='a@a.com')

    @mock.patch('pdf.forms.magic.from_buffer', return_value='application/pdf')
    def test_add_form_valid(self, mock_from_buffer):
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test1.pdf'
        form = forms.AddForm(data={'name': 'PDF Name'}, owner=self.user.profile, files={'file': file_mock})

        self.assertTrue(form.is_valid())

    @mock.patch('pdf.forms.magic.from_buffer', return_value='application/pdf')
    def test_clean_missing_owner(self, mock_from_buffer):
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test1.pdf'
        form = forms.AddForm(data={'name': 'PDF Name'}, files={'file': file_mock})

        self.assertFalse(form.is_valid())

    @mock.patch('pdf.forms.magic.from_buffer', return_value='application/pdf')
    def test_pdf_clean_name_existing(self, mock_from_buffer):
        # create pdf for user
        Pdf.objects.create(owner=self.user.profile, name='existing name')
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test1.pdf'
        # create the form with the already existing pdf name
        form = forms.AddForm(data={'name': 'existing name'}, owner=self.user.profile, files={'file': file_mock})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['A PDF with this name already exists!'])

    def test_pdf_clean_file_wrong_suffix(self):
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'not_pdf.txt'
        form = forms.AddForm(data={'name': 'not_pdf'}, owner=self.user.profile, files={'file': file_mock})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['file'], ['Uploaded file is not a PDF!'])

    def test_pdf_clean_file_wrong_file_type(self):
        simple_file = SimpleUploadedFile("not_pdf.pdf", b"these are the file contents!")
        form = forms.AddForm(data={'name': 'not_pdf'}, owner=self.user.profile, files={'file': simple_file})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['file'], ['Uploaded file is not a PDF!'])

    def test_clean_name(self):
        inputs = ['  this is some    name with whitespaces ', 'simple']
        expected_output = ['this is some name with whitespaces', 'simple']
        generated_output = [forms.clean_name(i) for i in inputs]

        self.assertEqual(expected_output, generated_output)


class TestShareForms(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user', password='12345', email='a@a.com')

    def test_add_form_valid(self):
        form = forms.ShareForm(data={'name': 'Share Name'}, owner=self.user.profile)

        self.assertTrue(form.is_valid())

    def test_clean_missing_owner(self):
        form = forms.ShareForm(data={'name': 'Share Name'})

        self.assertFalse(form.is_valid())

    def test_pdf_clean_name_existing(self):
        # create pdf for user
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf_name')
        SharedPdf.objects.create(owner=self.user.profile, pdf=pdf, name='existing name')
        # create the form with the already existing pdf name
        form = forms.ShareForm(data={'name': 'existing name'}, owner=self.user.profile)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['A Share with this name already exists!'])
