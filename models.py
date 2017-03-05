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
    position = models.IntegerField(db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


@receiver(pre_delete, sender=Image)
def mymodel_delete(sender, instance, **kwargs):
    instance.src.delete(False)
