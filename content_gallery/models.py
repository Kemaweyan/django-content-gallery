from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

from slugify import UniqueSlugify

from . import utils
from . import settings
from . import fields

def _unique_slug_check(slug, uids):
    """
    Checks whether there is an image with given slug
    """
    slug = utils.name_in_db(slug)
    return not Image.objects.filter(image__startswith=slug)

# the object used to create unique slugs for names of images
# slugs contain the slugified str versions of the object and an unique number
# except first image:
#     slugified-title
#     slugified-title-1
#     slugified-title-2
#     etc...
slugify_unique = UniqueSlugify(unique_check=_unique_slug_check, to_lower=True)


class ImageQuerySet(models.QuerySet):
    """
    A custom QuerySet that implements deletion of all related files
    """

    def delete(self):
        """
        Perfoms deletion of all related files
        """
        for obj in self:
            obj.delete_files()
        return super().delete()


class ImageManager(models.Manager):
    """
    A custom Manager that returns specific QuerySet. Used in the Image model
    """

    def get_queryset(self):
        """
        Returns custom QuerySet used for Image model
        """
        return ImageQuerySet(self.model, using=self._db)
   

class Image(models.Model):
    """
    A model of image objects. It stores the image itself, its position
    between other images and the link to the object the image is related to.
    """

    image = fields.GalleryImageField(upload_to=settings.CONF['path'])
    position = models.IntegerField(default=0, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    #use custom manager
    objects = ImageManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # store initial content type and object_id to check whether related
        # object has been changed (another content_type and/or object_id)
        self.init_type = None
        self.init_id = self.object_id
        # do not try to read content_type value if there is no related object
        if self.object_id:
            self.init_type = self.content_type
        # store the name of the image to be able to keep correct filenames
        # when new images have been uploaded replacing old files
        self.image_name = self.image.name

    def __str__(self):
        return '{} photo #{}'.format(self.content_object, self.position + 1)

    def _get_position(self):
        """
        Calculates a position of added image and assing the value to the
        'position' field. New images are placed into the end of the list
        """
        # get all images related to the same object
        images = Image.objects.filter(
            content_type__exact=self.content_type,
            object_id__exact=self.object_id
        ).order_by('-position')[:1]
        if images:
            # a new position is greater by 1 than the last position
            self.position = images[0].position + 1
        else:
            # there were no images, this is the first one
            self.position = 0

    def _object_changed(self):
        """
        Checks whether the relation to the object has been changed
        """
        return self.content_type != self.init_type \
            or self.object_id != self.init_id

    def _get_slug(self):
        """
        Creates an unique slug using str version of the related object.
        The slug is used to create names of the image files.
        """
        title = str(self.content_object)
        return slugify_unique(title)

    def _save_data(self):
        """
        Saves image data to files
        """
        if not self.pk or self._object_changed():
            # create new position and new slug for new image
            # or if related object has been changed
            self._get_position()
            slug = self._get_slug()
        else:
            slug = ''
        self.image.save_files(slug, self.image_name)

    def save(self, *args, **kwargs):
        """
        Saves the image object
        """
        # save image data first
        self._save_data()
        super().save(*args, **kwargs)

    def delete_files(self):
        """
        Deletes image files
        """
        self.image.delete_files()

    def delete(self, *args, **kwargs):
        """
        Deletes the image object
        """
        # delete image data first
        self.delete_files()
        return super().delete(*args, **kwargs)

    @property
    def thumbnail_url(self):
        """
        URL of the thumbnail file
        """
        return self.image.thumbnail_url

    @property
    def image_url(self):
        """
        URL of the fullsize image file
        """
        return self.image.image_url

    @property
    def small_image_url(self):
        """
        URL of the small image file
        """
        return self.image.small_image_url

    @property
    def preview_url(self):
        """
        URL of the large preview file
        """
        return self.image.preview_url

    @property
    def small_preview_url(self):
        """
        URL of the small preview file
        """
        return self.image.small_preview_url


class ContentGalleryMixin(models.Model):
    """
    A mixin that adds the ContentGallery features to any model
    of you project. It allows to access all related images via
    the 'gallery' field. The 'gallery_visible' flag is used to hide
    your model from the list in the content_gallery.Image admin page
    by setting it to False. But you still can add images from the
    admin pages of you models.
    """

    content_gallery = GenericRelation(Image)  # the manager of related images
    gallery_visible = True  # the flag of visibility in the Image admin

    class Meta:
        abstract = True
