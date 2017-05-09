import json

from django.template import Library
from django.conf import settings as global_sett
from django.utils.html import escape

from .. import settings

register = Library()

def get_first_image(obj):
    images = obj.gallery.all().order_by('position')
    if not images:
        return None
    return images[0]

@register.inclusion_tag('content_gallery/templatetags/preview.html')
def gallery_preview(obj):
    image = get_first_image(obj)
    context = {
        'image_width': settings.GALLERY_PREVIEW_WIDTH,
        'image_height': settings.GALLERY_PREVIEW_HEIGHT,
        'div_width': settings.GALLERY_PREVIEW_WIDTH + 14,
        'div_height': settings.GALLERY_PREVIEW_HEIGHT + 14,
        'zoom_left': settings.GALLERY_PREVIEW_WIDTH - 55
    }
    if not image:
        context.update({'no_image': True})
        return context
    data = {
        'app_label': image.content_type.app_label,
        'content_type': image.content_type.model,
        'object_id': str(image.object_id)
    }
    data_json = json.dumps(data)
    context.update({
        'preview_url': image.preview_url,
        'data_image': escape(data_json),
        'alt': str(image),
        'no_image': False
    })
    return context


@register.simple_tag
def gallery_small_preview(obj):
    image = get_first_image(obj)
    if not image:
        return "/".join([
            global_sett.STATIC_URL.rstrip("/"),
            "content_gallery",
            "img",
            "no-image-small.png"
        ])
    return image.small_preview_url
    
