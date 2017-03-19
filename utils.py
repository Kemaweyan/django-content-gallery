import os
import re
from PIL import Image

from django.core import urlresolvers as ur

from . import settings

IMG_W = settings.GALLERY_IMAGE_WIDTH
IMG_H = settings.GALLERY_IMAGE_HEIGHT

THUMB_W = settings.GALLERY_THUMBNAIL_WIDTH
THUMB_H = settings.GALLERY_THUMBNAIL_HEIGHT

def make_src(slug, filename=''):
    if filename and '.' in filename:
        name, ext = os.path.splitext(filename)
        src = "{}{}".format(slug, ext)
    else:
        src = slug
    return os.path.join('gallery', src)

def get_choices_url_pattern():
    choices_url = ur.reverse('gallery:choices', args=(0,))
    return re.sub(r'\d+$', '', choices_url)

def create_thumbnail_path(path):
    name, ext = os.path.splitext(path)
    return "{}_thumbnail{}".format(name, ext)

def resize(path, size, rename=""):
    img = Image.open(path)
    img.thumbnail(size)
    if rename:
        path = rename
    img.save(path, img.format)    

def resize_image(path):
    size = (IMG_W, IMG_H)
    resize(path, size)

def create_thumbnail(path):
    size = (THUMB_W, THUMB_H)
    thumb_path = create_thumbnail_path(path)
    resize(path, size, thumb_path)

def delete_thumbnail(path):
    thumb_path = create_thumbnail_path(path)
    try:
        os.remove(thumb_path)
    except FileNotFoundError:
        pass
