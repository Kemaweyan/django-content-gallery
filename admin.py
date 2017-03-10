from django.contrib import admin

from . import models
from . import forms

class ImageAdmin(admin.ModelAdmin):
    form = forms.ImageAdminForm

admin.site.register(models.Image, ImageAdmin)
