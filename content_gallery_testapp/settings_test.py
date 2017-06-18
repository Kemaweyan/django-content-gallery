from .settings import *

ROOT_URLCONF = 'content_gallery_testapp.urls'

INSTALLED_APPS += [
    'content_gallery.tests'
]

TEST_RUNNER = 'content_gallery.tests.runner.GalleryTestSuiteRunner'
