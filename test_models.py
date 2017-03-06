from django.test import TestCase

from . import models

class TestMakeSrc(TestCase):

    def test_filename_with_ext(self):
        src = models._make_src('slug', 'file.ext')
        self.assertEqual(src, 'gallery/slug.ext')

    def test_filename_without_ext(self):
        src = models._make_src('slug', 'file')
        self.assertEqual(src, 'gallery/slug')

    def test_without_filename(self):
        src = models._make_src('slug')
        self.assertEqual(src, 'gallery/slug')
