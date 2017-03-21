import sys
import os
import re
import io
from PIL import Image
import magic

from django.core import urlresolvers as ur
from django.core.files import uploadedfile as uf

from . import settings

# the size of large image
LARGE_W = settings.GALLERY_LARGE_WIDTH
LARGE_H = settings.GALLERY_LARGE_HEIGHT

# the size of normal image
IMG_W = settings.GALLERY_IMAGE_WIDTH
IMG_H = settings.GALLERY_IMAGE_HEIGHT

# the size of small image (thumbnail)
THUMB_W = settings.GALLERY_THUMBNAIL_WIDTH
THUMB_H = settings.GALLERY_THUMBNAIL_HEIGHT

def get_choices_url_pattern():
    """
    Returns the pattern of URL for getting product choices
    via AJAX in JS code.
    """
    # get 'choices' URL with any id
    choices_url = ur.reverse('gallery:choices', args=(0,))
    # remove id (last digits in the URL)
    return re.sub(r'\d+$', '', choices_url)

def get_basename(path):
    """Returns basename of path. A shortcut for os.path.basename"""
    return os.path.basename(path)

def get_file_ext(filename):
    """Returns the extension of the file"""
    name, ext = os.path.splitext(filename)
    return ext

def get_file_name(filename):
    """Returns the name of the file without extension"""
    name, ext = os.path.splitext(os.path.basename(filename))
    return name

def create_path(filename):
    """Returns the path to the file in the GALLERY_PATH folder"""
    return os.path.join(settings.MEDIA_ROOT, settings.GALLERY_PATH, filename)

def create_url(filename):
    """Returns the URL to the file"""
    return os.path.join(settings.MEDIA_URL, settings.GALLERY_PATH, filename)

def create_db_slug(slug):
    """
    Returns the slug in pattern that could be stored in the database.
    After saving the model, ImageField adds GALLERY_PATH to image filename,
    therefore the image field in the database contains filename with that
    path. This function adds the path to the slug in order to search such
    items in the database.
    """
    return os.path.join(settings.GALLERY_PATH, slug)

def _resize(src, dst, size):
    """Resizes image data from src using size, saves to dst"""
    img = Image.open(src)
    img.thumbnail(size)
    img.save(dst, img.format)

def resize_image(img):
    """
    Resizes image data to IMAGE_SIZE and returns the InMemoryUploadedFile
    object that could be assigned to ImageField field.
    """
    size = (IMG_W, IMG_H)
    output = io.BytesIO()
    _resize(img, output, size)
    # get mime type of data
    mime = magic.from_buffer(output.getvalue(), mime=True)
    f = uf.InMemoryUploadedFile(output, 'ImageField', img.name, mime,
        sys.getsizeof(output), None)
    return f

def create_thumbnail(img, path):
    """Creates the thumbnail and saves it to path"""
    size = (THUMB_W, THUMB_H)
    _resize(img, path, size)

def create_large_image(img, path):
    """Creates the large image and saves it to path"""
    size = (LARGE_W, LARGE_H)
    _resize(img, path, size)

def safe_delete(path):
    """Removes the file if it exists"""
    try:
        os.remove(path)
    except:
        pass

def safe_rename(src, dst):
    """Renames the file if it exists"""
    try:
        os.rename(src, dst)
    except:
        pass
