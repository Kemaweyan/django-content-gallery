import os

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from slugify import UniqueSlugify
from PIL import Image as Img

from . import settings
from . import utils

IMG_W = settings.GALLERY_IMAGE_WIDTH
IMG_H = settings.GALLERY_IMAGE_HEIGHT

THUMB_W = settings.GALLERY_THUMBNAIL_WIDTH
THUMB_H = settings.GALLERY_THUMBNAIL_HEIGHT

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

def _resize(path, size, rename=""):
    img = Img.open(path)
    img.thumbnail(size)
    if rename:
        path = rename
    img.save(path, img.format)    

def _resize_image(path):
    size = (IMG_W, IMG_H)
    _resize(path, size)

def _create_thumbnail(path):
    size = (THUMB_W, THUMB_H)
    thumb_path = utils.create_thumbnail_path(path)
    _resize(path, size, thumb_path)
   

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
        _resize_image(self.src.path)
        _create_thumbnail(self.src.path)


@receiver(pre_delete, sender=Image)
def image_delete(sender, instance, **kwargs):
    thumb_path = utils.create_thumbnail_path(instance.src.path)
    os.remove(thumb_path)
    instance.src.delete(False)
