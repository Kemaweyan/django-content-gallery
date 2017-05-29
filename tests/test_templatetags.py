from django.test import mock, TestCase
from django.contrib.contenttypes.models import ContentType

from ..templatetags import content_gallery
from .. import models
from .. import settings

from .models import TestModel, ViewsTestCase
from .utils import get_image_in_memory_data

class TestGetFirstImage(ViewsTestCase):

    def test_get_image(self):
        img = content_gallery.get_first_image(self.object)
        self.assertEquals(self.image1, img)

    def test_get_image_change_order(self):
        self.image1.position = 2
        self.image1.save()
        img = content_gallery.get_first_image(self.object)
        self.assertEquals(self.image2, img)

    def test_get_image_none(self):
        img = content_gallery.get_first_image(self.alone_object)
        self.assertIsNone(img)
