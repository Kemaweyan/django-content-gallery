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

    @override_settings(CONTENT_GALLERY={'image_width': 1024})
    def test_image_width(self):
        imp.reload(settings)
        self.assertEqual(settings.CONF['image_width'], 1024)

    @override_settings(CONTENT_GALLERY={'image_height': 768})
    def test_image_height(self):
        imp.reload(settings)
        self.assertEqual(settings.CONF['image_height'], 768)

    @override_settings(CONTENT_GALLERY={'small_image_width': 800})
    def test_small_image_width(self):
        imp.reload(settings)
        self.assertEqual(settings.CONF['small_image_width'], 800)

    @override_settings(CONTENT_GALLERY={'small_image_height': 600})
    def test_small_image_height(self):
        imp.reload(settings)
        self.assertEqual(settings.CONF['small_image_height'], 600)

    @override_settings(CONTENT_GALLERY={'preview_width': 400})
    def test_preview_width(self):
        imp.reload(settings)
        self.assertEqual(settings.CONF['preview_width'], 400)

    @override_settings(CONTENT_GALLERY={'preview_height': 300})
    def test_preview_height(self):
        imp.reload(settings)
        self.assertEqual(settings.CONF['preview_height'], 300)

    @override_settings(CONTENT_GALLERY={'small_preview_width': 200})
    def test_small_preview_width(self):
        imp.reload(settings)
        self.assertEqual(settings.CONF['small_preview_width'], 200)

    @override_settings(CONTENT_GALLERY={'small_preview_height': 150})
    def test_small_preview_height(self):
        imp.reload(settings)
        self.assertEqual(settings.CONF['small_preview_height'], 150)

    @override_settings(CONTENT_GALLERY={'thumbnail_width': 120})
    def test_thumbnail_width(self):
        imp.reload(settings)
        self.assertEqual(settings.CONF['thumbnail_width'], 120)

    @override_settings(CONTENT_GALLERY={'thumbnail_height': 80})
    def test_thumbnail_height(self):
        imp.reload(settings)
        self.assertEqual(settings.CONF['thumbnail_height'], 80)
