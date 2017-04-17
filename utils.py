import sys
import os
import re
import io
from PIL import Image
import magic
from abc import ABCMeta, abstractmethod

from django.core import urlresolvers as ur
from django.core.files import uploadedfile as uf

from . import settings

def get_choices_url_pattern():
    """
    Returns the pattern of URL for getting product choices
    via AJAX in JS code.
    """
    # get 'choices' URL with any id
    choices_url = ur.reverse('gallery:choices', args=(0,))
    # remove id (last digits in the URL)
    return re.sub(r'\d+$', '', choices_url)

def calculate_image_size(size, max_size):
    # copied from PIL.Image.thumbnail
    x, y = size
    if x > max_size[0]:
        y = int(max(y * max_size[0] / x, 1))
        x = int(max_size[0])
    if y > max_size[1]:
        x = int(max(x * max_size[1] / y, 1))
        y = int(max_size[1])
    return x, y

def get_ext(filename):
    name, ext = os.path.splitext(filename)
    return ext

def get_name(filename):
    name, ext = os.path.splitext(filename)
    return name

def create_path(filename):
    return os.path.join(settings.MEDIA_ROOT, settings.GALLERY_PATH, filename)

def create_url(filename):
    media_url = settings.MEDIA_URL.rstrip('/')
    gallery_path = settings.GALLERY_PATH.strip('/')
    return '/'.join([media_url, gallery_path, filename])

def name_in_db(name):
    return os.path.join(settings.GALLERY_PATH, name)


class BaseImageData(metaclass=ABCMeta):

    def __init__(self, image, width, height):
        self._set_name(image.name)
        self.size = (width, height)

    def _set_name(self, name):
        self.name = os.path.basename(name)

    @property
    def filename(self):
        return self._create_filename(self.name)

    @property
    def path(self):
        return create_path(self.filename)

    @property
    def url(self):
        return create_url(self.filename)

    def _resize(self, src, dst):
        img = Image.open(src)
        img.thumbnail(self.size)
        img.save(dst, img.format)

    @abstractmethod
    def _create_image(self, image):
        pass

    @abstractmethod
    def _create_filename(self, filename):
        pass

    def _change_ext(self, filename):
        name = get_name(self.name)
        ext = get_ext(filename)
        self.name = name + ext

    def save(self, image, slug, name):
        is_uploaded = '/' not in image.name
        self._set_name(name)
        if is_uploaded and self.name:
            self.delete()
        if slug:
            new_name = slug + get_ext(image.name)
            if self.name and not is_uploaded:
                self._rename_file(new_name)
            self.name = new_name
        if is_uploaded:
            if not slug:
                self._change_ext(image.name)
            self._create_image(image)

    def _rename_file(self, name):
        new_filename = self._create_filename(name)
        new_path = create_path(new_filename)
        os.rename(self.path, new_path)

    def delete(self):
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass


class ImageFile(BaseImageData):

    def __init__(self, image, width, height, word):
        self.word = word
        super().__init__(image, width, height)

    def _create_filename(self, filename):
        name, ext = os.path.splitext(filename)
        return "{}_{}{}".format(name, self.word, ext)

    def _create_image(self, image):
        self._resize(image, self.path)


class InMemoryImageData(BaseImageData):

    def __init__(self, image, width, height):
        super().__init__(image, width, height)
        self.data = None

    def _create_filename(self, filename):
        return filename

    def _create_image(self, image):
        output = io.BytesIO()
        self._resize(image, output)
        mime = magic.from_buffer(output.getvalue(), mime=True)
        self.data = uf.InMemoryUploadedFile(output, 'ImageField', self.name,
            mime, sys.getsizeof(output), None)

    @property
    def name_in_db(self):
        return name_in_db(self.name)
