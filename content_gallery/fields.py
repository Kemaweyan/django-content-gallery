import os

from django.db import models
from django.db.models.fields import files
from django.conf import settings as django_settings

from . import settings
from . import image_data

class GalleryImageFieldFile(files.ImageFieldFile):
    """
    A file wrapper of the field for image files used in the Image model.
    Contains and manages 5 image files with different sizes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # a full-size image
        self.image_data = image_data.InMemoryImageData(
            self,
            settings.CONF['image_width'],
            settings.CONF['image_height'],
        )
        # a small image for displays with low resolution
        self.small_image = image_data.ImageFile(
            self,
            settings.CONF['small_image_width'],
            settings.CONF['small_image_height'],
            'small'
        )
        # a large preview, it's meant to be used on detail views
        self.preview = image_data.ImageFile(
            self,
            settings.CONF['preview_width'],
            settings.CONF['preview_height'],
            'preview'
        )
        # a small preview, it's meant to be used on list views
        self.small_preview = image_data.ImageFile(
            self,
            settings.CONF['small_preview_width'],
            settings.CONF['small_preview_height'],
            'small_preview'
        )
        # a thumbnail, used in the list of available images
        self.thumbnail = image_data.ImageFile(
            self,
            settings.CONF['thumbnail_width'],
            settings.CONF['thumbnail_height'],
            'thumbnail'
        )

    @staticmethod
    def _check_dir():
        """
        Creates a directory for image files if it does not exist.
        """
        path = os.path.join(django_settings.MEDIA_ROOT, settings.CONF['path'])
        if not os.path.isdir(path):
            os.mkdir(path)

    def save_files(self, slug, name):
        """
        Saves image data to the files or renames existing files if the related
        object has been changed and the image file has not been uploaded.
        Since the full-size image is stored in the memory, it is not saved
        into the file but prepared (resized) for saving by parent 'save' method.
        """
        # create the directory first if it does not exist
        self._check_dir()
        self.image_data.save(self, slug, name)
        self.thumbnail.save(self, slug, name)
        self.small_image.save(self, slug, name)
        self.preview.save(self, slug, name)
        self.small_preview.save(self, slug, name)
        # if no image has been uploaded, get the name directly
        if not self.image_data.data:
            self.name = self.image_data.name_in_db

    def save(self, name, content, save=True):
        """
        Saves full-size image data to the file and writes data to database
        using prepared image data and generated file name.
        """
        # get resized image data
        content = self.image_data.data
        # get generated file name
        name = self.image_data.data.name
        super().save(name, content, save)

    def delete_files(self):
        """
        Deletes all image files related to the Image object.
        """
        self.thumbnail.delete()
        self.image_data.delete()
        self.small_image.delete()
        self.preview.delete()
        self.small_preview.delete()

    @property
    def thumbnail_url(self):
        """
        URL to the thumbnail file
        """
        return self.thumbnail.url

    @property
    def image_url(self):
        """
        URL to the full-size image file
        """
        return self.image_data.url

    @property
    def small_image_url(self):
        """
        URL to the small image file
        """
        return self.small_image.url

    @property
    def preview_url(self):
        """
        URL to the preview image file
        """
        return self.preview.url
    # the 'url' property is used by django.forms.ClearableFileInput
    # to display the link to the uploaded image and it contains the link
    # to the full-size image. Override this property with the 'preview' url
    url = preview_url

    @property
    def small_preview_url(self):
        """
        URL to the small preview image file
        """
        return self.small_preview.url


class GalleryImageField(models.ImageField):
    """
    A field for image files used in the Image model.
    """
    attr_class = GalleryImageFieldFile
