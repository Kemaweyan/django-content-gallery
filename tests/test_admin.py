import json

from django.test import mock, TestCase
from django.core.urlresolvers import reverse

from .. import admin
from .. import utils

from .base_test_cases import ViewsTestCase, AjaxRequestMixin

class ImageAdminInline(TestCase):

    def setUp(self):
        self.inline_admin = mock.MagicMock(spec=admin.ImageAdminInline)

    def test_get_queryset(self):
        qs = mock.MagicMock()
        qs.order_by = mock.MagicMock(return_value='bar')
        with mock.patch(
            'django.contrib.contenttypes.admin'
            '.GenericInlineModelAdmin.get_queryset',
            return_value=qs
        ) as get_queryset:
            result = admin.ImageAdminInline.get_queryset(
                self.inline_admin,
                'request'
            )
            get_queryset.assert_called_with('request')
        qs.order_by.assert_called_with('position')

    def test_get_formset(self):
        formset = mock.MagicMock()
        with mock.patch(
            'django.contrib.contenttypes.admin'
            '.GenericInlineModelAdmin.get_formset',
            return_value=formset
        ) as get_formset, mock.patch.object(
            utils,
            'get_admin_new_image_preview_url_pattern',
            return_value='url_pattern'
        ) as get_pattern:
            result = admin.ImageAdminInline.get_formset(
                self.inline_admin,
                'request'
            )
            get_formset.assert_called_with('request', None)
            get_pattern.assert_called()
        self.assertEqual(formset, result)
        self.assertEqual(formset.preview_url_pattern, 'url_pattern')
        


class ImageAdmin(AjaxRequestMixin, ViewsTestCase):

    @staticmethod
    def create_url(pk):
        return reverse('admin:gallery_new_image_preview', args=(pk,))

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = cls.create_url(cls.image1.pk)

    def test_preview_not_ajax(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_preview_not_found(self):
        url = self.create_url(0)
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 404)

    def test_preview_success(self):
        with mock.patch.object(
            utils,
            'create_static_url',
            return_value='foo'
        ) as create_url, mock.patch.object(
            utils,
            'create_image_data',
            return_value='bar'
        ) as create_data:
            resp = self.send_ajax_request(self.url)
            create_url.assert_called_with(
                "content_gallery/img/zoom-small.png"
            )
            create_data.assert_called_with(self.image1)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode("utf-8"))
        self.assertDictEqual(
            data,
            {
                "small_preview_url": self.image1.small_preview_url,
                "position": self.image1.position,
                "image_data": json.dumps('bar'),
                "zoom_url": 'foo',
            }
        )
