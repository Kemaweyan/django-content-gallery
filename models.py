from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

from slugify import UniqueSlugify

from . import utils
from . import settings
from . import fields

def _unique_slug_check(slug, uids):
    slug = utils.name_in_db(slug)
    return not Image.objects.filter(image__startswith=slug)

slugify_unique = UniqueSlugify(unique_check=_unique_slug_check, to_lower=True)


class ImageQuerySet(models.QuerySet):

    def delete(self):
        for obj in self:
            obj.delete_files()
        return super().delete()


class ImageManager(models.Manager):

    def get_queryset(self):
        return ImageQuerySet(self.model, using=self._db)
   

class Image(models.Model):
    image = fields.GalleryImageField(upload_to=settings.GALLERY_PATH)
    position = models.IntegerField(default=0, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = ImageManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_type = None
        self.init_id = self.object_id
        if self.object_id:
            self.init_type = self.content_type
        self.image_name = self.image.name

    def __str__(self):
        return '{} photo #{}'.format(self.content_object, self.position + 1)

    def _get_position(self):
        images = Image.objects.filter(
            content_type__exact=self.content_type,
            object_id__exact=self.object_id
        ).order_by('-position')
        if images:
            self.position = images[0].position + 1
        else:
            self.position = 0

    def _object_changed(self):
        return self.content_type != self.init_type \
            or self.object_id != self.init_id

    def _get_slug(self):
        title = str(self.content_object)
        return slugify_unique(title)

    def save(self, *args, **kwargs):
        if not self.pk or self._object_changed():
            self._get_position()
            slug = self._get_slug()
        else:
            slug = ''
        self.image.save_files(slug, self.image_name)
        super().save(*args, **kwargs)

    def delete_files(self):
        self.image.delete_files()

    def delete(self, *args, **kwargs):
        self.delete_files()
        return super().delete(*args, **kwargs)

    @property
    def thumbnail_url(self):
        return self.image.thumbnail_url

    @property
    def image_url(self):
        return self.image.image_url

    @property
    def small_image_url(self):
        return self.image.small_image_url

    @property
    def preview_url(self):
        return self.image.preview_url

    @property
    def small_preview_url(self):
        return self.image.small_preview_url


class ContentGalleryMixin(models.Model):

    gallery = GenericRelation(Image)
    gallery_visible = True

    class Meta:
        abstract = True
