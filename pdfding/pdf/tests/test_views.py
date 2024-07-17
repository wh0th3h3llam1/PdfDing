from pathlib import Path
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http.response import Http404, HttpResponse
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse

from core.settings import MEDIA_ROOT
from pdf.models import Pdf, Tag
from pdf.views import BasePdfView
from pdf.forms import AddForm


def set_up(self):
    self.client = Client()

    self.user = User.objects.create_user(username=self.username, password=self.password, email='a@a.com')


class TestViews(TestCase):
    username = 'user'
    password = '12345'

    def setUp(self):
        self.user = None
        set_up(self)

    def test_login_required(self):
        response = self.client.get(reverse('pdf_overview'))

        self.assertRedirects(response, f'/accountlogin/?next={reverse('pdf_overview')}', status_code=302)

    def test_get_pdf_existing(self):
        self.client.login(username=self.username, password=self.password)
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf')
        response = self.client.get(reverse('pdf_overview'))
        request = response.wsgi_request

        self.assertEqual(pdf, BasePdfView.get_pdf(request, pdf.id))

    def test_get_pdf_not_existing(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('pdf_overview'))
        request = response.wsgi_request

        with self.assertRaises(Http404):
            BasePdfView.get_pdf(request, '12345')

    def test_overview_get(self):
        self.client.login(username=self.username, password=self.password)

        # create some pdfs
        for i in range(1, 15):
            pdf = Pdf.objects.create(owner=self.user.profile, name=f'pdf_{i % 5}_{i}')

            tag = Tag.objects.create(name='tag', owner=self.user.profile)

            # add a tag to pdf 2, 7
            if i % 5 == 2 and i < 10:
                pdf.tags.set([tag])

        # get the pdf files that start with pdf_2 and have the tag 'tag'
        # also sort them oldest to newest
        response = self.client.get(f'{reverse('pdf_overview')}?q=pdf_2+%23tag&sort=oldest')

        pdf_names = [pdf.name for pdf in response.context['page_obj']]

        self.assertEqual(pdf_names, ['pdf_2_2', 'pdf_2_7'])

    @patch('pdf.views.serve')
    def test_serve_get(self, mock_serve):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf')
        pdf.file.name = f'{self.user}/pdf_name'
        pdf.save()
        mock_serve.return_value = HttpResponse('some response')

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('serve_pdf', kwargs={'pdf_id': pdf.id}))

        mock_serve.assert_called_with(response.wsgi_request, document_root=MEDIA_ROOT, path=f'{self.user}/pdf_name')

    def test_view_get(self):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf')
        self.assertEqual(pdf.views, 0)

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('view_pdf', kwargs={'pdf_id': pdf.id}))

        # check that views increased by one
        pdf = self.user.profile.pdf_set.get(name='pdf')
        self.assertEqual(pdf.views, 1)

        self.assertEqual(response.context['pdf_id'], str(pdf.id))

    def test_add_get(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('add_pdf'))

        self.assertIsInstance(response.context['form'], AddForm)

    def test_add_post_invalid_form(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('add_pdf'), data={'name': 'pdf'})

        self.assertIsInstance(response.context['form'], AddForm)

    @patch('pdf.forms.magic.from_buffer', return_value='application/pdf')
    def test_add_post(self, mock_from_buffer):
        self.client.login(username=self.username, password=self.password)
        simple_file = SimpleUploadedFile("simple.pdf", b"these are the file contents!")

        self.client.post(
            reverse('add_pdf'),
            data={'name': 'pdf', 'description': 'something', 'tag_string': 'tag_a tag_2', 'file': simple_file},
        )

        pdf = self.user.profile.pdf_set.get(name='pdf')

        Path(pdf.file.path).unlink()

        tag_names = [tag.name for tag in pdf.tags.all()]
        self.assertEqual(set(tag_names), {'tag_2', 'tag_a'})
        self.assertEqual(pdf.description, 'something')

    def test_details_get(self):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf')
        self.client.login(username=self.username, password=self.password)

        # test without http referer
        response = self.client.get(reverse('pdf_details', kwargs={'pdf_id': pdf.id}))

        self.assertEqual(response.context['pdf'], pdf)
        self.assertEqual(response.context['sort_query'], '')

        # test without sort query
        response = self.client.get(
            reverse('pdf_details', kwargs={'pdf_id': pdf.id}), HTTP_REFERER='pdfding.com/details/?q=search'
        )

        self.assertEqual(response.context['pdf'], pdf)
        self.assertEqual(response.context['sort_query'], '')

        # test with sort query
        response = self.client.get(
            reverse('pdf_details', kwargs={'pdf_id': pdf.id}), HTTP_REFERER='pdfding.com/details/?q=search&sort=oldest'
        )

        self.assertEqual(response.context['pdf'], pdf)
        self.assertEqual(response.context['sort_query'], 'oldest')

    def test_edit_get_no_htmx(self):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf')
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse('edit_pdf', kwargs={'pdf_id': pdf.id, 'field': 'description'}))
        self.assertRedirects(response, reverse('pdf_details', kwargs={'pdf_id': pdf.id}), status_code=302)

    def test_edit_get_htmx(self):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf')
        self.client.login(username=self.username, password=self.password)
        headers = {'HTTP_HX-Request': 'true'}

        response = self.client.get(reverse('edit_pdf', kwargs={'pdf_id': pdf.id, 'field': 'description'}), **headers)

        self.assertEqual(response.context['pdf_id'], str(pdf.id))
        self.assertEqual(response.context['field'], 'description')

    def test_edit_post_description(self):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf', description='something')
        self.client.login(username=self.username, password=self.password)

        self.client.post(
            reverse('edit_pdf', kwargs={'pdf_id': pdf.id, 'field': 'description'}),
            data={'description': 'new'},
        )

        # get pdf again with the changes
        pdf = self.user.profile.pdf_set.get(id=pdf.id)

        self.assertEqual(pdf.description, 'new')

    def test_edit_post_name_existing(self):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf', description='something')
        Pdf.objects.create(owner=self.user.profile, name='pdf_2', description='something')
        self.client.login(username=self.username, password=self.password)

        # follow=True is needed for getting the message
        response = self.client.post(
            reverse('edit_pdf', kwargs={'pdf_id': pdf.id, 'field': 'name'}), data={'name': 'pdf_2'}, follow=True
        )

        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, 'This name is already used by another PDF!')

    def test_edit_post_name(self):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf', description='something')
        self.client.login(username=self.username, password=self.password)

        self.client.post(
            reverse('edit_pdf', kwargs={'pdf_id': pdf.id, 'field': 'name'}),
            data={'name': 'new'},
        )

        # get pdf again with the changes
        pdf = self.user.profile.pdf_set.get(id=pdf.id)

        self.assertEqual(pdf.name, 'new')

    def test_edit_post_tags(self):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf', description='something')
        tag_1 = Tag.objects.create(name='tag_1', owner=self.user.profile)
        tag_2 = Tag.objects.create(name='tag_2', owner=self.user.profile)

        pdf.tags.set([tag_1, tag_2])
        self.client.login(username=self.username, password=self.password)

        self.client.post(
            reverse('edit_pdf', kwargs={'pdf_id': pdf.id, 'field': 'tags'}),
            data={'tag_string': 'tag_1 tag_3'},
        )

        # get pdf again with the changes
        pdf = self.user.profile.pdf_set.get(id=pdf.id)
        tag_names = [tag.name for tag in pdf.tags.all()]

        self.assertEqual(sorted(tag_names), sorted(['tag_1', 'tag_3']))
        # check that tag 2 was deleted
        self.assertFalse(self.user.profile.tag_set.filter(name='tag_2').exists())

    def test_download_get(self):
        simple_file = SimpleUploadedFile("simple.pdf", b"these are the file contents!")
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf', file=simple_file)
        pdf_path = Path(pdf.file.path)

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('download_pdf', kwargs={'pdf_id': pdf.id}))

        pdf_path.unlink()

        self.assertEqual(response.filename, pdf.name)
        self.assertTrue(response.as_attachment)

    def test_update_page_post(self):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf')

        self.client.login(username=self.username, password=self.password)
        self.client.post(reverse('update_page'), data={'pdf_id': pdf.id, 'current_page': 10})

        # get pdf again with the changes
        pdf = self.user.profile.pdf_set.get(id=pdf.id)

        self.assertEqual(pdf.current_page, 10)

    def test_current_page_get(self):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf')
        pdf.current_page = 5
        pdf.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('current_page', kwargs={'pdf_id': pdf.id}))

        self.assertEqual(response.json()['current_page'], 5)


# we need the TransactionTestCase class because otherwise django_cleanup will not delete the file
class TestDelete(TransactionTestCase):
    username = 'user'
    password = '12345'

    def setUp(self):
        self.user = None
        set_up(self)

    def test_delete_delete_htmx(self):
        # create a file for the test, so we can check that it was deleted by django_cleanup
        simple_file = SimpleUploadedFile("simple.pdf", b"these are the file contents!")
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf', file=simple_file)
        pdf_path = Path(pdf.file.path)

        self.client.login(username=self.username, password=self.password)
        headers = {'HTTP_HX-Request': 'true'}
        self.client.delete(reverse('delete_pdf', kwargs={'pdf_id': pdf.id}), **headers)

        self.assertFalse(self.user.profile.pdf_set.filter(id=pdf.id).exists())
        self.assertFalse(pdf_path.exists())

    def test_delete_delete_no_htmx(self):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf')
        self.client.login(username=self.username, password=self.password)

        response = self.client.delete(reverse('delete_pdf', kwargs={'pdf_id': pdf.id}))
        self.assertRedirects(response, reverse('pdf_overview'), status_code=302)
