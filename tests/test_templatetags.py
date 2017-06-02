import json

from django.test import mock, TestCase
from django.contrib.contenttypes.models import ContentType

from ..templatetags import content_gallery
from .. import models

from .base_test_cases import ViewsTestCase
from .utils import get_image_in_memory_data, patch_settings

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


class TestGalleryImageData(ViewsTestCase):

    def test_object_without_images(self):
        with mock.patch.object(
                content_gallery,
                'get_first_image',
                return_value=None
        ) as get_first_image:
            result = content_gallery.gallery_image_data(self.object)
            get_first_image.assert_called_with(self.object)
        self.assertIsNone(result['image'])
        data = json.loads(result['data_image'])
        self.assertDictEqual(data, {})

    def test_object_with_image(self):
        with mock.patch.object(
                content_gallery,
                'get_first_image',
                return_value=self.image1
        ) as get_first_image:
            result = content_gallery.gallery_image_data(self.object)
            get_first_image.assert_called_with(self.object)
        self.assertEqual(result['image'], self.image1)
        with self.assertRaises(ValueError):
            json.loads(result['data_image'])

    @mock.patch('django.utils.html.escape', lambda x: x)
    def test_object_with_image_unescaped(self):
        with mock.patch.object(
                content_gallery,
                'get_first_image',
                return_value=self.image1
        ) as get_first_image:
            result = content_gallery.gallery_image_data(self.object)
            get_first_image.assert_called_with(self.object)
        self.assertEqual(result['image'], self.image1)
        data = json.loads(result['data_image'])
        self.assertDictEqual(
            data,
            {
                'app_label': self.image1.content_type.app_label,
                'content_type': self.image1.content_type.model,
                'object_id': str(self.image1.object_id)
            }
        )


class TestGalleryPreview(ViewsTestCase):

    def test_get_context(self):
        with patch_settings(
            {
                'preview_width': 400,
                'preview_height': 300
            }
        ), mock.patch.object(
                content_gallery,
                'gallery_image_data',
                return_value={'foo': 'bar'}
        ) as gallery_image_data:
            context = content_gallery.gallery_preview(self.object)
            gallery_image_data.assert_called_with(self.object)
        self.assertDictEqual(
            context,
            {
                'foo': 'bar',
                'image_width': 400,
                'image_height': 300,
                'div_width': 400 + 14,
                'div_height': 300 + 14,
                'zoom_left': 400 - 55
            }
        )


class TestGallerySmallPreview(ViewsTestCase):

    def test_get_context(self):
        with patch_settings(
            {
                'small_preview_width': 200,
                'small_preview_height': 150
            }
        ), mock.patch.object(
                content_gallery,
                'gallery_image_data',
                return_value={'foo': 'bar'}
        ) as gallery_image_data:
            context = content_gallery.gallery_small_preview(self.object)
            gallery_image_data.assert_called_with(self.object)
        self.assertDictEqual(
            context,
            {
                'foo': 'bar',
                'image_width': 200,
                'image_height': 150,
                'div_width': 200 + 14,
                'div_height': 150 + 14,
                'zoom_left': 200 - 15
            }
        )
