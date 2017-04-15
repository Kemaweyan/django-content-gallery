from django.contrib import admin
from django.contrib.contenttypes.admin import GenericInlineModelAdmin

from . import models
from . import forms

class ImageAdminInline(GenericInlineModelAdmin):
    model = models.Image
    form = forms.ImageAdminInlineForm
    template = "gallery/edit_inline/image_admin.html"

class ImageAdmin(admin.ModelAdmin):
    form = forms.ImageAdminForm

admin.site.register(models.Image, ImageAdmin)
