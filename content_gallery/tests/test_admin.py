import json

from django.test import mock, TestCase
from django.core.urlresolvers import reverse

from .. import admin
from .. import utils

from .base_test_cases import ViewsTestCase, AjaxRequestMixin

class TestImageAdminInline(TestCase):
    """
    Tests for the inline Image admin
    """

    def setUp(self):
        """
        Creates a mock object passed to methods of 
        the ImageAdminInline for each test
        """
        self.inline_admin = mock.MagicMock(spec=admin.ImageAdminInline)

    def test_get_queryset(self):
        """
        Checks whether images in the query set are sorted by position
        """
        qs = mock.MagicMock()  # mock object returned by parent's method
        # create order_by method
        qs.order_by = mock.MagicMock(return_value='bar')
        # patch parent class to return the mock
        with mock.patch(
            'django.contrib.contenttypes.admin'
            '.GenericInlineModelAdmin.get_queryset',
            return_value=qs
        ) as get_queryset:
            # call method being tested with the mock ImageAdminInline
            result = admin.ImageAdminInline.get_queryset(
                self.inline_admin,
                'request'
            )
            # check whether the parent's method has been called
            # with the same argument
            get_queryset.assert_called_with('request')
        # check whether the order_by method has been called
        # with the 'position' str as an argument
        qs.order_by.assert_called_with('position')
        # check whether the method returns the result of the 'order_by'
        self.assertEqual(result, 'bar')

    def test_get_formset(self):
        """
        Checks whether the formset has the 'preview_url_pattern'
        attribute containing the URL pattern
        """
        # the mock object returned by parent's method
        formset = mock.MagicMock()
        # patch parent class to return the mock
        with mock.patch(
            'django.contrib.contenttypes.admin'
            '.GenericInlineModelAdmin.get_formset',
            return_value=formset
            # patch the helper function to return known value
        ) as get_formset, mock.patch.object(
            utils,
            'get_admin_new_image_preview_url_pattern',
            return_value='url_pattern'
        ) as get_pattern:
            # call the method being tested with the mock ImageAdminInline
            result = admin.ImageAdminInline.get_formset(
                self.inline_admin,
                'request'
            )
            # check whether parent's method has been called
            # with the same argument
            get_formset.assert_called_with('request', None)
            # check whether the helper function has been called
            get_pattern.assert_called_with()
        # check whether the method returns the result of parent's method
        self.assertEqual(formset, result)
        # check whether the 'preview_url_pattern' of returned object
        # has the correct value
        self.assertEqual(formset.preview_url_pattern, 'url_pattern')
        


class TestImageAdmin(AjaxRequestMixin, ViewsTestCase):
    """
    Tests for the Image admin. Inherits the TestModel object, two
    images related to that and one another TestModel object without
    related images. Also has the 'send_ajax_request' method
    """

    @staticmethod
    def create_url(pk):
        """
        Returns the URL of the 'gallery_new_image_preview' view
        """
        return reverse('admin:gallery_new_image_preview', args=(pk,))

    @classmethod
    def setUpClass(cls):
        """
        Creates and saves the URL to the view
        """
        super().setUpClass()
        cls.url = cls.create_url(cls.image1.pk)

    def test_preview_not_ajax(self):
        """
        Checks whether the view returns 403 error in response
        to non-AJAX requests
        """
        # send a normal request
        resp = self.client.get(self.url)
        # check whether the response code is 403
        self.assertEqual(resp.status_code, 403)

    def test_preview_not_found(self):
        """
        Checks whether the view returns 404 error if the object
        does not exist
        """
        # create URL with non-existing pk (0 could not exist)
        url = self.create_url(0)
        # send an AJAX request
        resp = self.send_ajax_request(url)
        # check whether the response code is 404
        self.assertEqual(resp.status_code, 404)

    def test_preview_success(self):
        """
        Checks whether the view returns correct data
        """
        # patch the helper functions to return known values
        with mock.patch.object(
            utils,
            'create_static_url',
            return_value='foo'
        ) as create_url, mock.patch.object(
            utils,
            'create_image_data',
            return_value='bar'
        ) as create_data:
            # send an AJAX request
            resp = self.send_ajax_request(self.url)
            # check whether the 'create_static_url' has been called
            # to create a URL to the small zoom image
            create_url.assert_called_with(
                "content_gallery/img/zoom-small.png"
            )
            # check whether the 'create_image_data' has been called
            # to get data of the first image
            create_data.assert_called_with(self.image1)
        # check whether the response code is 200
        self.assertEqual(resp.status_code, 200)
        # decode the response
        data = json.loads(resp.content.decode("utf-8"))
        # check whether the returned data is correct
        self.assertDictEqual(
            data,
            {
                "small_preview_url": self.image1.small_preview_url,
                "position": self.image1.position,
                "image_data": json.dumps('bar'),  # the data also is encoded
                "zoom_url": 'foo',
            }
        )
