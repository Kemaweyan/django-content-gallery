import sys
from io import BytesIO
from contextlib import contextmanager
from PIL import Image

from django.core.files.uploadedfile import InMemoryUploadedFile

from .. import settings
from .. import models

from .models import *

def get_image_data():
    """
    Returns the BytesIO object containing an Image data
    """
    io = BytesIO()
    # create filled with red color image 200x200 px
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGB", size, color)
    # save the image data in JPEG format to the io buffer
    image.save(io, format='JPEG')
    io.seek(0)  # seek to the beginning
    return io

def get_image_in_memory_data():
    """
    Creates the InMemoryUploadedFile object using thedata from io
    to save it into the ImageField of the database
    """
    io = get_image_data()  # get a red rectangle 200x200px
    # create the InMemoryUploadedFile object with the 'foo.jpg' file
    image_file = InMemoryUploadedFile(io, None, 'foo.jpg', 
                            'jpeg', sys.getsizeof(io), None)
    image_file.seek(0)  # seek to the beginning
    return image_file

def create_image_file(name):
    """
    Saves the image data to the file
    """
    io = get_image_data()  # get a red rectangle 200x200px
    # save it into the file
    with open(name, 'wb') as f:
        f.write(io.read())

def get_image_size(path):
    """
    Returns the size of the image
    """
    with Image.open(path) as img:
        return img.size

@contextmanager
def patch_settings(settings_dict):
    """
    Temporary replaces values in the ContentGallery
    settings with values from the dictionary
    """
    saved_settings = {}
    for key, value in settings_dict.items():
        # save the original value
        saved_settings[key] = settings.CONF[key]
        # set the fake value
        settings.CONF[key] = value
    # stop here until the context manager exits
    yield
    # restore the original settings
    settings.CONF.update(saved_settings)

def clean_db():
    """
    Removes all objects from the test database
    """
    TestModel.objects.all().delete()
    AnotherTestModel.objects.all().delete()
    WrongTestModel.objects.all().delete()
    models.Image.objects.all().delete()
