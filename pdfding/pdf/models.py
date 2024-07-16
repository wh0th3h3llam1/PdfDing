from uuid import uuid4

from django.db import models
from django.contrib.humanize.templatetags.humanize import naturaltime

from users.models import Profile


class Tag(models.Model):
    """The model for the tags used for organizing PDF files."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50, null=True, blank=False)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):  # pragma: no cover
        return str(self.name)

    @staticmethod
    def parse_tag_string(tag_string: str):
        if not tag_string:
            return []

        names = tag_string.strip().split(' ')
        # remove empty names, sanitize remaining names
        names = [name.strip() for name in names if name]
        # remove duplicates
        names = [name.replace('#', '').lower() for name in set(names)]

        return sorted(names)


def get_file_path(instance, _):
    """Get the file path for a PDF by generating a UUID and using the user id. File paths are user_id/<uuid>.pdf"""

    file_name = f'{uuid4()}.pdf'
    file_path = '/'.join([str(instance.owner.user.id), file_name])

    return str(file_path)


class Pdf(models.Model):
    """Model for the pdf files."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=False)
    name = models.CharField(max_length=50, null=True, blank=False)
    file = models.FileField(upload_to=get_file_path, blank=False)
    description = models.TextField(null=True, blank=True, help_text='Optional')
    creation_date = models.DateTimeField(blank=False, editable=False, auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True)
    current_page = models.IntegerField(default=1)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.name  # pragma: no cover

    @property
    def natural_age(self) -> str:
        """
        Get the natural age of a file. This converts the creation date to a natural age,
        e.g: 2 minutes, 1 hour,  2 months, etc
        """

        natural_time = naturaltime(self.creation_date)

        if ',' in natural_time:
            natural_time = natural_time.split(sep=', ')[0]
        else:
            natural_time = natural_time.replace(' ago', '')

        # naturaltime will include space characters that will cause failed unit tests
        # splitting and joining fixes that
        return ' '.join(natural_time.split())
