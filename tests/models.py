from django.db import models as django_models
from django.test import TestCase, mock
from django.contrib.contenttypes.models import ContentType

from .. import models
from .. import settings

from .utils import get_image_in_memory_data

class TestModel(django_models.Model):
    name = django_models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AnotherTestModel(django_models.Model):
    name = django_models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ImageTestCase(TestCase):

    @mock.patch('gallery.models.slugify_unique', return_value='foo')
    def setUp(self, slugify_unique):
        self.object = TestModel(name="TestObject")
        self.object.save()
        self.image = models.Image(
            image=get_image_in_memory_data(),
            position=0,
            content_type=ContentType.objects.get_for_model(TestModel),
            object_id=self.object.id
        )
        self.image.save()
        self.image = self.get_image()

    def tearDown(self):
        self.image.delete()
        self.object.delete()

    @staticmethod
    def get_image():
        return models.Image.objects.all()[0]

    @staticmethod
    def get_name(name):
        return "/".join([settings.GALLERY_PATH, name])


class MultipleObjectsImageTestCase(ImageTestCase):

    def setUp(self):
        super().setUp()
        self.second_object = TestModel(name="SecondTestObject")
        self.second_object.save()
        self.another_object = AnotherTestModel(name="AnotherTestObject")
        self.another_object.save()

    def tearDown(self):
        super().tearDown()
        self.second_object.delete()
        self.another_object.delete()
