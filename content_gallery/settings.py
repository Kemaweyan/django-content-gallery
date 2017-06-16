from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# default settings
CONF = {
    # the size of full-size image
    'image_width': 752,
    'image_height': 608,

    # the size of small image
    'small_image_width': 564,
    'small_image_height': 456,

    # the size of thumbnail
    'thumbnail_width': 94,
    'thumbnail_height': 76,

    # the size of image preview
    'preview_width': 376,
    'preview_height': 304,

    # the size of small image preview
    'small_preview_width': 141,
    'small_preview_height': 114,

    # the path to image files
    'path': 'content_gallery',
}

# overwrite defaults with settings specified in project settings file
CONF.update(getattr(settings, 'CONTENT_GALLERY', {}))

# the ContentGallery requires the MEDIA_ROOT and MEDIA_URL settings

if getattr(settings, 'MEDIA_ROOT', None) is None:
    raise ImproperlyConfigured("'MEDIA_ROOT' variable is not defined")

if getattr(settings, 'MEDIA_URL', None) is None:
    raise ImproperlyConfigured("'MEDIA_URL' variable is not defined")
