import shutil
import tempfile

from django.conf import settings as global_sett
from django.test.runner import DiscoverRunner

from .. import settings

class CustomTestSuiteRunner(DiscoverRunner):

    def setup_test_environment(self):
        super().setup_test_environment()
        global_sett._original_media_root = global_sett.MEDIA_ROOT
        global_sett._original_file_storage = global_sett.DEFAULT_FILE_STORAGE
        self._temp_media = tempfile.mkdtemp()
        global_sett.MEDIA_ROOT = self._temp_media
        settings.MEDIA_ROOT = self._temp_media
        global_sett.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    def teardown_test_environment(self):
        super().teardown_test_environment()
        shutil.rmtree(self._temp_media, ignore_errors=True)
        global_sett.MEDIA_ROOT = global_sett._original_media_root
        settings.MEDIA_ROOT = global_sett._original_media_root
        del global_sett._original_media_root
        global_sett.DEFAULT_FILE_STORAGE = global_sett._original_file_storage
        del global_sett._original_file_storage
