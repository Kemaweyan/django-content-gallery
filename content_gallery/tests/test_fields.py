import os

from django.test import mock, override_settings

from .. import fields
from .. import models
from .. import image_data

from .base_test_cases import ImageTestCase
from .utils import patch_settings

class TestGalleryImageFieldFile(ImageTestCase):
    """
    Tests for GalleryImageFieldFile. Inherits a TestModel object
    and an image related to that, The image is unique per test
    """

    def setUp(self):
        """
        Creates a GalleryImageFieldFile object with known values
        for each test. Saves used mocks of the InMemoryImageData
        and ImageFile classes.
        """
        super().setUp()
        # patch classes used to manipulate with image data
        with mock.patch.object(image_data, 'InMemoryImageData') as m:
            with mock.patch.object(image_data, 'ImageFile') as f:
                # set known settings
                with patch_settings(
                    {
                        'image_width': 1024,
                        'image_height': 768,
                        'small_image_width': 800,
                        'small_image_height': 600,
                        'preview_width': 400,
                        'preview_height': 300,
                        'small_preview_width': 200,
                        'small_preview_height': 150,
                        'thumbnail_width': 120,
                        'thumbnail_height': 80
                    }
                ):
                    # create the object
                    self.field_file = fields.GalleryImageFieldFile(
                        self.image,
                        mock.MagicMock(),
                        str(self.image)
                    )
            # save mocks of called classes
            self.image_file = f
            self.in_memory_data = m

    def test_init(self):
        """
        Checks whether all objets has been created properly
        """
        # check whether the full-size image objects has been created properly
        self.in_memory_data.assert_any_call(
            self.field_file,
            1024,
            768
        )
        # check whether the small image objects has been created properly
        self.image_file.assert_any_call(
            self.field_file,
            800,
            600,
            'small'
        )
        # check whether the preview objects has been created properly
        self.image_file.assert_any_call(
            self.field_file,
            400,
            300,
            'preview'
        )
        # check whether the small preview objects has been created properly
        self.image_file.assert_any_call(
            self.field_file,
            200,
            150,
            'small_preview'
        )
        # check whether the thumbnail objects has been created properly
        self.image_file.assert_any_call(
            self.field_file,
            120,
            80,
            'thumbnail'
        )

    # set known media root
    @override_settings(MEDIA_ROOT='/media')
    @mock.patch('os.mkdir')
    # emulate an existence of the directory
    @mock.patch('os.path.isdir', return_value=True)
    def test_check_dir_exists(self, isdir, mkdir):
        """
        Checks whether the mkdir is not called if the directory exists
        """
        # create known path
        path = '/media' + os.sep + 'gallery'
        # patch settings to set known path
        with patch_settings({'path': 'gallery'}):
            self.field_file._check_dir()
        # check whether isdir has been called with the path
        isdir.assert_called_with(path)
        # check whether mkdir has not been called
        mkdir.assert_not_called()

    # set known media root
    @override_settings(MEDIA_ROOT='/media')
    @mock.patch('os.mkdir')
    # emulate an absence of the directory
    @mock.patch('os.path.isdir', return_value=False)
    def test_check_dir_does_not_exist(self, isdir, mkdir):
        """
        Checks whether the mkdir is called with the path
        if the directory does not exist
        """
        # create known path
        path = '/media' + os.sep + 'gallery'
        # patch settings to set known path
        with patch_settings({'path': 'gallery'}):
            self.field_file._check_dir()
        # check whether isdir has been called with the path
        isdir.assert_called_with(path)
        # check whether mkdir has been called with the path
        mkdir.assert_called_with(path)

    def test_save_files_image_data_exists(self):
        """
        Checks whether save methods of image objects are
        called properly and the name has not been changed
        if data exists
        """
        # replace creation of the directory
        self.field_file._check_dir = mock.MagicMock()
        # data exists
        self.field_file.image_data.data = True
        # set known name in the database
        self.field_file.image_data.name_in_db = 'foo'
        # call the method with known arguments
        self.field_file.save_files('bar', 'baz')

        # check whether the _check_dir has been called
        self.field_file._check_dir.assert_called_with()
        # check whether the save methods of all image objects
        # has been called with the arguments passed to tested method
        self.field_file.image_data.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.thumbnail.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.preview.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.small_preview.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.small_image.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        # check whether the name equals with the image name
        self.assertEqual(self.field_file.name, str(self.image))

    def test_save_files_image_data_does_not_exist(self):
        """
        Checks whether save methods of image objects are
        called properly and the name has been set to the
        name in the database
        """
        # replace creation of the directory
        self.field_file._check_dir = mock.MagicMock()
        # data does not exist
        self.field_file.image_data.data = None
        # set known name in the database
        self.field_file.image_data.name_in_db = 'foo'
        # call the method with known arguments
        self.field_file.save_files('bar', 'baz')

        # check whether the _check_dir has been called
        self.field_file._check_dir.assert_called_with()
        # check whether the save methods of all image objects
        # has been called with the arguments passed to tested method
        self.field_file.image_data.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.thumbnail.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.preview.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.small_preview.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        self.field_file.small_image.save.assert_called_with(
            self.field_file,
            'bar',
            'baz'
        )
        # check whether the name has been set to the name in the database
        self.assertEqual(self.field_file.name, 'foo')

    def test_delete_files(self):
        """
        Checks whether the delete method of all image objects
        has been called
        """
        # call the method
        self.field_file.delete_files()
        # check whether all delete methods has been called
        self.field_file.image_data.delete.assert_called_with()
        self.field_file.thumbnail.delete.assert_called_with()
        self.field_file.preview.delete.assert_called_with()
        self.field_file.small_preview.delete.assert_called_with()
        self.field_file.small_image.delete.assert_called_with()

    def test_thumbnail_url(self):
        """
        Checks whether returned value is the value of containing
        'thumbnail' object
        """
        # get url
        url = self.field_file.thumbnail_url
        # check whether values are equal
        self.assertEqual(url, self.field_file.thumbnail.url)

    def test_image_url(self):
        """
        Checks whether returned value is the value of containing
        'image' object
        """
        # get url
        url = self.field_file.image_url
        # check whether values are equal
        self.assertEqual(url, self.field_file.image_data.url)

    def test_small_image_url(self):
        """
        Checks whether returned value is the value of containing
        'small_image' object
        """
        # get url
        url = self.field_file.small_image_url
        # check whether values are equal
        self.assertEqual(url, self.field_file.small_image.url)

    def test_preview_url(self):
        """
        Checks whether returned value is the value of containing
        'preview' object
        """
        # get url
        url = self.field_file.preview_url
        # check whether values are equal
        self.assertEqual(url, self.field_file.preview.url)

    def test_small_preview_url(self):
        """
        Checks whether returned value is the value of containing
        'small_preview' object
        """
        # get url
        url = self.field_file.small_preview_url
        # check whether values are equal
        self.assertEqual(url, self.field_file.small_preview.url)
