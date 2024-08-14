from unittest.mock import Mock, patch

from admin.service import get_latest_version
from django.test import TestCase


class TestService(TestCase):
    mock_response = Mock()
    mock_response.json = lambda: {'tag_name': '0.0.0'}

    @patch('admin.service.requests.get', return_value=mock_response)
    def test_get_latest_version(self, mock_get):
        generated_tag = get_latest_version()

        self.assertEqual(generated_tag, '0.0.0')
