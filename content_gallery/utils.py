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
    # get 'choices' URL using 'reverse',
    # the pattern requires one numeric argument
    choices_url = urlresolvers.reverse('content_gallery:choices', args=(0,))
    # remove argument (last digits in the URL with '/' optionally)
    return re.sub(r'\d+/?$', '', choices_url)

def get_gallery_data_url_pattern():
    """
    Returns the pattern of URL for getting data of images
    related to the object
    """
    # get 'gallery_data' using 'reverse',
    # the pattern requires two words and one number as arguments
    choices_url = urlresolvers.reverse(
        'content_gallery:gallery_data',
        args=(
            'app_label',
            'content_type',
            0
        )
    )
    # remove arguments
    return re.sub(r'\w+/\w+/\d+/?$', '', choices_url)

def get_admin_new_image_preview_url_pattern():
    """
    Returns the pattern of URL for getting data of the image.
    Used to get data of new added image.
    """
    # get 'gallery_new_image_preview' using 'reverse',
    # the pattern requires one numeric argument
    preview_url = urlresolvers.reverse(
        'admin:gallery_new_image_preview',
         args=(0,)
    )
    # remove argument (last digits in the URL with '/' optionally)
    return re.sub(r'\d+/?$', '', preview_url)

def calculate_image_size(size, target_size):
    """
    Returns the size of the image after resizing.
    The same code is used in PIL.Image.thumbnail
    The results of this function is used by JavaScript
    in resize effect while changing image.
    """
    x, y = size
    # if the width is greater than the target
    if x > target_size[0]:
        # proportionally decrease the height but not less than 1px
        y = int(max(y * target_size[0] / x, 1))
        x = int(target_size[0])  # set the width to the target width
    # if the height is still greater than the target
    if y > target_size[1]:
        # proportionally decrease the width but not less than 1px
        x = int(max(x * target_size[1] / y, 1))
        y = int(target_size[1])  # set the height to the target height
    return x, y

def get_ext(filename):
    """
    Returns the ext of the file name with prefix dot
    """
    name, ext = os.path.splitext(filename)
    return ext

def get_name(filename):
    """
    Returns the name of the file name without the ext
    """
    name, ext = os.path.splitext(filename)
    return name

def create_path(filename):
    """
    Returns the path to the file located in the gallery folder
    """
    return os.path.join(
        django_settings.MEDIA_ROOT,
        settings.CONF['path'],
        filename
    )

def create_url(filename):
    """
    Returns the URL of the file located in the gallery folder
    """
    # remove slashes to avoid double slashes in the URL
    # keep the first slash in the MEDIA_URL
    media_url = django_settings.MEDIA_URL.rstrip('/')
    gallery_path = settings.CONF['path'].strip('/')
    return '/'.join([media_url, gallery_path, filename])

def name_in_db(name):
    """
    Returns the name of the file after saving data to the database
    Adds the gallery folder to the file name
    """
    return os.path.join(settings.CONF['path'], name)

def image_resize(src, dst, size):
    """
    Resizes the image and saves it to the 'dst' (filename of io object)
    """
    with Image.open(src) as img:
        img.thumbnail(size)  # use 'thumbnail' to keep aspect ratio
        img.save(dst, img.format)

def create_in_memory_image(image, name, size):
    """
    Resizes the image and saves it as InMemoryUploadedFile object
    Returns the InMemoryUploadedFile object with the image data
    """
    output = io.BytesIO()  # create an io object
    # resize the image and save it to the io object
    image_resize(image, output, size)
    # get MIME type of the image
    mime = magic.from_buffer(output.getvalue(), mime=True)
    # create InMemoryUploadedFile using data from the io
    return uploadedfile.InMemoryUploadedFile(output, 'ImageField', name,
        mime, sys.getsizeof(output), None)

def create_image_data(image):
    """
    Returns a dict with the full-size image
    and the small image URLs with sizes
    """
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
    """
    Returns a URL to the file located in the static folder
    """
    # remove ending slash to avoid double slashes
    static = django_settings.STATIC_URL.rstrip("/")
    path = "/".join([static, url])
    # use obfuscated file in non-DEBUG mode
    return get_obfuscated_file(path)

def get_first_image(obj):
    """
    Returns the first image related to the object or None
    if there is no images. The first image is the image
    with the smallest value of the 'position' field. 
    """
    # get one image ordered by 'position'
    images = obj.content_gallery.all().order_by('position')[:1]
    # return None if result is empty
    if not images:
        return None
    # return the first image
    return images[0]

def get_obfuscated_file(path):
    """
    Adds .min to the filename in non-debug mode
    """
    if django_settings.DEBUG:
        return path
    name, ext = os.path.splitext(path)
    return "".join([name, ".min", ext])
