import os
from abc import ABCMeta, abstractmethod

from . import utils

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
        return utils.create_path(self.filename)

    @property
    def url(self):
        return utils.create_url(self.filename)

    @abstractmethod
    def _create_image(self, image):
        """Creates an image using data of uploaded file"""

    @abstractmethod
    def _create_filename(self, filename):
        """Creates a name of the file"""

    def _change_ext(self, filename):
        name = utils.get_name(self.name)
        ext = utils.get_ext(filename)
        self.name = name + ext

    def save(self, image, slug, name):
        is_uploaded = '/' not in image.name
        self._set_name(name)
        if is_uploaded and self.name:
            self.delete()
        if slug:
            new_name = slug + utils.get_ext(image.name)
            if self.name and not is_uploaded:
                self._rename_file(new_name)
            self.name = new_name
        if is_uploaded:
            if not slug:
                self._change_ext(image.name)
            self._create_image(image)

    def _rename_file(self, name):
        new_filename = self._create_filename(name)
        new_path = utils.create_path(new_filename)
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
        utils.image_resize(image, self.path, self.size)


class InMemoryImageData(BaseImageData):

    def __init__(self, image, width, height):
        super().__init__(image, width, height)
        self.data = None

    def _create_filename(self, filename):
        return filename

    def _create_image(self, image):
        self.data = utils.create_in_memory_image(image, self.name, self.size)

    @property
    def name_in_db(self):
        return utils.name_in_db(self.name)
