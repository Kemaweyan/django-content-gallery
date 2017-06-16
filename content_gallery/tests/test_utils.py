import os

from django.test import TestCase, mock, override_settings
from django.conf import settings as django_settings

from .. import utils

from .utils import create_image_file, get_image_size, patch_settings
from .base_test_cases import ViewsTestCase

class TestPatterns(TestCase):
    """
    Tests for helper functions that return various URL patterns
    """

    def test_get_choices_url_pattern(self):
        """
        Checks whether the get_choices_url_pattern function
        returns correct URL pattern for getting a list of
        objects (choices) of the model
        """
        url = utils.get_choices_url_pattern()
        self.assertRegex(url, r'^/\w+/ajax/choices/$')

    def test_get_gallery_data_url_pattern(self):
        """
        Checks whether the get_gallery_data_url_pattern function
        returns correct URL pattern for getting data of all images
        related to the object
        """
        url = utils.get_gallery_data_url_pattern()
        self.assertRegex(url, r'^/\w+/ajax/gallery_data/$')

    def test_get_admin_new_image_preview_url_pattern(self):
        """
        Checks whether the get_admin_new_image_preview_url_pattern
        function returns correct URL pattern for getting data of
        preview the image in admin
        """
        url = utils.get_admin_new_image_preview_url_pattern()
        self.assertRegex(url, r'^/admin/\w+/image/ajax/preview/$')


class TestCalculateImageSize(TestCase):
    """
    Tests for the calculate_image_size function
    """

    # a target image size, the result image
    # should not be larger than these values
    target_size = (100, 100)

    def test_larger_width(self):
        """
        Checks whether an image with width larger than height
        is resized in a way that width becomes to target width
        and height is changed proportionally
        """
        # resize 200x100 image with 100x100 target
        size = utils.calculate_image_size((200, 100), self.target_size)
        # check whether the size has been calculated properly
        self.assertEqual(size[0], 100)  # 200 -> 100 (target)
        self.assertEqual(size[1], 50)  # 100 -> 50 (proportionally)

    def test_larger_height(self):
        """
        Checks whether an image with height larger than width
        is resized in a way that height becomes to target height
        and width is changed proportionally
        """
        # resize 100x200 image with 100x100 target
        size = utils.calculate_image_size((100, 200), self.target_size)
        # check whether the size has been calculated properly
        self.assertEqual(size[0], 50)  # 100 -> 50 (proportionally)
        self.assertEqual(size[1], 100)  # 200 -> 100 (target)

    def test_larger_size(self):
        """
        Checks whether a larger image is resized to the target size
        """
        # resize 200x200 image with 100x100 target
        size = utils.calculate_image_size((200, 200), self.target_size)
        # check whether the size has been calculated properly
        self.assertEqual(size[0], 100)  # 200 -> 100 (target)
        self.assertEqual(size[1], 100)  # 200 -> 100 (target)

    def test_same_size(self):
        """
        Checks whether an image with the target size is not affected
        """
        # resize 100x100 image with 100x100 target
        size = utils.calculate_image_size(self.target_size, self.target_size)
        # check whether the size has been calculated properly
        self.assertEqual(size[0], 100)  # 100 -> 100 (target)
        self.assertEqual(size[1], 100)  # 100 -> 100 (target)

    def test_smaller_size(self):
        """
        Checks whether a smaller image is not affected
        """
        # resize 50x50 image with 100x100 target
        size = utils.calculate_image_size((50, 50), self.target_size)
        # check whether the size has been calculated properly
        self.assertEqual(size[0], 50)
        self.assertEqual(size[1], 50)


class TestFilenameUtils(TestCase):
    """
    Tests for helper functions manipulating with file names
    """

    def test_get_ext_single(self):
        """
        Checks whether the get_ext function returns a correct
        file extension if the filename contains a single dot
        """
        ext = utils.get_ext('foo.jpg')
        self.assertEqual(ext, '.jpg')

    def test_get_ext_double(self):
        """
        Checks whether the get_ext function returns a correct
        file extension if the filename contains two dots
        """
        ext = utils.get_ext('foo.bar.jpg')
        self.assertEqual(ext, '.jpg')

    def test_get_ext_none(self):
        """
        Checks whether the get_ext function returns an empty
        file extension if the filename contains no dot
        """
        ext = utils.get_ext('filename')
        self.assertEqual(ext, '')

    def test_get_ext_path(self):
        """
        Checks whether the get_ext function returns a correct
        file extension if the filename contains a path
        """
        ext = utils.get_ext('/path/to/foo.jpg')
        self.assertEqual(ext, '.jpg')

    def test_get_name_single(self):
        """
        Checks whether the get_name function returns a correct
        file name without its extension if the filename contains
        a single dot
        """
        name = utils.get_name('foo.jpg')
        self.assertEqual(name, 'foo')

    def test_get_name_double(self):
        """
        Checks whether the get_name function returns a correct
        file name without its extension if the filename contains
        two dots
        """
        name = utils.get_name('foo.bar.jpg')
        self.assertEqual(name, 'foo.bar')

    def test_get_filename_none(self):
        """
        Checks whether the get_name function returns a correct
        file name without extension if the filename contains no dot
        """
        name = utils.get_name('foo')
        self.assertEqual(name, 'foo')

    def test_get_name_path(self):
        """
        Checks whether the get_name function returns a correct
        file name without extension if the filename contains a path
        """
        name = utils.get_name('/path/to/foo.jpg')
        self.assertEqual(name, '/path/to/foo')

    @override_settings(MEDIA_ROOT='/media')
    def test_create_path(self):
        """
        Checks whether the create_path function returns a correct
        path if the MEDIA_ROOT contains a beginning slash only and
        the 'path' setting contains no slashes
        """
        with patch_settings({'path': 'gallery'}):
            path = utils.create_path('foo.jpg')
        self.assertEqual(path, '/media/gallery/foo.jpg')

    @override_settings(MEDIA_ROOT='/media/')
    def test_create_path_right_slash_in_media_root(self):
        """
        Checks whether the create_path function returns a correct
        path if the MEDIA_ROOT contains both slashes and the 'path'
        setting contains no slashes
        """
        with patch_settings({'path': 'gallery'}):
            path = utils.create_path('foo.jpg')
        self.assertEqual(path, '/media/gallery/foo.jpg')

    @override_settings(MEDIA_ROOT='/media')
    def test_create_path_slash_in_gallery_path(self):
        """
        Checks whether the create_path function returns a correct
        path if the MEDIA_ROOT contains a beginning slash only and
        the 'path' setting contains an ending slash
        """
        with patch_settings({'path': 'gallery/'}):
            path = utils.create_path('foo.jpg')
        self.assertEqual(path, '/media/gallery/foo.jpg')

    @override_settings(MEDIA_ROOT='/media/')
    def test_create_path_slash_in_both(self):
        """
        Checks whether the create_path function returns a correct
        path if the MEDIA_ROOT contains both slashes and the 'path'
        setting contains an ending slash
        """
        with patch_settings({'path': 'gallery/'}):
            path = utils.create_path('foo.jpg')
        self.assertEqual(path, '/media/gallery/foo.jpg')

    @override_settings(MEDIA_URL='/media/')
    def test_create_url(self):
        """
        Checks whether the create_url function returns a correct
        URL if 'path' setting contains no slashes
        """
        with patch_settings({'path': 'gallery'}):
            url = utils.create_url('foo.jpg')
        self.assertEqual(url, '/media/gallery/foo.jpg')

    @override_settings(MEDIA_URL='/media/')
    def test_create_url_left_slash_in_gallery_path(self):
        """
        Checks whether the create_url function returns a correct
        URL if 'path' setting contains a beginning slash
        """
        with patch_settings({'path': '/gallery'}):
            url = utils.create_url('foo.jpg')
        self.assertEqual(url, '/media/gallery/foo.jpg')

    @override_settings(MEDIA_URL='/media/')
    def test_create_url_right_slash_in_gallery_path(self):
        """
        Checks whether the create_url function returns a correct
        URL if 'path' setting contains an ending slash
        """
        with patch_settings({'path': 'gallery/'}):
            url = utils.create_url('foo.jpg')
        self.assertEqual(url, '/media/gallery/foo.jpg')

    @override_settings(MEDIA_URL='/media/')
    def test_create_url_slashes_in_gallery_path(self):
        """
        Checks whether the create_url function returns a correct
        URL if 'path' setting contains both slashes
        """
        with patch_settings({'path': '/gallery/'}):
            url = utils.create_url('foo.jpg')
        self.assertEqual(url, '/media/gallery/foo.jpg')

    def test_create_name_in_db(self):
        """
        Checks whether the name_in_db function returns a correct
        name as it is in the database (path + filename) of the
        'path' setting contains no slashes
        """
        with patch_settings({'path': 'gallery'}):
            name = utils.name_in_db('foo.jpg')
        self.assertEqual(name, 'gallery/foo.jpg')

    def test_create_name_in_db_right_slash(self):
        """
        Checks whether the name_in_db function returns a correct
        name as it is in the database (path + filename) of the
        'path' setting contains an ending slash
        """
        with patch_settings({'path': 'gallery/'}):
            name = utils.name_in_db('foo.jpg')
        self.assertEqual(name, 'gallery/foo.jpg')

    @override_settings(STATIC_URL='/static/')
    def test_create_static_url_result(self):
        """
        Checks whether the create_static_url function creates
        a correct URL
        """
        # patch the get_obfuscated_file function so that it returns
        # given value without changes
        with mock.patch.object(utils, 'get_obfuscated_file', lambda x: x):
            name = utils.create_static_url('gallery/foo.jpg')
        self.assertEqual(name, '/static/gallery/foo.jpg')

    @override_settings(STATIC_URL='/static/')
    def test_create_static_url_obfuscation_call(self):
        """
        Checks whether the create_static_url function calls
        the get_obfuscated_file function with a correct URL
        """
        # patch the get_obfuscated_file function
        with mock.patch.object(
            utils,
            'get_obfuscated_file',
            return_value="foo"
        ) as obfuscation:
            name = utils.create_static_url('gallery/foo.jpg')
            # check whether the get_obfuscated_file function
            # has been called with a correct URL
            obfuscation.assert_called_with('/static/gallery/foo.jpg')
        # check whether the create_static_url function returns
        # a result of the get_obfuscated_file function
        self.assertEqual(name, 'foo')


class TestImageUtils(TestCase):
    """
    Tests for functions manipulating with image data
    """

    # a path to the tmp image file
    image_path = os.path.join(django_settings.MEDIA_ROOT, 'foo.jpg')

    def setUp(self):
        """
        Creates a new 100x100 image for each test
        """
        create_image_file(self.image_path)

    def tearDown(self):
        """
        Deletes an image after each test
        """
        os.remove(self.image_path)

    def test_resize_image_same_size(self):
        """
        Checks whether the image_resize function keeps the size of the image
        without changes if the image size equals the target size
        """
        # resize 100x100 image with target size 100x100
        utils.image_resize(self.image_path, self.image_path, (100, 100))
        # get size of the image after resizing
        size = get_image_size(self.image_path)
        # check whether the result size if correct
        self.assertEqual(size[0], 100)  # 100 -> 100
        self.assertEqual(size[1], 100)  # 100 -> 100

    def test_resize_image_smaller_width(self):
        """
        Checks whether the image_resize function keeps an aspect ratio
        of the image if the target width is lesser than width of the image
        """
        # resize 100x100 image with target size 50x100
        utils.image_resize(self.image_path, self.image_path, (50, 100))
        # get size of the image after resizing
        size = get_image_size(self.image_path)
        # check whether the result size if correct
        self.assertEqual(size[0], 50)  # 100 -> 50
        self.assertEqual(size[1], 50)  # 100 -> 50

    def test_resize_image_smaller_height(self):
        """
        Checks whether the image_resize function keeps an aspect ratio
        of the image if the target height is lesser than height of the image
        """
        # resize 100x100 image with target size 100x50
        utils.image_resize(self.image_path, self.image_path, (100, 50))
        # get size of the image after resizing
        size = get_image_size(self.image_path)
        # check whether the result size if correct
        self.assertEqual(size[0], 50)  # 100 -> 50
        self.assertEqual(size[1], 50)  # 100 -> 50

    def test_resize_image_smaller_size(self):
        """
        Checks whether the image_resize function resizes the image properly
        if both target dimesions are lesser than the image size
        """
        # resize 100x100 image with target size 50x50
        utils.image_resize(self.image_path, self.image_path, (50, 50))
        # get size of the image after resizing
        size = get_image_size(self.image_path)
        # check whether the result size if correct
        self.assertEqual(size[0], 50)  # 100 -> 50
        self.assertEqual(size[1], 50)  # 100 -> 50

    def test_create_in_memory_image(self):
        """
        Checks whether the create_in_memory_image function resizes the image
        and stores it in the memory properly
        """
        # create an image data from 100x100 image with target size 50x50
        img = utils.create_in_memory_image(self.image_path, 'foo', (50, 50))
        # get size of the image data after resizing
        size = get_image_size(img)
        self.assertEqual(img.name, 'foo')
        # check whether the result size if correct
        self.assertEqual(size[0], 50)  # 100 -> 50
        self.assertEqual(size[1], 50)  # 100 -> 50



class TestCreateImageData(TestCase):
    """
    Tests for the create_image_data function that should return
    URLs and sizes of the full-size and the small image files
    """

    def test_create_image_data(self):
        """
        Checks whether the create_image_data function returns
        correct data
        """
        # create a mock image with known values of the urls
        image = mock.MagicMock()
        image.image_url = 'foo'
        image.small_image_url = 'bar'
        # patch settings so that set known sizes
        with patch_settings(
            {
                'image_width': 1024,
                'image_height': 768,
                'small_image_width': 800,
                'small_image_height': 600
            }
        ):
            # call the create_image_data function
            data = utils.create_image_data(image)
        # check whether the full-size image URL is correct
        self.assertEqual(data['image']['url'], 'foo')
        # check whether the full-size image size is correct
        self.assertEqual(data['image']['width'], 1024)
        self.assertEqual(data['image']['height'], 768)
        # check whether the small image URL is correct
        self.assertEqual(data['small_image']['url'], 'bar')
        # check whether the small image size is correct
        self.assertEqual(data['small_image']['width'], 800)
        self.assertEqual(data['small_image']['height'], 600)


class TestGetFirstImage(ViewsTestCase):
    """
    Tests for the get_first_image function. It should return the
    first image from ordered by position list of related to
    the object images.
    The test case inherits the TestModel object, two images related
    to that and one another TestModel object without related images
    """

    def test_get_image(self):
        """
        Checks whether the get_first_image function returns the image
        with position 0 if there is also the image with position 1
        """
        # call the function with the object
        img = utils.get_first_image(self.object)
        # check whether the get_first_image returns
        # an image with the smallest position
        self.assertEquals(self.image1, img)

    def test_get_image_change_order(self):
        """
        Checks whether the get_first_image function returns the image
        with position 1 if there is also the image with position 2
        """
        # set a new position
        self.image1.position = 2
        # save changes to the database
        self.image1.save()
        # call the function with the object
        img = utils.get_first_image(self.object)
        # check whether the get_first_image returns
        # an image with the smallest position
        self.assertEquals(self.image2, img)

    def test_get_image_none(self):
        """
        Checks whether the get_first_image function returns None
        if there is no images related to the object
        """
        # call the function with the alone object
        img = utils.get_first_image(self.alone_object)
        # check whether the returned value is None
        self.assertIsNone(img)


class TestGetObfuscatedFile(TestCase):
    """
    Tests for the get_obfuscated_file function. It should return
    the file name with the '.min' suffix if the DEBUG mode is off
    or given filename without changes if the DEBUG mode is on
    """

    @override_settings(DEBUG=True)
    def test_debug_mode(self):
        """
        Checks whether the get_obfuscated_file function does not
        affect the file name without a path if the DEBUG mode is on
        """
        js = utils.get_obfuscated_file('foo.js')
        self.assertEqual(js, 'foo.js')

    @override_settings(DEBUG=True)
    def test_debug_mode_with_path(self):
        """
        Checks whether the get_obfuscated_file function does not
        affect the file name with a path if the DEBUG mode is on
        """
        js = utils.get_obfuscated_file('foo/bar.js')
        self.assertEqual(js, 'foo/bar.js')

    @override_settings(DEBUG=False)
    def test_non_debug_mode(self):
        """
        Checks whether the get_obfuscated_file function adds the '.min'
        suffix to the file name without a path if the DEBUG mode is off
        """
        js = utils.get_obfuscated_file('foo.js')
        self.assertEqual(js, 'foo.min.js')

    @override_settings(DEBUG=False)
    def test_non_debug_mode_with_path(self):
        """
        Checks whether the get_obfuscated_file function adds the '.min'
        suffix to the file name with a path if the DEBUG mode is off
        """
        js = utils.get_obfuscated_file('foo/bar.js')
        self.assertEqual(js, 'foo/bar.min.js')
