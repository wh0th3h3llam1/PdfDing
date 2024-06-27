from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_delete
from pdf.models import Pdf


@receiver(pre_delete, sender=Pdf)
def delete_orphan_tag(sender, instance, **kwargs):
    pdf = instance

    for tag in pdf.tags.all():
        # if only one pdf is  associated with the tag it is the one being deleted
        # in that case the tag should be deleted
        if tag.pdf_set.count() == 1:
            tag.delete()
