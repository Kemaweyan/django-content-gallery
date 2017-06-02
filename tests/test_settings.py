import imp

from django.test import TestCase, override_settings
from django.core.exceptions import ImproperlyConfigured

from .. import settings

class TestSettings(TestCase):

    @override_settings(MEDIA_ROOT=None)
    def test_without_media_root(self):
        with self.assertRaises(ImproperlyConfigured):
            imp.reload(settings)

    @override_settings(MEDIA_URL=None)
    def test_without_media_url(self):
        with self.assertRaises(ImproperlyConfigured):
            imp.reload(settings)
