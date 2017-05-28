from django.test import mock
from django.contrib.contenttypes.models import ContentType

from .. import models

from .models import *
from .utils import get_image_in_memory_data


class TestUniqueSlugCheck(ImageTestCase):

    @mock.patch('gallery.utils.name_in_db', return_value='gallery/foo.jpg')
    def test_name_exisits(self, name_in_db):
        result = models._unique_slug_check("foo.jpg", [])
        self.assertEqual(result, False)
        name_in_db.assert_called_once_with("foo.jpg")

    @mock.patch('gallery.utils.name_in_db', return_value='gallery/bar.jpg')
    def test_name_does_not_exisit(self, name_in_db):
        result = models._unique_slug_check("bar.jpg", [])
        self.assertEqual(result, True)
        name_in_db.assert_called_once_with("bar.jpg")


class TestImage(MultipleObjectsImageTestCase):

    def test_create_empty_image(self):
        image = models.Image()
        self.assertIsNone(image.init_type)
        self.assertIsNone(image.init_id)
        self.assertEqual(image.image_name, "")

    def test_create_atatched_to_object_image(self):
        ctype = ContentType.objects.get_for_model(TestModel)
        name = self.get_name('foo.jpg')
        self.assertEqual(self.image.init_type, ctype)
        self.assertEqual(self.image.init_id, self.object.id)
        self.assertEqual(self.image.image_name, name)

    def test_loaded_image_str(self):
        self.assertEqual(str(self.image), "TestObject photo #1")

    def test_craeted_image_str(self):
        image = self.get_image()
        self.assertEqual(str(image), "TestObject photo #1")

    def test_get_position_with_existing_images(self):
        image = models.Image(
            image=get_image_in_memory_data(),
            position=0,
            content_type=ContentType.objects.get_for_model(TestModel),
            object_id=self.object.id
        )
        image._get_position()
        self.assertEqual(image.position, 1)

    def test_get_position_with_new_object_id(self):
        image = models.Image(
            image=get_image_in_memory_data(),
            position=0,
            content_type=ContentType.objects.get_for_model(TestModel),
            object_id=self.second_object.id
        )
        image._get_position()
        self.assertEqual(image.position, 0)

    def test_get_position_with_new_content_type(self):
        image = models.Image(
            image=get_image_in_memory_data(),
            position=0,
            content_type=ContentType.objects.get_for_model(TestModel),
            object_id=self.another_object.id
        )
        image._get_position()
        self.assertEqual(image.position, 0)

    def test_object_changed_does_not_changed(self):
        self.assertFalse(self.image._object_changed())

    def test_object_changed_object_id_changed(self):
        self.image.content_object = self.second_object
        self.image.save()
        self.assertTrue(self.image._object_changed())

    def test_object_changed_object_ctype_changed(self):
        self.image.content_object = self.another_object
        self.image.save()
        self.assertTrue(self.image._object_changed())

    @mock.patch('gallery.models.slugify_unique', return_value='foo')
    def test_get_slug(self, slugify_unique):
        self.assertEqual('foo', self.image._get_slug())
        slugify_unique.assert_called_once_with('TestObject')

    def test_save_data_new_image(self):
        image = models.Image(
            image=get_image_in_memory_data(),
            position=0,
            content_type=ContentType.objects.get_for_model(TestModel),
            object_id=self.object.id
        )
        image._get_slug = mock.MagicMock(return_value='foo')
        image.image.save_files = mock.MagicMock()
        image._save_data()
        image._get_slug.assert_called_once()
        image.image.save_files.assert_called_once_with('foo', 'foo.jpg')

    def test_save_data_unchanged_image(self):
        self.image._get_slug = mock.MagicMock()
        self.image.image.save_files = mock.MagicMock()
        self.image._object_changed = mock.MagicMock(return_value=False)
        self.image._save_data()
        self.image._get_slug.assert_not_called()
        name = self.get_name('foo.jpg')
        self.image.image.save_files.assert_called_once_with('', name)

    def test_save_data_changed_image(self):
        self.image._get_slug = mock.MagicMock(return_value='foo')
        self.image.image.save_files = mock.MagicMock()
        self.image._object_changed = mock.MagicMock(return_value=True)
        self.image._save_data()
        self.image._get_slug.assert_called_once()
        name = self.get_name('foo.jpg')
        self.image.image.save_files.assert_called_once_with('foo', name)

    def test_delete_files_image(self):
        self.image.image.delete_files = mock.MagicMock()
        self.image.delete_files()
        self.image.image.delete_files.assert_called_once()

    def test_thumbnail_url_property(self):
        image_mock = mock.MagicMock()
        image_mock.thumbnail_url = 'foo'
        with mock.patch.object(self.image, 'image', image_mock):
            self.assertEqual(self.image.thumbnail_url, 'foo')

    def test_image_url_property(self):
        image_mock = mock.MagicMock()
        image_mock.image_url = 'foo'
        with mock.patch.object(self.image, 'image', image_mock):
            self.assertEqual(self.image.image_url, 'foo')

    def test_preview_url_property(self):
        image_mock = mock.MagicMock()
        image_mock.preview_url = 'foo'
        with mock.patch.object(self.image, 'image', image_mock):
            self.assertEqual(self.image.preview_url, 'foo')

    def test_small_image_url_property(self):
        image_mock = mock.MagicMock()
        image_mock.small_image_url = 'foo'
        with mock.patch.object(self.image, 'image', image_mock):
            self.assertEqual(self.image.small_image_url, 'foo')

    def test_small_preview_url_property(self):
        image_mock = mock.MagicMock()
        image_mock.small_preview_url = 'foo'
        with mock.patch.object(self.image, 'image', image_mock):
            self.assertEqual(self.image.small_preview_url, 'foo')
