from datetime import datetime, timedelta, timezone

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from pdf.models import Pdf, SharedPdf


class TestCleanUpSharedPdfs(TestCase):
    def test_clean_up_shared_pdfs(self):
        user = User.objects.create_user(username='user', password='password', email='a@a.com')
        pdf = Pdf.objects.create(owner=user.profile, name='1.pdf')

        shared_pdf_1 = SharedPdf.objects.create(
            owner=user.profile,
            name='shared_pdf_1',
            pdf=pdf,
            deletion_date=datetime.now(timezone.utc) - timedelta(minutes=5),
        )
        shared_pdf_2 = SharedPdf.objects.create(
            owner=user.profile,
            name='shared_pdf_2',
            pdf=pdf,
            deletion_date=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        shared_pdf_3 = SharedPdf.objects.create(owner=user.profile, name='shared_pdf_3', pdf=pdf)

        shared_pdfs_set_before = {shared_pdf for shared_pdf in SharedPdf.objects.all()}
        self.assertEqual(shared_pdfs_set_before, {shared_pdf_1, shared_pdf_2, shared_pdf_3})

        call_command('clean_up_shared_pdfs')

        shared_pdfs_set_after = {shared_pdf for shared_pdf in SharedPdf.objects.all()}
        self.assertEqual(shared_pdfs_set_after, {shared_pdf_2, shared_pdf_3})
