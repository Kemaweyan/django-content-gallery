from django.contrib import admin

from content_gallery.admin import ImageAdminInline

from . import models

class CatAdmin(admin.ModelAdmin):
    inlines = [
        ImageAdminInline,
    ]

admin.site.register(models.Cat, CatAdmin)
