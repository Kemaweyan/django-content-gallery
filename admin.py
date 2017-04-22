from django.contrib import admin
from django.contrib.contenttypes.admin import GenericInlineModelAdmin

from . import models
from . import forms

class ImageAdminInline(GenericInlineModelAdmin):
    model = models.Image
    form = forms.ImageAdminInlineForm
    template = "gallery/edit_inline/image_admin.html"
    extra = 0

    class Media:
        js = (
            "/static/admin/js/jquery-ui.js",
            "/static/admin/js/inline_admin.js",
        )
        css = {
            "all": ("/static/admin/css/inline_admin.css",)
        }

class ImageAdmin(admin.ModelAdmin):
    form = forms.ImageAdminForm

admin.site.register(models.Image, ImageAdmin)
