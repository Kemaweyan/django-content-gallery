from django.test import mock, TestCase
from django.contrib.contenttypes.admin import GenericInlineModelAdmin

from .. import admin

class ImageAdminInline(TestCase):

    def test_get_queryset(self):
        inline_admin = mock.MagicMock(spec=admin.ImageAdminInline)
        qs = mock.MagicMock()
        qs.order_by = mock.MagicMock(return_value='bar')
        with mock.patch.object(
            GenericInlineModelAdmin,
            'get_queryset',
            return_value=qs
        ) as get_queryset:
            result = admin.ImageAdminInline.get_queryset(inline_admin, 'foo')
            get_queryset.assert_called_with('foo')
        qs.order_by.assert_called_with('position')
