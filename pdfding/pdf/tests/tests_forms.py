from unittest import mock

from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.core.files import File
from django.test import Client, TestCase

from pdf import forms
from pdf.models import Pdf, Tag


class TestForms(TestCase):
    def setUp(self):
        self.client = Client()

        # this will not create an email address object
        self.user = User.objects.create_user(username='user', password='12345', email='a@a.com')
        # so we need to create it
        EmailAddress.objects.create(user=self.user, email=self.user.email, primary=True, verified=True)

    def test_add_form_valid(self):
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test1.pdf'
        form = forms.AddForm(data={'name': 'PDF Name'}, owner=self.user.profile, files={'file': file_mock})

        self.assertTrue(form.is_valid())

    def test_clean_missing_owner(self):
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test1.pdf'
        form = forms.AddForm(data={'name': 'PDF Name'}, files={'file': file_mock})

        self.assertFalse(form.is_valid())

    def test_pdf_clean_name_existing(self):
        # create pdf for user
        Pdf.objects.create(owner=self.user.profile, name='existing name')
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test1.pdf'
        # create the form with the already existing pdf name
        form = forms.AddForm(data={'name': 'existing name'}, owner=self.user.profile, files={'file': file_mock})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['A PDF with this name already exists!'])

    def test_pdf_clean_file(self):
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'not_pdf.txt'
        form = forms.AddForm(data={'name': 'not_pdf'}, owner=self.user.profile, files={'file': file_mock})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['file'], ['Uploaded file is not a PDF!'])

    def test_get_detail_form_class_not_tags(self):
        field_name = 'name'
        field_value = 'pdf_name'

        pdf = Pdf.objects.create(owner=self.user.profile, name=field_value)

        form = forms.get_detail_form_class(field_name, pdf)
        self.assertEqual(
            str(form[field_name]),
            f'<input type="text" name="{field_name}" '
            f'value="{field_value}" maxlength="50" required id="id_{field_name}">',
        )

    def test_get_detail_form_class_tags(self):
        field_name = 'tags'
        field_value = ['tag_x', 'tag_a', 'tag_3']

        pdf = Pdf.objects.create(owner=self.user.profile, name=field_value)
        tags = [Tag.objects.create(name=tag_name, owner=pdf.owner) for tag_name in field_value]
        pdf.tags.set(tags)

        form = forms.get_detail_form_class(field_name, pdf)

        self.assertEqual(
            str(form['tag_string']),
            f'<input type="text" name="tag_string" value="{' '.join(sorted(field_value))}"'
            f' rows="3" class="form-control" required id="id_tag_string">',
        )
        self.assertEqual(form.initial, {'tag_string': ' '.join(sorted(field_value))})

    def test_get_detail_form_class_with_data(self):
        field_name = 'description'
        field_value = 'new description'
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf')

        form = forms.get_detail_form_class(field_name=field_name, instance=pdf, data={field_name: field_value})
        form.save()
        self.assertEqual(Pdf.objects.get(name='pdf').description, field_value)

    def test_clean_name(self):
        inputs = ['  this is some    name with whitespaces ', 'simple']
        expected_output = ['this is some name with whitespaces', 'simple']
        generated_output = [forms.clean_name(i) for i in inputs]

        self.assertEqual(expected_output, generated_output)
