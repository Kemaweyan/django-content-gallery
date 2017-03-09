from django.contrib import admin

from . import models

class ImageAdmin(admin.ModelAdmin):
    fields = ('src', 'content_type', 'object_id')

admin.site.register(models.Image, ImageAdmin)
