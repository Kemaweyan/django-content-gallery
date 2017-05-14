import json

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericInlineModelAdmin
from django.conf.urls import url
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from . import models
from . import forms
from . import utils

class ImageAdminInline(GenericInlineModelAdmin):
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
                    "content_gallery/admin/css/content-gallery-inline-admin.css"
                ),
            )
        }

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('position')


class ImageAdmin(admin.ModelAdmin):
    form = forms.ImageAdminForm
    change_form_template = "content_gallery/admin/image_admin.html"

    def get_urls(self):
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
        image = get_object_or_404(models.Image, pk=pk)
        data = utils.create_image_data(image)
        response = {
            "small_preview_url": image.small_preview_url,
            "position": image.position,
            "image_data": json.dumps(data),
        }
        return HttpResponse(json.dumps(response), content_type='application/json')

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
