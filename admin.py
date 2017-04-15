from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

from . import models
from . import forms

class ImageAdminInline(GenericStackedInline):
    model = models.Image

class ImageAdmin(admin.ModelAdmin):
    form = forms.ImageAdminForm

admin.site.register(models.Image, ImageAdmin)
