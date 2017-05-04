from django.db import models
from django.db.models.fields import files

from . import settings
from . import image_files

# the size of image
IMG_W = settings.GALLERY_IMAGE_WIDTH
IMG_H = settings.GALLERY_IMAGE_HEIGHT

# the size of small image
SMALL_W = settings.GALLERY_SMALL_IMAGE_WIDTH
SMALL_H = settings.GALLERY_SMALL_IMAGE_HEIGHT

# the size of thumbnail
THUMB_W = settings.GALLERY_THUMBNAIL_WIDTH
THUMB_H = settings.GALLERY_THUMBNAIL_HEIGHT

# the size of preview
PREVIEW_W = settings.GALLERY_PREVIEW_WIDTH
PREVIEW_H = settings.GALLERY_PREVIEW_HEIGHT

# the size of small preview
SMALL_PREVIEW_W = settings.GALLERY_SMALL_PREVIEW_WIDTH
SMALL_PREVIEW_H = settings.GALLERY_SMALL_PREVIEW_HEIGHT

class GalleryImageFieldFile(files.ImageFieldFile):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thumbnail = image_files.ImageFile(self, THUMB_W, THUMB_H,
            'thumbnail')
        self.image_data = image_files.InMemoryImageData(self, IMG_W, IMG_H)
        self.small_image = image_files.ImageFile(self, SMALL_W, SMALL_H,
            'small')
        self.preview = image_files.ImageFile(self, PREVIEW_W, PREVIEW_H,
            'preview')
        self.small_preview = image_files.ImageFile(self, SMALL_PREVIEW_W,
            SMALL_PREVIEW_H, 'small_preview')

    def save_files(self, slug, name):
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
