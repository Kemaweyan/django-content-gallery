import sys
from io import BytesIO
from contextlib import contextmanager
from PIL import Image

from django.core.files.uploadedfile import InMemoryUploadedFile

from .. import settings
from .. import models

from .models import *

def get_image_data():
    io = BytesIO()
    size = (200,200)
    color = (255,0,0,0)
    image = Image.new("RGBA", size, color)
    image.save(io, format='JPEG')
    io.seek(0)
    return io

def get_image_in_memory_data():
    io = get_image_data()
    image_file = InMemoryUploadedFile(io, None, 'foo.jpg', 
                            'jpeg', sys.getsizeof(io), None)
    image_file.seek(0)
    return image_file

def create_image_file(name):
    io = get_image_data()
    with open(name, 'wb') as f:
        f.write(io.read())

def get_image_size(path):
    with Image.open(path) as img:
        return img.size

@contextmanager
def patch_settings(settings_dict):
    saved_settings = {}
    for key, value in settings_dict.items():
        saved_settings[key] = settings.CONF[key]
        settings.CONF[key] = value
    yield
    settings.CONF.update(saved_settings)

def clean_db():
    TestModel.objects.all().delete()
    AnotherTestModel.objects.all().delete()
    WrongTestModel.objects.all().delete()
    models.Image.objects.all().delete()
