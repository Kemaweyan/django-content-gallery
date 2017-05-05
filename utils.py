import sys
import os
import re
import io
from PIL import Image
import magic

from django.core import urlresolvers
from django.core.files import uploadedfile
from django.conf import settings as global_sett

from . import settings

def get_choices_url_pattern():
    """
    Returns the pattern of URL for getting product choices
    via AJAX in JS code.
    """
    # get 'choices' URL with any id
    choices_url = urlresolvers.reverse('gallery:choices', args=(0,))
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

def image_resize(src, dst, size):
    img = Image.open(src)
    img.thumbnail(size)
    img.save(dst, img.format)

def create_in_memory_image(image, name, size):
    output = io.BytesIO()
    image_resize(image, output, size)
    mime = magic.from_buffer(output.getvalue(), mime=True)
    return uploadedfile.InMemoryUploadedFile(output, 'ImageField', name,
        mime, sys.getsizeof(output), None)

def create_image_data(image):
    return {
        "image": {
            "url": image.image_url,
            "width": settings.GALLERY_IMAGE_WIDTH,
            "height": settings.GALLERY_IMAGE_HEIGHT
        },
        "small_image":  {
            "url": image.small_image_url,
            "width": settings.GALLERY_SMALL_IMAGE_WIDTH,
            "height": settings.GALLERY_SMALL_IMAGE_HEIGHT
        }
    }

def create_static_url(url):
    static = global_sett.STATIC_URL.rstrip("/")
    return "/".join([static, url])
