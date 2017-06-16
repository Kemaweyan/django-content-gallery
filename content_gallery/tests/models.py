from django.db import models as django_models

from .. import models

class BaseTestModel(django_models.Model):
    """
    An abstract base test model class for test objects that
    could be related to Images. Contains just one text field
    """
    name = django_models.CharField(max_length=100)

    def __str__(self):
        """
        A str version of the object just returns
        the value of its text field
        """
        return self.name

    class Meta:
        abstract = True


class TestModel(models.ContentGalleryMixin, BaseTestModel):
    """
    A main test model. Uses the ContentGalleryMixin without
    changes, so it allows to show the model in the list of
    available models in the Image admin.
    """


class AnotherTestModel(models.ContentGalleryMixin, BaseTestModel):
    """
    Another test model. It also uses the ContentGalleryMixin, but
    sets the 'gallery_visible' to False, so it's still possible
    to attach images to objects of this model, but the model
    does not present in the available models list in the Image admin.
    """
    gallery_visible = False


class WrongTestModel(BaseTestModel):
    """
    A test model that does not uses the ContentGalleryMixin.
    It could not be related to the Image objects.
    """
