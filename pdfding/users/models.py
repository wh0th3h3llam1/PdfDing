from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """The user profile model of PdfDing"""

    class DarkMode(models.TextChoices):
        LIGHT = 'Light'
        DARK = 'Dark'

    class PdfsPerPage(models.IntegerChoices):
        p_5 = 5, '5'
        p_10 = 10, '10'
        p_25 = 25, '25'
        p_50 = 50, '50'
        p_100 = 100, '100'

    class ThemeColor(models.TextChoices):
        GREEN = 'Green'
        BLUE = 'Blue'
        GRAY = 'Gray'
        RED = 'Red'
        PINK = 'Pink'
        ORANGE = 'Orange'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dark_mode = models.CharField(choices=DarkMode.choices, max_length=5, default=DarkMode.LIGHT)
    theme_color = models.CharField(choices=ThemeColor.choices, max_length=6, default=ThemeColor.GREEN)
    pdfs_per_page = models.IntegerField(choices=PdfsPerPage.choices, default=PdfsPerPage.p_25)

    def __str__(self):  # pragma: no cover
        return str(self.user.email)
