import os
from abc import ABCMeta, abstractmethod

from . import utils

class BaseImageData(metaclass=ABCMeta):
    """
    An abstract base class for image files and in memory
    stored image data. Implements common methods.
    """

    def __init__(self, image, width, height):
        # save the name and the size of the image
        self._set_name(image.name)
        self.size = (width, height)

    def _set_name(self, name):
        """
        Sets the name of the image file excluding the path
        """
        self.name = os.path.basename(name)

    @property
    def filename(self):
        """
        Returns the file name of the image
        """
        return self._create_filename(self.name)

    @property
    def path(self):
        """
        Returns the path to the image
        """
        return utils.create_path(self.filename)

    @property
    def url(self):
        """
        Returns the URL to the image
        """
        return utils.create_url(self.filename)

    @abstractmethod
    def _create_image(self, image):
        """Creates an image using data of uploaded file"""

    @abstractmethod
    def _create_filename(self, filename):
        """Creates a name of the file"""

    def _change_ext(self, filename):
        """
        Changes the ext in the file name to the ext
        of given file name.
        """
        name = utils.get_name(self.name)
        ext = utils.get_ext(filename)
        self.name = name + ext

    def save(self, image, slug, name):
        """
        Saves changes of the Image object: saves new image data
        and/or renames the file. 'image' contains the image
        field file (uploaded or read from the database),
        'slug' is a new name of the image or empty string if
        the related object has not changed. 'name' is the former
        name of the image and used when the related object has not
        changed but a new image file has been uploaded.
        """
        # check whether there is a new uploaded image
        # uploaded files have not '/' in the file name
        # but while saving to the database the ImageField
        # adds path to the file name
        is_uploaded = '/' not in image.name
        # overwrite the name with old one since if there is uploaded
        # file the self.name would contain its original file name
        # it will be overwritten if slug specified, it happens when
        # a new image object is created or the related object changed
        self._set_name(name)
        if is_uploaded and name:
            # delete the old file if it exists
            # and a new image has been uploaded
            self.delete()
        if slug:
            # if new name required create it using
            # the slug and the ext of actual image file
            new_name = slug + utils.get_ext(image.name)
            if self.name and not is_uploaded:
                # no new file has been uploaded
                # so just rename existing file
                self._rename_file(new_name)
            # set a new name
            self.name = new_name
        # when a new file has been uploaded
        if is_uploaded:
            # if the slug is specified the file name is already correct
            if not slug:
                # change the ext of existing file name
                # if the related object has not changed
                self._change_ext(image.name)
            # resize and save the image data
            self._create_image(image)

    def _rename_file(self, name):
        """
        Renames the image file
        """
        # create a filename depending of implementation
        new_filename = self._create_filename(name)
        # get the path
        new_path = utils.create_path(new_filename)
        os.rename(self.path, new_path)

    def delete(self):
        """
        Deletes the iamge file if it exists
        """
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass


class ImageFile(BaseImageData):
    """
    An image file object used for all images
    except the full-size image. Saves the image data
    into the files directly.
    """

    def __init__(self, image, width, height, suffix):
        # store the suffix word used in the file name
        self.suffix = suffix
        super().__init__(image, width, height)

    def _create_filename(self, filename):
        """
        Inserts the suffix word separated with underscore 
        in the end of the file name and returns it.
        """
        name, ext = os.path.splitext(filename)
        return "{}_{}{}".format(name, self.suffix, ext)

    def _create_image(self, image):
        """
        Resizes the image and saves it into the file.
        """
        utils.image_resize(image, self.path, self.size)


class InMemoryImageData(BaseImageData):
    """
    A stored in memory image data object used for
    the full-size image. Saved the image data in the memory
    before the GalleryImageFieldFile saves it to the file.
    """

    def __init__(self, image, width, height):
        super().__init__(image, width, height)
        # set empty data attribute
        self.data = None

    def _create_filename(self, filename):
        """
        The full-size image does not need any suffixes
        and uses just simple slug as the file name.
        """
        return filename

    def _create_image(self, image):
        """
        Resizes the image and saves resized image data
        as the 'data' attribute.
        """
        self.data = utils.create_in_memory_image(image, self.name, self.size)

    @property
    def name_in_db(self):
        """
        Simulates the transformation of the file name
        after saving the image object into the database.
        The transformation is adding the path.
        """
        return utils.name_in_db(self.name)
