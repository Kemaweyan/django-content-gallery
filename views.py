import json

from django.http import HttpResponse, Http404
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from . import settings
from . import models
from . import utils

def choices(request, pk):
    """
    Returns a list of available objects of the model.
    The 'pk' argument is the primary key of the ContentType.
    """
    # allow only AJAX requests
    if not request.is_ajax():
        raise PermissionDenied
    response = []
    # get content type with specified pk and determine its model class
    ctype = get_object_or_404(ContentType, pk=pk)
    model_class = ctype.model_class()
    try:
        # look for 'gallery_visible' attribute in the model
        if model_class.gallery_visible:
            # the model permits to add it to the list
            # get all objects
            qs = model_class.objects.all()
            # add objects to the list
            for product in qs:
                response.append({"id": str(product.id), "name": str(product)})
        else:
            # the model does not permit to add it to the list
            raise PermissionDenied
    except AttributeError:
        # the model has not the 'gallery_visible' attribute
        # so images couldn't be attached to the model
        raise Http404
    # send the response in JSON format
    return HttpResponse(json.dumps(response), content_type='application/json')


def gallery_data(request, app_label, content_type, object_id):
    """
    Returns data of all images attached to the object.
    """
    # allow only AJAX requests
    if not request.is_ajax():
        raise PermissionDenied
    # the maximum size of full-size images
    image_size = {
        "width": settings.CONF['image_width'],
        "height": settings.CONF['image_height']
    }
    # the maximum size of small images
    small_image_size = {
        "width": settings.CONF['small_image_width'],
        "height": settings.CONF['small_image_height']
    }
    # the maximum size of thumbnails
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
