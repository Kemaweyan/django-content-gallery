from .settings import *

INSTALLED_APPS += [
    'content_gallery.tests'
]

TEST_RUNNER = 'content_gallery.tests.runner.GalleryTestSuiteRunner'
