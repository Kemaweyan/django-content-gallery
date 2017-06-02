from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

CONF = {
    'image_width': 752,
    'image_height': 608,
    'small_image_width': 564,
    'small_image_height': 456,
    'thumbnail_width': 94,
    'thumbnail_height': 76,
    'preview_width': 376,
    'preview_height': 304,
    'small_preview_width': 141,
    'small_preview_height': 114,
    'path': 'gallery',
}

CONF.update(getattr(settings, 'CONTENT_GALLERY', {}))

if getattr(settings, 'MEDIA_ROOT', None) is None:
    raise ImproperlyConfigured("'MEDIA_ROOT' variable is not defined")

if getattr(settings, 'MEDIA_URL', None) is None:
    raise ImproperlyConfigured("'MEDIA_URL' variable is not defined")
