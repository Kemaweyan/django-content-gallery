import json

from django import template
from django.utils import html

from .. import settings
from .. import utils

register = template.Library()

@register.simple_tag
def gallery_image_data(obj):
    """
    Returns data of the image related to the object.
    Used to construct previews.
    """
    # get the first image related to the object
    image = utils.get_first_image(obj)
    try:
        # get data related to the object if the image exists
        data = {
            'app_label': image.content_type.app_label,
            'content_type': image.content_type.model,
            'object_id': str(image.object_id)
        }
    except AttributeError:
        # set empty data if the image does not exist
        data = {}
    # return the image and data in JSON format
    data_json = json.dumps(data)
    return {
        'image': image,
        'data_image': html.escape(data_json)
    }


@register.inclusion_tag('content_gallery/templatetags/preview.html')
def gallery_preview(obj):
    """
    Returns a large preview of the first image related to the object
    """
    # preview dimensions used in its template
    context = {
        'image_width': settings.CONF['preview_width'],
        'image_height': settings.CONF['preview_height'],
        'div_width': settings.CONF['preview_width'] + 14,
        'div_height': settings.CONF['preview_height'] + 14,
        'zoom_left': settings.CONF['preview_width'] - 55
    }
    # get image data
    image_data = gallery_image_data(obj)
    # add the image data to the context
    context.update(image_data)
    # return context to render the template
    return context


@register.inclusion_tag('content_gallery/templatetags/small_preview.html')
def gallery_small_preview(obj):
    """
    Returns a small preview of the first image related to the object
    """
    # preview dimensions used in its template
    context = {
        'image_width': settings.CONF['small_preview_width'],
        'image_height': settings.CONF['small_preview_height'],
        'div_width': settings.CONF['small_preview_width'] + 14,
        'div_height': settings.CONF['small_preview_height'] + 14,
        'zoom_left': settings.CONF['small_preview_width'] - 15
    }
    # get image data
    image_data = gallery_image_data(obj)
    # add the image data to the context
    context.update(image_data)
    # return context to render the template
    return context


@register.simple_tag
def gallery_data_url_pattern():
    """
    Returns gallery data URL pattern used by JavaScript code.
    The template tag is used in the gallery template.
    """
    return utils.get_gallery_data_url_pattern()


@register.filter
def obfuscate(path):
    """
    Returns the link to the original static file in DEBUG mode
    of to the obfuscated file if the DEBUG is False.
    """
    return utils.get_obfuscated_file(path)
