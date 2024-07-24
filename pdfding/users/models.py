from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static


class Profile(models.Model):
    """The user profile model of PdfDing"""

    class DarkMode(models.TextChoices):
        LIGHT = 'Light'
        DARK = 'Dark'

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

    def __str__(self):  # pragma: no cover
        return str(self.user.email)
