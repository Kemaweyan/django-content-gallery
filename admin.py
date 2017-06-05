import json

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericInlineModelAdmin
from django.conf.urls import url
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from . import models
from . import forms
from . import utils

class ImageAdminInline(GenericInlineModelAdmin):
    """
    Inline model admin of Image that could be added to related models.
    Adds to admin page a collection of images related to the object.
    """
    model = models.Image
    form = forms.ImageAdminInlineForm
    template = "content_gallery/admin/image_admin_inline.html"
    extra = 0

    class Media:
        js = (
            utils.create_static_url(
                "content_gallery/js/content-gallery-view.js"
            ),
            utils.create_static_url(
                "content_gallery/admin/js/content-gallery-admin-view.js"
            ),
            utils.create_static_url(
                "content_gallery/admin/js/content-gallery-inline-admin.js"
            ),
        )
        css = {
            "all": (
                utils.create_static_url(
                    "content_gallery/css/content-gallery.css"
                ),
                utils.create_static_url(
                    "content_gallery/admin/css/content-gallery-admin.css"
                ),
                utils.create_static_url(
                    "content_gallery/admin/css/"
                    "content-gallery-inline-admin.css"
                ),
            )
        }

    def get_queryset(self, request):
        """
        Returns a collection of Image objects ordered by 'position' value.
        """
        qs = super().get_queryset(request)
        return qs.order_by('position')

    def get_formset(self, request, obj=None, **kwargs):
        """
        Adds 'preview_url_pattern' attribute to the formset object.
        The attribute contains the pattern of URL used by JavaScript code
        to get data of new added image to show its preview.
        """
        formset = super().get_formset(request, obj, **kwargs)
        url = utils.get_admin_new_image_preview_url_pattern()
        setattr(formset, 'preview_url_pattern', url)
        return formset


class ImageAdmin(admin.ModelAdmin):
    """
    Model admin of Image.
    """
    form = forms.ImageAdminForm
    change_form_template = "content_gallery/admin/image_admin.html"

    def get_urls(self):
        """
        Adds extra URL pattern for getting data of images. Used by
        JavaScript code in inline admin for new added images.
        """
        urls = super().get_urls()
        extra_urls = [
            url(
                r'^ajax/preview/(?P<pk>\d+)/$',
                self.preview,
                name='gallery_new_image_preview'
            ),
        ]
        return extra_urls + urls

    def preview(self, request, pk):
        """
        A view that returns data of an image object.
        """
        # allow only AJAX requests
        if not request.is_ajax():
            raise PermissionDenied
        image = get_object_or_404(models.Image, pk=pk)
        data = utils.create_image_data(image)
        response = {
            "small_preview_url": image.small_preview_url,
            "position": image.position,
            "image_data": json.dumps(data),
            "zoom_url": utils.create_static_url(
                "content_gallery/img/zoom-small.png"
            ),
        }
        return HttpResponse(
            json.dumps(response),
            content_type='application/json'
        )

    class Media:
        js = (
            utils.create_static_url(
                "content_gallery/js/content-gallery-view.js"
            ),
            utils.create_static_url(
                "content_gallery/admin/js/content-gallery-admin-view.js"
            ),
        )
        css = {
            "all": (
                utils.create_static_url(
                    "content_gallery/css/content-gallery.css"
                ),
                utils.create_static_url(
                    "content_gallery/admin/css/content-gallery-admin.css"
                ),
            )
        }

admin.site.register(models.Image, ImageAdmin)
