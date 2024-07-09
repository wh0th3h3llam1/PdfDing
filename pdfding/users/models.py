from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static


class Profile(models.Model):
    """The user profile model of PdfDing"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):  # pragma: no cover
        return str(self.user.email)

    @property
    def avatar(self):  # pragma: no cover
        """Returns the path to the avatar image"""

        return static("images/avatar.png")
