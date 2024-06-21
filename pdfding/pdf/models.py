from django.db import models
from django.templatetags.static import static

from users.models import Profile 


class Tag(models.Model):
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


class Pdf(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=False)
    filename = models.CharField(max_length=50, null=True, blank=False)
    description = models.TextField(null=True, blank=True, help_text='Optional')
    creation_date = models.DateField(blank=False, editable=False, auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    def __str__(self):
        return self.name
    
