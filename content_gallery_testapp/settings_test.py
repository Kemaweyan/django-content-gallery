from .settings import *

# add the tests app

INSTALLED_APPS += [
    'content_gallery.tests'
]

# set custom test runner that creates a tmp folder for test files

TEST_RUNNER = 'content_gallery.tests.runner.GalleryTestSuiteRunner'
