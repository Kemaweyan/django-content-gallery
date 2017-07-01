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
    # get the ContentType object or raise 404
    ctype = get_object_or_404(
        ContentType,
        app_label=app_label,
        model=content_type
    )
    # get the object of the model or raise 404
    obj = get_object_or_404(ctype.model_class(), pk=object_id)
    # order images by 'position'
    qs = obj.content_gallery.order_by('position')
    # the target size of the small image from the settings
    max_size = (
        settings.CONF['small_image_width'],
        settings.CONF['small_image_height']
    )

    # Since there is the resizing effect when user switches to another
    # image, the JavaScript code requires actual sizes of images. But
    # images could have any aspect ratio so their width or haight could
    # differ from specified in the settings. Actually settings specify
    # just maximum values of width and height. But JavaSctipt code needs
    # real size of each image to keep correct aspect ratio while the effect
    # is performing.
    # There is no problem to determine the size of the full-size image
    # using properties of the ImageField. But with small images we must
    # calculate the size again using the size of full-size image to determine
    # the aspect ratio. 
    # For this purpose we use the 'utils.calculate_image_size' function.

    images = []
    for img in qs:
        try:
            # actual size of the full-size image
            # it raises an exception if the image file does not exist
            size = (img.image.width, img.image.height)
        except:
            # skip non-existing images
            continue
        # calculate the actual size of the small image
        small_width, small_height = utils.calculate_image_size(
            size,
            max_size
        )
        # add the data of the image to the list
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

    # create the response
    # the size settings are used by JavaScript code to create
    # HTML containers for images
    response = {
        "images": images,
        "image_size": image_size,
        "small_image_size": small_image_size,
        "thumbnail_size": thumbnail_size,
    }
    # send the response in JSON format
    return HttpResponse(json.dumps(response), content_type='application/json')
