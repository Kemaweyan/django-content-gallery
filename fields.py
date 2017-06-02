import os

from django.db import models
from django.db.models.fields import files
from django.conf import settings as django_settings

from . import settings
from . import image_data

class GalleryImageFieldFile(files.ImageFieldFile):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_data = image_data.InMemoryImageData(
            self,
            settings.CONF['image_width'],
            settings.CONF['image_height'],
        )
        self.small_image = image_data.ImageFile(
            self,
            settings.CONF['small_image_width'],
            settings.CONF['small_image_height'],
            'small'
        )
        self.preview = image_data.ImageFile(
            self,
            settings.CONF['preview_width'],
            settings.CONF['preview_height'],
            'preview'
        )
        self.small_preview = image_data.ImageFile(
            self,
            settings.CONF['small_preview_width'],
            settings.CONF['small_preview_height'],
            'small_preview'
        )
        self.thumbnail = image_data.ImageFile(
            self,
            settings.CONF['thumbnail_width'],
            settings.CONF['thumbnail_height'],
            'thumbnail'
        )

    @staticmethod
    def _check_dir():
        path = os.path.join(django_settings.MEDIA_ROOT, settings.CONF['path'])
        if not os.path.isdir(path):
            os.mkdir(path)

    def save_files(self, slug, name):
        self._check_dir()
        self.image_data.save(self, slug, name)
        self.thumbnail.save(self, slug, name)
        self.small_image.save(self, slug, name)
        self.preview.save(self, slug, name)
        self.small_preview.save(self, slug, name)
        if not self.image_data.data:
            self.name = self.image_data.name_in_db

    def save(self, name, content, save=True):
        content = self.image_data.data
        name = self.image_data.data.name
        super().save(name, content, save)

    def delete_files(self):
        self.thumbnail.delete()
        self.image_data.delete()
        self.small_image.delete()
        self.preview.delete()
        self.small_preview.delete()

    @property
    def thumbnail_url(self):
        return self.thumbnail.url

    @property
    def image_url(self):
        return self.image_data.url

    @property
    def small_image_url(self):
        return self.small_image.url

    @property
    def preview_url(self):
        return self.preview.url
    url = preview_url

    @property
    def small_preview_url(self):
        return self.small_preview.url


class GalleryImageField(models.ImageField):
    attr_class = GalleryImageFieldFile
