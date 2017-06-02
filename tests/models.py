from django.db import models as django_models

from .. import models

class BaseTestModel(django_models.Model):
    name = django_models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class TestModel(models.ContentGalleryMixin, BaseTestModel):
    pass


class AnotherTestModel(models.ContentGalleryMixin, BaseTestModel):
    gallery_visible = False


class WrongTestModel(BaseTestModel):
    pass
