import json

from django import template
from django.utils import html

from .. import settings
from .. import utils

register = template.Library()

@register.simple_tag
def gallery_image_data(obj):
    image = utils.get_first_image(obj)
    try:
        data = {
            'app_label': image.content_type.app_label,
            'content_type': image.content_type.model,
            'object_id': str(image.object_id)
        }
    except AttributeError:
        data = {}
    data_json = json.dumps(data)
    return {
        'image': image,
        'data_image': html.escape(data_json)
    }


@register.inclusion_tag('content_gallery/templatetags/preview.html')
def gallery_preview(obj):
    context = {
        'image_width': settings.CONF['preview_width'],
        'image_height': settings.CONF['preview_height'],
        'div_width': settings.CONF['preview_width'] + 14,
        'div_height': settings.CONF['preview_height'] + 14,
        'zoom_left': settings.CONF['preview_width'] - 55
    }
    image_data = gallery_image_data(obj)
    context.update(image_data)
    return context


@register.inclusion_tag('content_gallery/templatetags/small_preview.html')
def gallery_small_preview(obj):
    context = {
        'image_width': settings.CONF['small_preview_width'],
        'image_height': settings.CONF['small_preview_height'],
        'div_width': settings.CONF['small_preview_width'] + 14,
        'div_height': settings.CONF['small_preview_height'] + 14,
        'zoom_left': settings.CONF['small_preview_width'] - 15
    }
    image_data = gallery_image_data(obj)
    context.update(image_data)
    return context


@register.simple_tag
def gallery_data_url_pattern():
    return utils.get_gallery_data_url_pattern()
