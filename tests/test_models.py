from io import BytesIO
from PIL import Image
import sys

from django.core.files.base import File
from django.test import TestCase, mock
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import InMemoryUploadedFile

from .. import models

from .models import TestModel

class BaseTestCase(TestCase):

    @staticmethod
    def get_image_file():
        io = BytesIO()
        size = (200,200)
        color = (255,0,0,0)
        image = Image.new("RGBA", size, color)
        image.save(io, format='JPEG')
        image_file = InMemoryUploadedFile(io, None, 'foo.jpg', 'jpeg', sys.getsizeof(io), None)
        image_file.seek(0)
        return image_file

    @mock.patch('gallery.models.slugify_unique', return_value='foo')
    def setUp(self, slugify_unique):
        self.object = TestModel(name="TestObject")
        self.object.save()
        self.image = models.Image(
            image=self.get_image_file(),
            position=0,
            content_type=ContentType.objects.get_for_model(TestModel),
            object_id=self.object.id
        )
        self.image.save()

    def tearDown(self):
        self.image.delete()
        self.object.delete()


class TestUniqueSlugCheck(BaseTestCase):

    @mock.patch('gallery.utils.name_in_db', return_value='gallery/foo.jpg')
    def test_name_exisits(self, name_in_db):
        result = models._unique_slug_check("foo.jpg", [])
        self.assertEqual(result, False)
        name_in_db.assert_called_once_with("foo.jpg")

    @mock.patch('gallery.utils.name_in_db', return_value='gallery/bar.jpg')
    def test_name_not_exisits(self, name_in_db):
        result = models._unique_slug_check("bar.jpg", [])
        self.assertEqual(result, True)
        name_in_db.assert_called_once_with("bar.jpg")
