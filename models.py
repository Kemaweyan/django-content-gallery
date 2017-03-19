import os

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from slugify import UniqueSlugify

from . import utils

def _unique_src_check(slug, uids):
    if slug in uids:
        return False
    src = utils.make_src(slug)
    return not Image.objects.filter(image__startswith=src)

slugify_unique = UniqueSlugify(unique_check=_unique_src_check, to_lower=True)

def _upload_rename(instance, filename):
    title = str(instance.content_object)
    slug = slugify_unique(title)
    src = utils.make_src(slug, filename)
    return src


class ImageQuerySet(models.QuerySet):

    def delete(self):
        for obj in self:
            obj.delete_files()
        return super().delete()


class ImageManager(models.Manager):

    def get_queryset(self):
        return ImageQuerySet(self.model, using=self._db)
   

class Image(models.Model):
    image = models.ImageField(upload_to=_upload_rename)
    position = models.IntegerField(default=0, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = ImageManager()

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
        else:
            image = Image.objects.get(pk=self.pk)
            if self.image.path != image.image.path:
                image.delete_files()
        super().save(*args, **kwargs)
        utils.resize_image(self.image.path)
        utils.create_thumbnail(self.image.path)

    def delete_files(self):
        utils.delete_thumbnail(self.image.path)
        self.image.delete(False)

    def delete(self, *args, **kwargs):
        self.delete_files()
        return super().delete(*args, **kwargs)

    @property
    def thumbnail(self):
        return utils.create_thumbnail_path(self.image.url)
