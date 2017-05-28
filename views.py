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
        "width": settings.GALLERY_IMAGE_WIDTH,
        "height": settings.GALLERY_IMAGE_HEIGHT
    }
    small_image_size = {
        "width": settings.GALLERY_SMALL_IMAGE_WIDTH,
        "height": settings.GALLERY_SMALL_IMAGE_HEIGHT
    }
    thumbnail_size = {
        "width": settings.GALLERY_THUMBNAIL_WIDTH,
        "height": settings.GALLERY_THUMBNAIL_HEIGHT
    }

    try:
        ctype = ContentType.objects.get(
            app_label=app_label,
            model=content_type
        )
    except:
        raise Http404
    else:
        qs = models.Image.objects.filter(content_type__exact=ctype,
                object_id__exact=object_id).order_by('position')
        max_size = (
            settings.GALLERY_SMALL_IMAGE_WIDTH,
            settings.GALLERY_SMALL_IMAGE_HEIGHT
        )

        images = []
        for img in qs:
            size = (img.image.width, img.image.height)
            small_width, small_height = utils.calculate_image_size(size, max_size)
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
        return HttpResponse(json.dumps(response), content_type='application/json')
