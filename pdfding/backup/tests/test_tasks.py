import logging
import sqlite3
from pathlib import Path
from unittest import mock

from allauth.account.models import EmailAddress
from backup import tasks
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from pdf.models import Pdf, Tag

logger = logging.getLogger('huey')


class TestPeriodicBackup(TestCase):
    mock_objects = []
    for i in range(4, 9):
        mock_object = mock.Mock()
        mock_object.object_name = f'1/pdf_{i}.pdf'
        mock_objects.append(mock_object)
    for i in range(3):
        mock_object = mock.Mock()
        mock_object.object_name = f'2/pdf_{i}{i}.pdf'
        mock_objects.append(mock_object)

    mock_object = mock.Mock()
    mock_object.object_name = 'backup.sqlite3'

    @mock.patch('backup.tasks.Minio.bucket_exists', side_effect=ValueError('some error'))
    def test_backup_function_exception(self, mock_bucket_exists):
        with self.assertLogs(logger) as cm:
            tasks.backup_function()

            expected_logs = [
                'INFO:huey:----------------------------------------------------',
                'INFO:huey:Backup is being started',
                'ERROR:huey:There was an error during the backup: "ValueError(\'some ' 'error\')"!',
                'ERROR:huey:Backup aborted!',
                'INFO:huey:----------------------------------------------------',
            ]

            self.assertListEqual(cm.output, expected_logs)

    @mock.patch('backup.tasks.difference_local_minio', return_value=({'add_1.pdf', 'add_2.pdf'}, {'remove.pdf'}))
    @mock.patch('backup.tasks.Minio.fput_object')
    @mock.patch('backup.tasks.Minio.make_bucket')
    @mock.patch('backup.tasks.Minio.bucket_exists', return_value=False)
    def test_backup_function(self, mock_bucket_exists, mock_make_bucket, mock_fput_object, mock_difference_local_minio):
        tasks.backup_function()

        mock_make_bucket.assert_called_with('pdfding')
        mock_bucket_exists.assert_called_with('pdfding')
        self.assertEqual(mock_fput_object.call_count, 3)
        mock_fput_object.assert_has_calls(
            [
                mock.call('pdfding', 'backup.sqlite3', Path(__file__).parents[2] / 'db' / 'backup.sqlite3'),
                mock.call('pdfding', 'add_1.pdf', Path(__file__).parents[2] / 'media' / 'add_1.pdf'),
                mock.call('pdfding', 'add_2.pdf', Path(__file__).parents[2] / 'media' / 'add_2.pdf'),
            ],
            any_order=True,
        )

    def test_parse_cron_schedule(self):
        expected_dict = {'minute': '3', 'hour': '*/2', 'day': '6', 'month': '7', 'day_of_week': '*'}
        generated_dict = tasks.parse_cron_schedule('3 */2 6 7 *')

        self.assertEqual(expected_dict, generated_dict)

    @mock.patch('backup.tasks.Minio.list_objects', return_value=mock_objects)
    def test_difference_local_minio(self, mock_list_objects):
        user_1 = User.objects.create_user(username='user_1', password='password', email='a@a.com')
        user_2 = User.objects.create_user(username='user_2', password='password', email='b@a.com')

        for i in range(1, 7):
            pdf = Pdf.objects.create(owner=user_1.profile, name=f'pdf_{i}.pdf')
            pdf.file.name = f'{pdf.owner.id}/{pdf.name}'
            pdf.save()
        for i in range(2, 4):
            pdf = Pdf.objects.create(owner=user_2.profile, name=f'pdf_{i}{i}.pdf')
            pdf.file.name = f'{pdf.owner.id}/{pdf.name}'
            pdf.save()

        generated_to_be_added, generated_to_be_deleted = tasks.difference_local_minio()
        expected_to_be_added = {'1/pdf_1.pdf', '1/pdf_2.pdf', '1/pdf_3.pdf', '2/pdf_33.pdf'}
        expected_to_be_deleted = {'1/pdf_7.pdf', '1/pdf_8.pdf', '2/pdf_00.pdf', '2/pdf_11.pdf'}

        self.assertEqual(expected_to_be_added, generated_to_be_added)
        self.assertEqual(expected_to_be_deleted, generated_to_be_deleted)


class TestSqliteBackup(TestCase):
    username = 'user'
    password = '12345'

    def setUp(self):
        for i in range(1, 4):
            user = User.objects.create_user(username=i, password='password', email=f'{i}@a.com')

            EmailAddress.objects.get_primary(user)
            # save in order to add email
            user.save()

            for j in range(1, i + 1):
                pdf = Pdf.objects.create(owner=user.profile, name=f'pdf_{j}')
                tags = [Tag.objects.create(name=f'pdf_{j}_tag_{k}', owner=pdf.owner) for k in range(2)]
                pdf.tags.set(tags)

    def test_backup_sqlite(self):
        test_db_path = settings.BASE_DIR / 'db' / 'test.sqlite3'
        backup_db_path = settings.BASE_DIR / 'db' / 'test_backup.sqlite3'

        tasks.backup_sqlite(test_db_path, backup_db_path)

        # check if the important tables are the same
        for table in ['account_emailaddress', 'auth_user', 'pdf_pdf_tags', 'sqlite_sequence', 'users_profile']:
            if table != 'sqlite_sequence':
                table_compare = f'SELECT * FROM {table} order by id'
            else:
                table_compare = f'SELECT * FROM {table} order by name'

            conn1 = sqlite3.connect(test_db_path)
            conn2 = sqlite3.connect(backup_db_path)
            cursor1 = conn1.cursor()
            cursor2 = conn2.cursor()
            result1 = cursor1.execute(table_compare).fetchall()
            result2 = cursor2.execute(table_compare).fetchall()

            self.assertEqual(result1, result2)

        backup_db_path.unlink()
