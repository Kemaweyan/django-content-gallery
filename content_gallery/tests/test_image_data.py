from django.test import mock, TestCase

from .. import image_data
from .. import utils

from .base_test_cases import MockImageTestCase


class TestImageFile(MockImageTestCase):
    """
    Tests for the ImageFile and inherited methods from
    the BaseImageData base class
    """

    def setUp(self):
        """
        Creates a new mock ImageFile object for each test
        """
        super().setUp()
        self.image_file = mock.MagicMock(spec=image_data.ImageFile)

    def test_init(self):
        """
        Checks whether the object contains correct values
        after instantiation
        """
        # call the constructor with known arguments
        image_file = image_data.ImageFile(
            self.image,
            100,
            50,
            'bar'
        )
        # check whether the name has a corect value
        self.assertEqual(image_file.name, 'foo.jpg')
        # check whether the suffix has a corect value
        self.assertEqual(image_file.suffix, 'bar')
        # check whether the width has a corect value
        self.assertEqual(image_file.size[0], 100)
        # check whether the height has a corect value
        self.assertEqual(image_file.size[1], 50)

    def test_set_name_with_path(self):
        """
        Checks whether the _set_name method sets a basename only
        if it has been called with an argument containing a path
        """
        # call _set_name with a path
        image_data.ImageFile._set_name(self.image_file, 'gallery/bar.jpg')
        # check whether the name contains the basename from the path
        self.assertEqual(self.image_file.name, 'bar.jpg')

    def test_set_name_without_path(self):
        """
        Checks whether the _set_name method sets a name from the argument
        if it has been called without a path
        """
        # call _set_name without a path
        image_data.ImageFile._set_name(self.image_file, 'bar.jpg')
        # check whether the name contains the name from the argument
        self.assertEqual(self.image_file.name, 'bar.jpg')

    def test_create_filename_with_path(self):
        """
        Checks whether the _create_filename method returns a name with
        the suffix if it has been called with an argument containing a path
        """
        # set a suffix
        self.image_file.suffix = 'bar'
        # call _create_filename with a path
        name = image_data.ImageFile._create_filename(
            self.image_file,
            'gallery/foo.jpg'
        )
        # check whether the suffix has been added properly
        self.assertEqual(name, 'gallery/foo_bar.jpg')

    def test_create_filename_without_path(self):
        """
        Checks whether the _create_filename method returns a name with
        the suffix if it has been called with an argument without a path
        """
        # set a suffix
        self.image_file.suffix = 'bar'
        # call _create_filename without a path
        name = image_data.ImageFile._create_filename(
            self.image_file,
            'foo.jpg'
        )
        # check whether the suffix has been added properly
        self.assertEqual(name, 'foo_bar.jpg')

    def test_filename_property(self):
        """
        Checks whether the filename property returns a result of
        the _create_filename method called with the name as an argument
        """
        # set a name
        self.image_file.name = 'bar'
        # create a mock for the method
        mock_func = mock.MagicMock(return_value='foo')
        # set the mock to the _create_filename attribute
        self.image_file._create_filename = mock_func
        # check whether the property returns a result of 
        # the _create_filename method
        self.assertEqual(
            image_data.ImageFile.filename.fget(self.image_file),
            'foo'
        )
        # check whether the _create_filename method has been called
        # with the name as an argument
        mock_func.assert_called_with('bar')

    def test_path_property(self):
        """
        Checks whether the path property returns a result of
        the utils.create_path helper function called with
        the name as an argument
        """
        # set a name
        self.image_file.filename = 'bar'
        # patch the helper function
        with mock.patch.object(
            utils,
            'create_path',
            return_value='foo'
        ) as create_path:
            # check whether the property returns a result of 
            # the helper function
            self.assertEqual(
                image_data.ImageFile.path.fget(self.image_file),
                'foo'
            )
            # check whether the helper function has been called
            # with the name as an argument
            create_path.assert_called_with('bar')

    def test_url_property(self):
        """
        Checks whether the url property returns a result of
        the utils.create_url helper function called with
        the name as an argument
        """
        # set a name
        self.image_file.filename = 'bar'
        # patch the helper function
        with mock.patch.object(
            utils,
            'create_url',
            return_value='foo'
        ) as create_url:
            # check whether the property returns a result of 
            # the helper function
            self.assertEqual(
                image_data.ImageFile.url.fget(self.image_file),
                'foo'
            )
            # check whether the helper function has been called
            # with the name as an argument
            create_url.assert_called_with('bar')

    def test_change_ext(self):
        """
        Checks whether the _change_ext method changes an extension to
        another one from given file name and does not affect the name
        """
        # set an image name
        self.image_file.name = 'foo.jpg'
        # call the _change_ext method with an argument containing another ext
        image_data.ImageFile._change_ext(self.image_file, 'bar.png')
        # check whether the ext on the name changed properly
        # but the name has not been changed
        self.assertEqual(self.image_file.name, 'foo.png')

    def test_save_adding_new_image(self):
        """
        Checks whether the save method creates a new image with a name
        constructed from a slug and an exit of given image data object while
        saving a new image. It should not call delete, _rename_files and
        _change_ext methods.
        """
        # set a name of uploaded image (the image has been uploaded)
        self.image.name = 'foo.jpg'
        # set the same name to the image file object
        self.image_file.name = self.image.name
        # patch utils.get_ext helper function
        with mock.patch.object(
            utils,
            'get_ext',
            return_value='.jpg'
        ) as get_ext:
            # call the save method with a slug and without old name
            # it happens when a new image is being added
            image_data.ImageFile.save(self.image_file, self.image, 'bar', '')
            # check whether the helper function has been called
            # with the image name
            get_ext.assert_called_with('foo.jpg')
        # check whether the _set_name method has been called
        # with old empty name
        self.image_file._set_name.assert_called_with('')
        # check whether the name has been constructed from the slug and
        # the ext of given image file
        self.assertEqual(self.image_file.name, 'bar.jpg')
        # check whether the _create_image method has been called
        # with the image file
        self.image_file._create_image.assert_called_with(self.image)
        # check whether delete, _rename_files and _change_ext methods
        # have not been called since there were not old files
        self.image_file.delete.assert_not_called()
        self.image_file._rename_file.assert_not_called()
        self.image_file._change_ext.assert_not_called()

    def test_save_changing_image_file(self):
        """
        Checks whether the save method creates a new image with an old file
        name and an ext of the new image while changing an image file. 
        The old files should be deleted. It should not call _rename_files
        method.
        """
        # set an image name without slash (the image has been uploaded)
        self.image.name = 'foo.jpg'
        # set a name of existing image object
        self.image_file.name = 'gallery/bar.jpg'
        # patch utils.get_ext helper function
        with mock.patch.object(
            utils,
            'get_ext',
            return_value='.jpg'
        ) as get_ext:
            # call the save method without slug and with old name
            # it happens when image file is being changed
            image_data.ImageFile.save(
                self.image_file,
                self.image,
                '',
                'gallery/bar.jpg'
            )
            # check whether the helper function has not been called
            get_ext.assert_not_called()
        # check whether the _set_name method has been called
        # with the old image name
        self.image_file._set_name.assert_called_with('gallery/bar.jpg')
        # check whether the delete method has been called
        self.image_file.delete.assert_called_with()
        # check whether the name has not been changed
        self.assertEqual(self.image_file.name, 'gallery/bar.jpg')
        # check whether the _change_ext method has been called
        # with the name of uploaded image
        self.image_file._change_ext.assert_called_with(self.image.name)
        # check whether the _create_image method has been called
        # with the uploaded image
        self.image_file._create_image.assert_called_with(self.image)
        # check whether the _rename_files method has not been called
        self.image_file._rename_file.assert_not_called()

    def test_save_changing_related_object(self):
        """
        Checks whether the save method creates a new name using given slug
        and the ext of existing image files. It should rename existing files.
        It should not delete files, change the ext and create new image files
        """
        # the name of mock image object already set to 'gallery/foo.jpg'
        # it contains a slash (the image has not been uploaded)
        # set the same name to the image file object
        self.image_file.name = self.image.name
        # patch utils.get_ext helper function
        with mock.patch.object(
            utils,
            'get_ext',
            return_value='.jpg'
        ) as get_ext:
            # call the save method with a slug and the old image name
            # it happens when the related object is being changed
            # the image is not being changed since a new image has not
            # been uploaded
            image_data.ImageFile.save(
                self.image_file,
                self.image,
                'bar',
                'gallery/foo.jpg'
            )
            # check whether the helper function has been called
            # with the image name
            get_ext.assert_called_with(self.image.name)
        # check whether the _set_name method has been called
        # with the old image name
        self.image_file._set_name.assert_called_with('gallery/foo.jpg')
        # check whether the name has been constructed from a new slug
        # and the old ext
        self.assertEqual(self.image_file.name, 'bar.jpg')
        # check whether the _rename_files method has been called
        # with the new name
        self.image_file._rename_file.assert_called_with('bar.jpg')
        # check whether the delete, _change+_ext and _create_image methods
        # have not been called
        self.image_file.delete.assert_not_called()
        self.image_file._change_ext.assert_not_called()
        self.image_file._create_image.assert_not_called()

    def test_save_changing_image_file_and_related_object(self):
        """
        Checks whether the save method creates new image files with
        a name created from given slug and the ext of uploaded file.
        It should delete old files, but should not rename files and
        change their ext.
        """
        # set an image name without slash (the image has been uploaded)
        self.image.name = 'foo.png'
        # set a name of existing image object
        self.image_file.name = 'gallery/bar.jpg'
        # patch utils.get_ext helper function
        with mock.patch.object(
            utils,
            'get_ext',
            return_value='.png'
        ) as get_ext:
            # call the save method with a slug and the old image name
            # it happens when the related object is being changed
            # the image is being changed as well since a new image has
            # been uploaded
            image_data.ImageFile.save(
                self.image_file,
                self.image,
                'baz',
                'gallery/foo.jpg'
            )
            # check whether the helper function has been called
            # with the uploaded image name
            get_ext.assert_called_with(self.image.name)
        # check whether the _set_name method has been called
        # with the old image name
        self.image_file._set_name.assert_called_with('gallery/foo.jpg')
        # check whether the delete method has been called
        self.image_file.delete.assert_called_with()
        # set whether the name has been constructed from given slug and
        # the ext of uploaded image
        self.assertEqual(self.image_file.name, 'baz.png')
        # check whether the _create_image method has been called
        # with the uploaded image
        self.image_file._create_image.assert_called_with(self.image)
        # check whether the _rename_files and _change_ext methods
        # have not been called since old files have been deleted
        self.image_file._rename_file.assert_not_called()
        self.image_file._change_ext.assert_not_called()

    @mock.patch('os.rename')
    def test_rename_file(self, rename):
        """
        Checks whether the _rename_file method calls the os.rename
        function with proper arguments
        """
        # a mock function to replace the _create_filename method
        mock_func = mock.MagicMock(return_value='baz_bar.jpg')
        self.image_file._create_filename = mock_func
        # set original path
        self.image_file.path = 'gallery/foo_bar.jpg'
        # patch the create_path helper function to return a new path
        with mock.patch.object(
            utils,
            'create_path', 
            return_value='gallery/baz_bar.jpg'
        ) as create_path:
            # call the _rename_files method with a new file name
            image_data.ImageFile._rename_file(self.image_file, 'baz.jpg')
            # check whether the helper function has been called
            # with the result of the _create_filename method
            create_path.assert_called_with('baz_bar.jpg')
        # check whether the mock _create_filename method has been called
        # with the new file name
        mock_func.assert_called_with('baz.jpg')
        # check whether the os.rename function has been called
        # with the original and the new paths
        rename.assert_called_with(
            'gallery/foo_bar.jpg',
            'gallery/baz_bar.jpg'
        )

    @mock.patch('os.remove')
    def test_delete_existing_file(self, remove):
        """
        Checks whether the delete method calls the os.remove
        function with proper argument
        """
        # set image path
        self.image_file.path = 'foo.jpg'
        # call the delete method
        image_data.ImageFile.delete(self.image_file)
        # check whether the os.remove function has been
        # called with the image path
        remove.assert_called_with('foo.jpg')

    @mock.patch('os.remove', side_effect=FileNotFoundError)
    def test_delete_not_existing_file(self, remove):
        """
        Checks whether the delete method calls the os.remove
        function with proper argument and does not raises an
        exception if the file does not exist (os.remove raises
        the FileNotFoundError exception)
        """
        # set image path
        self.image_file.path = 'foo.jpg'
        # call the delete method
        image_data.ImageFile.delete(self.image_file)
        # check whether the os.remove function has been
        # called with the image path and no exception
        # has been raised
        remove.assert_called_with('foo.jpg')

    def test_create_image(self):
        """
        Checks whether the _create_image method calls the utils.image_resize
        helper function with proper arguments
        """
        # set a path and size of the image
        self.image_file.path = 'foo.jpg'
        self.image_file.size = (100, 50)
        # patch the helper function
        with mock.patch.object(utils, 'image_resize') as image_resize:
            # call the _create_image method with the image
            image_data.ImageFile._create_image(self.image_file, self.image)
            # check whether the helper function has been called
            # with the image and its path and size
            image_resize.assert_called_with(self.image, 'foo.jpg', (100, 50))


class TestInMemoryImageData(MockImageTestCase):
    """
    Tests for the InMemoryImageData. Inherited methods from the BaseImageData
    are tested in the TestImageFile class.
    """

    def setUp(self):
        """
        Creates a new mock InMemoryImageData object for each test
        """
        super().setUp()
        self.memory_data = mock.MagicMock(spec=image_data.InMemoryImageData)

    def test_init(self):
        """
        Checks whether the object contains correct values
        after instantiation
        """
        # call the constructor with known arguments
        memory_data = image_data.InMemoryImageData(
            self.image,
            100,
            50
        )
        # check whether the name has a corect value
        self.assertEqual(memory_data.name, 'foo.jpg')
        # check whether the with has a corect value
        self.assertEqual(memory_data.size[0], 100)
        # check whether the height has a corect value
        self.assertEqual(memory_data.size[1], 50)
        # check whether the data is empty
        self.assertIsNone(memory_data.data)

    def test_create_filename_without_path(self):
        """
        Check whether the _create_filename method returns
        given argument without any changes if the argument
        does not contain a path
        """
        # call the _create_filename method without a path
        name = image_data.InMemoryImageData._create_filename(
            self.memory_data,
            'foo.jpg'
        )
        # check whether the returned value equals with given argument
        self.assertEqual(name, 'foo.jpg')

    def test_create_filename_with_path(self):
        """
        Check whether the _create_filename method returns
        given argument without any changes if the argument
        contains a path
        """
        # call the _create_filename method with a path
        name = image_data.InMemoryImageData._create_filename(
            self.memory_data,
            'gallery/foo.jpg'
        )
        # check whether the returned value equals with given argument
        self.assertEqual(name, 'gallery/foo.jpg')

    def test_create_image(self):
        """
        Checks whether the _create_image method calls
        the utils.create_in_memory_image helper function
        with proper arguments 
        """
        # set known name and size
        self.memory_data.name = 'foo.jpg'
        self.memory_data.size = (100, 50)
        # patch the helper function
        with mock.patch.object(
            utils,
            'create_in_memory_image',
            return_value='data'
        ) as create_func:
            # call the _create_image method with the image
            image_data.InMemoryImageData._create_image(
                self.memory_data,
                self.image
            )
            # check whether the helper function has been called
            # with the image and its path and size
            create_func.assert_called_with(self.image, 'foo.jpg', (100, 50))
        # check whether the data is set to returned by helper function value
        self.assertEqual(self.memory_data.data, 'data')

    def test_name_in_db(self):
        """
        Checks whether the name_in_db property returns a result of calling
        the utils.name_in_db helper function
        """
        # set a name
        self.memory_data.name = 'foo.jpg'
        # patch the helper function
        with mock.patch.object(
            utils,
            'name_in_db',
            return_value='gallery/foo.jpg'
        ) as name_in_db:
            # call the property
            name = image_data.InMemoryImageData.name_in_db.fget(
                self.memory_data
            )
            # check whether the helper function has been called with the name
            name_in_db.assert_called_with('foo.jpg')
        # check whether the result equels with returned value
        # of the helper function
        self.assertEqual(name, 'gallery/foo.jpg')
