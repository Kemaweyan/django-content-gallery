import json

from django.test import mock, TestCase
from django.contrib.contenttypes.models import ContentType

from ..templatetags import content_gallery
from .. import models
from .. import settings

from .models import ViewsTestCase
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
        with mock.patch.object(
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
                'image_width': settings.CONF['preview_width'],
                'image_height': settings.CONF['preview_height'],
                'div_width': settings.CONF['preview_width'] + 14,
                'div_height': settings.CONF['preview_height'] + 14,
                'zoom_left': settings.CONF['preview_width'] - 55
            }
        )


class TestGallerySmallPreview(ViewsTestCase):

    def test_get_context(self):
        with mock.patch.object(
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
                'image_width': settings.CONF['small_preview_width'],
                'image_height': settings.CONF['small_preview_height'],
                'div_width': settings.CONF['small_preview_width'] + 14,
                'div_height': settings.CONF['small_preview_height'] + 14,
                'zoom_left': settings.CONF['small_preview_width'] - 15
            }
        )
