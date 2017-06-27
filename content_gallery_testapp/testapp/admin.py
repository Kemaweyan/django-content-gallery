from django.contrib import admin

from content_gallery.admin import ImageAdminInline

from . import models

# add ImageAdminInline inline that allows to manage
# related images on the Cat admin page (add, remove, sort)

class CatAdmin(admin.ModelAdmin):
    inlines = [
        ImageAdminInline,
    ]

admin.site.register(models.Cat, CatAdmin)
