import json

from django.http import HttpResponse, Http404
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from . import settings
from . import models
from . import utils

def choices(request, pk):
    if not request.is_ajax():
        raise PermissionDenied
    response = []
    ctype = get_object_or_404(ContentType, pk=pk)
    model_class = ctype.model_class()
    try:
        if model_class.gallery_visible:
            qs = model_class.objects.all()
            for product in qs:
                response.append({"id": str(product.id), "name": str(product)})
        else:
            raise PermissionDenied
    except AttributeError:
        raise Http404
    return HttpResponse(json.dumps(response), content_type='application/json')


def gallery_data(request, app_label, content_type, object_id):
    if not request.is_ajax():
        raise PermissionDenied
    image_size = {
        "width": settings.CONF['image_width'],
        "height": settings.CONF['image_height']
    }
    small_image_size = {
        "width": settings.CONF['small_image_width'],
        "height": settings.CONF['small_image_height']
    }
    thumbnail_size = {
        "width": settings.CONF['thumbnail_width'],
        "height": settings.CONF['thumbnail_height']
    }

    try:
        ctype = ContentType.objects.get(
            app_label=app_label,
            model=content_type
        )
    except:
        raise Http404
    else:
        obj = get_object_or_404(ctype.model_class(), pk=object_id)
        qs = obj.gallery.order_by('position')
        max_size = (
            settings.CONF['small_image_width'],
            settings.CONF['small_image_height']
        )

        images = []
        for img in qs:
            size = (img.image.width, img.image.height)
            small_width, small_height = utils.calculate_image_size(
                size,
                max_size
            )
            images.append({
                "image": img.image_url,
                "image_size": {
                    "width": img.image.width,
                    "height": img.image.height
                },
                "small_image_size": {
                    "width": small_width,
                    "height": small_height
                },
                "small_image": img.small_image_url,
                "thumbnail": img.thumbnail_url
            })

        response = {
            "images": images,
            "image_size": image_size,
            "small_image_size": small_image_size,
            "thumbnail_size": thumbnail_size,
        }
        return HttpResponse(
            json.dumps(response),
            content_type='application/json'
        )
