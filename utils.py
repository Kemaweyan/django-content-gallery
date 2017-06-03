import sys
import os
import re
import io
from PIL import Image
import magic

from django.core import urlresolvers
from django.core.files import uploadedfile
from django.conf import settings as django_settings

from . import settings

def get_choices_url_pattern():
    """
    Returns the pattern of URL for getting product choices
    via AJAX in JS code.
    """
    # get 'choices' URL with any id
    choices_url = urlresolvers.reverse('gallery:choices', args=(0,))
    # remove id (last digits in the URL)
    return re.sub(r'\d+/?$', '', choices_url)

def get_gallery_data_url_pattern():
    choices_url = urlresolvers.reverse(
        'gallery:gallery_data',
        args=(
            'app_label',
            'content_type',
            0
        )
    )
    return re.sub(r'\w+/\w+/\d+/?$', '', choices_url)

def get_admin_new_image_preview_url_pattern():
    preview_url = urlresolvers.reverse(
        'admin:gallery_new_image_preview',
         args=(0,)
    )
    return re.sub(r'\d+/?$', '', preview_url)

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
    return os.path.join(
        django_settings.MEDIA_ROOT,
        settings.CONF['path'],
        filename
    )

def create_url(filename):
    media_url = django_settings.MEDIA_URL.rstrip('/')
    gallery_path = settings.CONF['path'].strip('/')
    return '/'.join([media_url, gallery_path, filename])

def name_in_db(name):
    return os.path.join(settings.CONF['path'], name)

def image_resize(src, dst, size):
    with Image.open(src) as img:
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
            "width": settings.CONF['image_width'],
            "height": settings.CONF['image_height']
        },
        "small_image":  {
            "url": image.small_image_url,
            "width": settings.CONF['small_image_width'],
            "height": settings.CONF['small_image_height']
        }
    }

def create_static_url(url):
    static = django_settings.STATIC_URL.rstrip("/")
    return "/".join([static, url])
