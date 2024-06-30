from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static


class Profile(models.Model):
    """The user profile model of PdfDing"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    displayname = models.CharField(max_length=20, null=True, blank=True)
    info = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.user.email)

    @property
    def avatar(self):
        """Returns the path to the avatar image"""

        return static("images/avatar.png")
