import os

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from slugify import UniqueSlugify

from . import utils

def _unique_src_check(slug, uids):
    if slug in uids:
        return False
    src = utils.make_src(slug)
    return not Image.objects.filter(src__startswith=src)

slugify_unique = UniqueSlugify(unique_check=_unique_src_check, to_lower=True)

def _upload_rename(instance, filename):
    title = str(instance.content_object)
    slug = slugify_unique(title)
    src = utils.make_src(slug, filename)
    return src
   

class Image(models.Model):
    src = models.ImageField(upload_to=_upload_rename)
    position = models.IntegerField(default=0, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return '{} photo #{}'.format(self.content_object, self.position)

    def save(self, *args, **kwargs):
        if not self.pk:
            images = Image.objects.filter(
                content_type__exact=self.content_type,
                object_id__exact=self.object_id
            ).order_by('-position')
            if images:
                self.position = images[0].position + 1
        super().save(*args, **kwargs)
        utils.resize_image(self.src.path)
        utils.create_thumbnail(self.src.path)


@receiver(pre_delete, sender=Image)
def image_delete(sender, instance, **kwargs):
    thumb_path = utils.create_thumbnail_path(instance.src.path)
    try:
        os.remove(thumb_path)
    except FileNotFoundError:
        pass
    instance.src.delete(False)
