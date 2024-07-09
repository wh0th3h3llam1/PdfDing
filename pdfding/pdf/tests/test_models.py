from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from unittest.mock import patch

import pdf.models as models


class TestModels(TestCase):
    @staticmethod
    def create_pdf(username='testuser', password='12345'):
        user = User.objects.create_user(username=username, password=password)
        pdf = models.Pdf(owner=user.profile, name='pdf')

        return pdf

    def test_parse_tag_string(self):
        input_tag_str = '#Tag1  ###tag2      tag3 tag4'
        expected_tags = ['tag1', 'tag2', 'tag3', 'tag4']
        generated_tags = models.Tag.parse_tag_string(input_tag_str)

        self.assertEqual(expected_tags, generated_tags)

    def test_parse_tag_string_empty(self):
        generated_tags = models.Tag.parse_tag_string('')

        self.assertEqual([], generated_tags)

    @patch('pdf.models.uuid4', return_value='uuid')
    def test_get_file_path(self, mock_uuid4):
        pdf = self.create_pdf()
        generated_filepath = models.get_file_path(pdf, '')

        self.assertEqual(generated_filepath, '1/uuid.pdf')

    def test_natural_age(self):
        pdf = self.create_pdf()
        pdf.creation_date = datetime.now() - timedelta(minutes=5)
        self.assertEqual(pdf.natural_age, '5 minutes')

        pdf.creation_date -= timedelta(days=3, hours=2)
        self.assertEqual(pdf.natural_age, '3 days')
