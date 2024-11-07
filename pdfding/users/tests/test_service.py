import users.service as service
from django.test import TestCase


class TestUserServices(TestCase):
    def test_clean_custom_theme_color_correct(self):
        self.assertEqual(service.convert_hex_to_rgb('#FFB3A5'), (255, 179, 165))
        self.assertEqual(service.convert_hex_to_rgb('ffb3a5'), (255, 179, 165))

    def test_convert_rgb_to_hex(self):
        self.assertEqual(service.convert_rgb_to_hex(255, 179, 165), '#ffb3a5')

    def test_get_color_shades(self):
        self.assertEqual(service.get_color_shades('#b5edff'), ('#91becc', '#6d8e99', '#d3f4ff'))
