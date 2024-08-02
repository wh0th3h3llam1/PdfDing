from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.test import TestCase


class TestRecoverData(
    TestCase,
):
    mock_object_1 = mock.Mock()
    mock_object_1.object_name = 'pdf_1.pdf'
    mock_object_2 = mock.Mock()
    mock_object_2.object_name = 'backup.sqlite3'

    mock_objects = [mock_object_1, mock_object_2]

    @mock.patch('backup.tasks.Minio.list_objects', return_value=mock_objects)
    @mock.patch('backup.tasks.Minio.fget_object')
    @mock.patch('builtins.input', return_value='y')
    def test_recover_data(self, mock_input, mock_fget_object, mock_list_objects):
        call_command('recover_data')

        self.assertEqual(mock_fget_object.call_count, 2)
        mock_fget_object.assert_has_calls(
            [
                mock.call('pdfding', 'backup.sqlite3', Path(__file__).parents[2] / 'db' / 'test.sqlite3'),
                mock.call('pdfding', 'pdf_1.pdf', Path(__file__).parents[2] / 'media' / 'pdf_1.pdf'),
            ],
        )
