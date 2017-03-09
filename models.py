import os

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from slugify import UniqueSlugify

def _make_src(slug, filename=''):
    if filename and '.' in filename:
        ext = filename.split('.')[-1]
        src = "{}.{}".format(slug, ext)
    else:
        src = slug
    return os.path.join('gallery', src)

def _unique_src_check(slug, uids):
    if slug in uids:
        return False
    src = _make_src(slug)
    return not Image.objects.filter(src__startswith=src)

slugify_unique = UniqueSlugify(unique_check=_unique_src_check, to_lower=True)

def _upload_rename(instance, filename):
    title = str(instance.content_object)
    slug = slugify_unique(title)
    src = _make_src(slug, filename)
    return src

class Image(models.Model):
    src = models.ImageField(upload_to=_upload_rename)
    position = models.IntegerField(db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return '{} photo #{}'.format(self.content_object, self.position)


@receiver(pre_delete, sender=Image)
def image_delete(sender, instance, **kwargs):
    instance.src.delete(False)
