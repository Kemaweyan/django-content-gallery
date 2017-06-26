import json

from django.test import mock, TestCase
from django.contrib.contenttypes.models import ContentType

from ..templatetags import content_gallery
from .. import models
from .. import utils

from .base_test_cases import ViewsTestCase
from .utils import get_image_in_memory_data, patch_settings


class TestGalleryImageData(ViewsTestCase):
    """
    Tests for a template tag returning the first image object
    related to the content object and JSON data of the object.
    Inherits the content object with two related images and one
    alone object without images
    """

    def test_object_without_images(self):
        """
        Checks whether the tag returns None in the image field
        and an empty JSON object if there is no related images
        """
        # patch the get_first_image helper function so that
        # it returns a None value
        with mock.patch.object(
                utils,
                'get_first_image',
                return_value=None
        ) as get_first_image:
            # call the template tag function with an object
            result = content_gallery.gallery_image_data(self.object)
            # check whether the helper function has been called
            # with the object
            get_first_image.assert_called_with(self.object)
        # check whether the image field in the result is None
        self.assertIsNone(result['image'])
        # decode json data
        data = json.loads(result['data_image'])
        # check whether the data is empty
        self.assertDictEqual(data, {})

    def test_object_with_image(self):
        """
        Checks whether the tag returns the first image and escaped
        JSON data that could not be decoded by json.loads
        """
        # patch the get_first_image helper function so that
        # it returns the image object
        with mock.patch.object(
                utils,
                'get_first_image',
                return_value=self.image1
        ) as get_first_image:
            # call the template tag function with an object
            result = content_gallery.gallery_image_data(self.object)
            # check whether the helper function has been called
            # with the object
            get_first_image.assert_called_with(self.object)
        # check whether the result contains the image
        self.assertEqual(result['image'], self.image1)
        # check whether the JSON data cold not be decoded (is escaped)
        with self.assertRaises(ValueError):
            json.loads(result['data_image'])

    # patch the escape function so that returns its argument without changes
    @mock.patch('django.utils.html.escape', lambda x: x)
    def test_object_with_image_unescaped(self):
        """
        Checks whether the tag returns the first image and data
        of the object containing its app label, content type and
        object id.
        """
        # patch the get_first_image helper function so that
        # it returns the image object
        with mock.patch.object(
                utils,
                'get_first_image',
                return_value=self.image1
        ) as get_first_image:
            # call the template tag function with an object
            result = content_gallery.gallery_image_data(self.object)
            # check whether the helper function has been called
            # with the object
            get_first_image.assert_called_with(self.object)
        # check whether the result contains the image
        self.assertEqual(result['image'], self.image1)
        # decode json data
        data = json.loads(result['data_image'])
        # check whether returned data contains correct values
        self.assertDictEqual(
            data,
            {
                'app_label': self.image1.content_type.app_label,
                'content_type': self.image1.content_type.model,
                'object_id': str(self.image1.object_id)
            }
        )


class TestGalleryPreview(ViewsTestCase):
    """
    Tests for the preview template tag containing the first
    preview image file and a link that opens a gallery view
    Inherits the content object with two related images and
    one alone object without images
    """

    def test_get_context(self):
        """
        Checks whether the template tag function returns the
        context containing values required by the template
        """
        # patch preview size settings
        with patch_settings(
            {
                'preview_width': 400,
                'preview_height': 300
            }
        # patch the gallery_image_data template tag so that
        # it returns known dictionary
        ), mock.patch.object(
                content_gallery,
                'gallery_image_data',
                return_value={'foo': 'bar'}
        ) as gallery_image_data:
            # call the tag with the object
            context = content_gallery.gallery_preview(self.object)
            # check whether the gallery_image_data tag has been called
            # with the object
            gallery_image_data.assert_called_with(self.object)
        # check whether the context dictionary contains all required values
        self.assertDictEqual(
            context,
            {
                # values returned by the gallery_image_data
                'foo': 'bar',
                # the preview size
                'image_width': 400,
                'image_height': 300,
                # size of the preview container
                'div_width': 400 + 14,
                'div_height': 300 + 14,
                # offset of zoom image
                'zoom_left': 400 - 55
            }
        )


class TestGallerySmallPreview(ViewsTestCase):
    """
    Tests for the small preview template tag containing the first
    small preview image file and a link that opens a gallery view
    Inherits the content object with two related images and one
    alone object without images
    """

    def test_get_context(self):
        """
        Checks whether the template tag function returns the
        context containing values required by the template
        """
        # patch preview size settings
        with patch_settings(
            {
                'small_preview_width': 200,
                'small_preview_height': 150
            }
        # patch the gallery_image_data template tag so that
        # it returns known dictionary
        ), mock.patch.object(
                content_gallery,
                'gallery_image_data',
                return_value={'foo': 'bar'}
        ) as gallery_image_data:
            # call the tag with the object
            context = content_gallery.gallery_small_preview(self.object)
            # check whether the gallery_image_data tag has been called
            # with the object
            gallery_image_data.assert_called_with(self.object)
        # check whether the context dictionary contains all required values
        self.assertDictEqual(
            context,
            {
                # values returned by the gallery_image_data
                'foo': 'bar',
                # the small preview size
                'image_width': 200,
                'image_height': 150,
                # size of the small preview container
                'div_width': 200 + 14,
                'div_height': 150 + 14,
                # offset of small zoom image
                'zoom_left': 200 - 15
            }
        )


class TestGalleryDataUrlPattern(TestCase):
    """
    Tests for the template tag returning the pattern of
    URL for getting data of related to the object images
    """

    def test_get_url_pattern(self):
        """
        Checks whether the gallery_data_url_pattern tag
        returns a result of the get_gallery_data_url_pattern
        helper function
        """
        # patch the get_gallery_data_url_pattern helper function
        with mock.patch.object(
            utils,
            'get_gallery_data_url_pattern',
            return_value='url_pattern'
        ) as get_pattern:
            # call the gallery_data_url_pattern tag function
            result = content_gallery.gallery_data_url_pattern()
            # check whether the helper function has been called
            get_pattern.assert_called_with()
        # check whether the tag returns the result
        # of the helper function
        self.assertEqual(result, 'url_pattern')


class TestObfuscateFilter(TestCase):
    """
    Tests for the filter adding .min suffix to given path
    iif the DEBUG mode is off
    """

    def test_obfuscate(self):
        """
        Checks whether the obfuscate filter returns a result
        of the get_obfuscated_file helper function
        """
        # patch the get_obfuscated_file helper function
        with mock.patch.object(
            utils,
            'get_obfuscated_file',
            return_value='path'
        ) as get_obfuscated_file:
            # call the obfuscate filter function
            result = content_gallery.obfuscate('foo')
            # check whether the helper function has been called
            get_obfuscated_file.assert_called_with('foo')
        # check whether the tag returns the result
        # of the helper function
        self.assertEqual(result, 'path')
