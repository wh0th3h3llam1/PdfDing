from uuid import uuid4

from django.db import models
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.templatetags.static import static

from core.settings import MEDIA_ROOT
from users.models import Profile


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50, null=True, blank=False)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

    @staticmethod
    def parse_tag_string(tag_string: str):
        if not tag_string:
            return []
        names = tag_string.strip().split(' ')
        # remove empty names, sanitize remaining names
        names = [name.strip() for name in names if name]
        # remove duplicates
        names = [name.lower() for name in set(names)]

        return names


def get_file_path(instance, _):
    file_name = f'{uuid4()}.pdf'
    file_path = '/'.join([str(instance.owner.user.id), file_name])

    return str(file_path)


class Pdf(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=False)
    file = models.FileField(upload_to=get_file_path)
    description = models.TextField(null=True, blank=True, help_text='Optional')
    creation_date = models.DateTimeField(blank=False, editable=False, auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.name

    @property
    def now(self):
        natural_time = naturaltime(self.creation_date)

        return natural_time.split(sep=',')[0]
