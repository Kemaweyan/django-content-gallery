import shutil
import tempfile

from django.conf import settings
from django.test.runner import DiscoverRunner

class GalleryTestSuiteRunner(DiscoverRunner):
    """
    A custom test suite runner that setups the environment
    creating a temporary directory for test image files
    and deletes them when all tests completed.
    """

    def setup_test_environment(self):
        """
        Setups the environment. Creates a temporary directory
        and saves default the values of environment settings
        """
        super().setup_test_environment()
        # save original settings
        settings._original_media_root = settings.MEDIA_ROOT
        settings._original_file_storage = settings.DEFAULT_FILE_STORAGE
        # create a temporary directory
        self._temp_media = tempfile.mkdtemp()
        # set a new media directory setting
        settings.MEDIA_ROOT = self._temp_media
        # set a file system storage setting
        storage = 'django.core.files.storage.FileSystemStorage'
        settings.DEFAULT_FILE_STORAGE = storage

    def teardown_test_environment(self):
        """
        Deletes all temporary files and the temporary directory.
        Restores original settings.
        """
        super().teardown_test_environment()
        # remove all temporary files
        shutil.rmtree(self._temp_media, ignore_errors=True)
        # restore original settings and delete saved values
        settings.MEDIA_ROOT = settings._original_media_root
        del settings._original_media_root
        settings.DEFAULT_FILE_STORAGE = settings._original_file_storage
        del settings._original_file_storage
