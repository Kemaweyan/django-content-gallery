import json

from django.http import HttpResponse, Http404
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

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
    except:
        raise Http404
    return HttpResponse(json.dumps(response), content_type='application/json')
