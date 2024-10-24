from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pdf.service as service
from django.contrib.auth.models import User
from django.http.response import Http404
from django.test import TestCase
from pdf.models import Pdf, Tag


class TestService(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='username', password='password', email='a@a.com')

    def test_process_tag_names(self):
        Tag.objects.create(name='existing', owner=self.user.profile)

        tag_names = ['existing', 'generated']
        tags = service.process_tag_names(tag_names, self.user.profile)

        for tag, tag_name in zip(tags, tag_names):
            self.assertEqual(tag.name, tag_name)

        # check if new tag was generated with correct owner
        self.assertEqual(tags[1].owner, self.user.profile)

    def test_process_tag_names_empty(self):
        tags = service.process_tag_names([], self.user.profile)

        self.assertEqual(tags, [])

    def test_process_raw_search_query(self):
        input_str_list = ['#tag_1 #tag_2 search_str_1 search_str_2', '#tag_1 #', 'search_str_1', '']
        expected_search_list = ['search_str_1 search_str_2', '', 'search_str_1', '']
        expected_tags_list = [['tag_1', 'tag_2'], ['tag_1'], [], []]

        for input_str, expected_search, expected_tags in zip(input_str_list, expected_search_list, expected_tags_list):
            generated_search, generated_tags = service.process_raw_search_query(input_str)
            self.assertEqual(generated_search, expected_search)
            self.assertEqual(generated_tags, expected_tags)

    def test_get_tag_dict(self):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf_1')
        tags = [
            Tag.objects.create(name=tag_name, owner=pdf.owner) for tag_name in ['tag3', 'bread', 'tag1', 'banana', 'a']
        ]
        pdf.tags.set(tags)

        expected_tag_dict = {'a': [''], 'b': ['anana', 'read'], 't': ['ag1', 'ag3']}
        generated_tag_dict = service.get_tag_dict(self.user.profile)

        self.assertEqual(expected_tag_dict, generated_tag_dict)

        # make sure first characters are sorted correctly
        self.assertEqual(['a', 'b', 't'], list(generated_tag_dict.keys()))

    @staticmethod
    @service.check_object_access_allowed
    def get_object(pdf_id: str, user: User):
        user_profile = user.profile
        pdf = user_profile.pdf_set.get(id=pdf_id)

        return pdf

    def test_check_object_access_allowed_existing(self):
        pdf = Pdf.objects.create(owner=self.user.profile, name='pdf')

        self.assertEqual(pdf, self.get_object(pdf.id, self.user))

    def test_check_object_access_allowed_validation(self):
        with self.assertRaises(Http404):
            self.get_object('12345', self.user)

    def test_check_object_access_allowed_does_not_exist(self):
        with self.assertRaises(Http404):
            self.get_object(str(uuid4()), self.user)

    def test_get_future_datetime(self):
        expected_result = datetime.now(timezone.utc) + timedelta(days=1, hours=0, minutes=22)
        generated_result = service.get_future_datetime('1d0h22m')

        self.assertTrue((generated_result - expected_result).total_seconds() < 0.1)

    def test_get_future_datetime_empty(self):
        self.assertEqual(service.get_future_datetime(''), None)
