import sys
import os
import re
import io
from PIL import Image
import magic

from django.core import urlresolvers as ur
from django.core.files import uploadedfile as uf

from . import settings

LARGE_W = settings.GALLERY_LARGE_WIDTH
LARGE_H = settings.GALLERY_LARGE_HEIGHT

IMG_W = settings.GALLERY_IMAGE_WIDTH
IMG_H = settings.GALLERY_IMAGE_HEIGHT

THUMB_W = settings.GALLERY_THUMBNAIL_WIDTH
THUMB_H = settings.GALLERY_THUMBNAIL_HEIGHT

def get_choices_url_pattern():
    choices_url = ur.reverse('gallery:choices', args=(0,))
    return re.sub(r'\d+$', '', choices_url)

def get_basename(path):
    return os.path.basename(path)

def get_file_ext(filename):
    name, ext = os.path.splitext(filename)
    return ext

def get_file_name(filename):
    name, ext = os.path.splitext(os.path.basename(filename))
    return name

def create_path(filename):
    return os.path.join(settings.MEDIA_ROOT, settings.GALLERY_PATH, filename)

def create_url(filename):
    return os.path.join(settings.MEDIA_URL, settings.GALLERY_PATH, filename)

def create_db_slug(slug):
    return os.path.join(settings.GALLERY_PATH, slug)

def _resize(src, dst, size):
    img = Image.open(src)
    img.thumbnail(size)
    img.save(dst, img.format)

def resize_image(img):
    size = (IMG_W, IMG_H)
    output = io.BytesIO()
    _resize(img, output, size)
    mime = magic.from_buffer(output.getvalue(), mime=True)
    f = uf.InMemoryUploadedFile(output, 'ImageField', img.name, mime,
        sys.getsizeof(output), None)
    return f

def create_thumbnail(img, path):
    size = (THUMB_W, THUMB_H)
    _resize(img, path, size)

def create_large_image(img, path):
    size = (LARGE_W, LARGE_H)
    _resize(img, path, size)

def safe_delete(path):
    try:
        os.remove(path)
    except:
        pass

def safe_rename(src, dst):
    try:
        os.rename(src, dst)
    except:
        pass
