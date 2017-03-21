import os

import PIL

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from slugify import UniqueSlugify

from . import utils
from . import settings

def _unique_slug_check(slug, uids):
    slug = utils.create_db_slug(slug)
    return not Image.objects.filter(image__startswith=slug)

slugify_unique = UniqueSlugify(unique_check=_unique_slug_check, to_lower=True)


class ImageQuerySet(models.QuerySet):

    def delete(self):
        for obj in self:
            obj.delete_files()
        return super().delete()


class ImageManager(models.Manager):

    def get_queryset(self):
        return ImageQuerySet(self.model, using=self._db)
   

class Image(models.Model):
    image = models.ImageField(upload_to=settings.GALLERY_PATH)
    position = models.IntegerField(default=0, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = ImageManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._get_names()

    def __str__(self):
        return '{} photo #{}'.format(self.content_object, self.position)

    def _get_position(self):
        images = Image.objects.filter(
            content_type__exact=self.content_type,
            object_id__exact=self.object_id
        ).order_by('-position')
        if images:
            self.position = images[0].position + 1

    def _create_file_name(self, word):
        return "{}_{}{}".format(self.slug, word, self.ext)

    @property
    def image_name(self):
        return utils.get_basename(self.image.name)

    def _set_image_name(self):
        self.image.name = ''.join([self.slug, self.ext])

    @property
    def thumbnail_name(self):
        return self._create_file_name('thumbnail')

    @property
    def large_image_name(self):
        return self._create_file_name('large')

    @property
    def image_path(self):
        return utils.create_path(self.image_name)

    @property
    def thumbnail_path(self):
        return utils.create_path(self.thumbnail_name)

    @property
    def large_image_path(self):
        return utils.create_path(self.large_image_name)

    @property
    def image_url(self):
        return utils.create_url(self.image_name)

    @property
    def thumbnail_url(self):
        return utils.create_url(self.thumbnail_name)

    @property
    def large_image_url(self):
        return utils.create_url(self.large_image_name)

    def _create_names(self):
        title = str(self.content_object)
        self.slug = slugify_unique(title)
        self.ext = utils.get_file_ext(self.image_name)
        self._set_image_name()

    def _get_names(self, image=None):
        if image:
            obj = image
        else:
            obj = self
        self.slug = utils.get_file_name(obj.image_name)
        self.ext = utils.get_file_ext(self.image_name)
        if image:
            self._set_image_name()

    def _object_changed(self, image):
        return self.content_type != image.content_type \
            or self.object_id != image.object_id

    def _is_uploaded(self, image):
        return self.image.path != image.image.path

    def save(self, *args, **kwargs):
        if not self.pk:
            self._get_position()
            self._create_names()
            self._create_images()
        else:
            old_image = Image.objects.get(pk=self.pk)
            is_uploaded = self._is_uploaded(old_image)
            if self._object_changed(old_image):
                self._create_names()
                if not is_uploaded:
                    self._rename_files(old_image)
            else:
                self._get_names(old_image)
            if is_uploaded:
                old_image.delete_files()
                self._create_images()
        super().save(*args, **kwargs)

    def _create_images(self):
        utils.create_thumbnail(self.image, self.thumbnail_path)
        utils.create_large_image(self.image, self.large_image_path)
        self.image = utils.resize_image(self.image)

    def _rename_files(self, old_image):
        old_image._get_names()
        utils.safe_rename(old_image.image_path, self.image_path)
        utils.safe_rename(old_image.thumbnail_path, self.thumbnail_path)
        utils.safe_rename(old_image.large_image_path, self.large_image_path)

    def delete_files(self):
        self._get_names()
        utils.safe_delete(self.thumbnail_path)
        utils.safe_delete(self.large_image_path)
        utils.safe_delete(self.image_path)

    def delete(self, *args, **kwargs):
        self.delete_files()
        return super().delete(*args, **kwargs)
