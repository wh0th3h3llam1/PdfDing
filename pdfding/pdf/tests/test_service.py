from django.contrib.auth.models import User
from django.test import TestCase

import pdf.service as service
from pdf.models import Tag


class TestService(TestCase):
    @staticmethod
    def create_user(username='testuser', password='12345'):
        user = User.objects.create_user(username=username, password=password)

        return user

    def test_process_tag_names(self):
        user = self.create_user()

        Tag.objects.create(name='existing', owner=user.profile)

        tag_names = ['existing', 'generated']
        tags = service.process_tag_names(tag_names, user.profile)

        for tag, tag_name in zip(tags, tag_names):
            self.assertEqual(tag.name, tag_name)

        # check if new tag was generated with correct owner
        self.assertEqual(tags[1].owner, user.profile)

    def test_process_tag_names_empty(self):
        user = self.create_user()

        tags = service.process_tag_names([], user.profile)

        self.assertEqual(tags, [])

    def test_process_raw_search_query(self):
        input_str_list = ['#tag_1 #tag_2 search_str_1 search_str_2', '#tag_1 #', 'search_str_1', '']
        expected_search_list = ['search_str_1 search_str_2', '', 'search_str_1', '']
        expected_tags_list = [['tag_1', 'tag_2'], ['tag_1'], [], []]

        for input_str, expected_search, expected_tags in zip(input_str_list, expected_search_list, expected_tags_list):
            generated_search, generated_tags = service.process_raw_search_query(input_str)
            self.assertEqual(generated_search, expected_search)
            self.assertEqual(generated_tags, expected_tags)
