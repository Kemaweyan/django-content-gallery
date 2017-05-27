from django.test import mock, TestCase
from unittest import skip

from .. import image_data

class MockImageTestCase(TestCase):

    def setUp(self):
        self.image = mock.MagicMock()
        self.image.name = 'gallery/foo.jpg'


class TestImageFile(MockImageTestCase):

    def setUp(self):
        super().setUp()
        self.image_file = mock.MagicMock(spec=image_data.ImageFile)

    def test_init(self):
        image_file = image_data.ImageFile(
            self.image,
            100,
            50,
            'bar'
        )
        self.assertEqual(image_file.name, 'foo.jpg')
        self.assertEqual(image_file.word, 'bar')
        self.assertEqual(image_file.size[0], 100)
        self.assertEqual(image_file.size[1], 50)

    def test_set_name_with_path(self):
        image_data.ImageFile._set_name(self.image_file, 'gallery/bar.jpg')
        self.assertEqual(self.image_file.name, 'bar.jpg')

    def test_set_name_without_path(self):
        image_data.ImageFile._set_name(self.image_file, 'bar.jpg')
        self.assertEqual(self.image_file.name, 'bar.jpg')

    def test_create_filename_with_path(self):
        self.image_file.word = 'bar'
        name = image_data.ImageFile._create_filename(
            self.image_file,
            'gallery/foo.jpg'
        )
        self.assertEqual(name, 'gallery/foo_bar.jpg')

    def test_create_filename_without_path(self):
        self.image_file.word = 'bar'
        name = image_data.ImageFile._create_filename(
            self.image_file,
            'foo.jpg'
        )
        self.assertEqual(name, 'foo_bar.jpg')

    def test_filename_property(self):
        self.image_file.name = 'bar'
        mock_func = mock.MagicMock(return_value='foo')
        self.image_file._create_filename = mock_func
        self.assertEqual(
            image_data.ImageFile.filename.fget(self.image_file),
            'foo'
        )
        mock_func.assert_called_with('bar')

    @mock.patch('gallery.utils.create_path', return_value='foo')
    def test_path_property(self, create_path):
        self.image_file.filename = 'bar'
        self.assertEqual(
            image_data.ImageFile.path.fget(self.image_file),
            'foo'
        )
        create_path.assert_called_with('bar')

    @mock.patch('gallery.utils.create_url', return_value='foo')
    def test_url_property(self, create_url):
        self.image_file.filename = 'bar'
        self.assertEqual(
            image_data.ImageFile.url.fget(self.image_file),
            'foo'
        )
        create_url.assert_called_with('bar')

    def test_change_ext(self):
        self.image_file.name = 'foo.jpg'
        image_data.ImageFile._change_ext(self.image_file, 'bar.png')
        self.assertEqual(self.image_file.name, 'foo.png')

    @mock.patch('gallery.utils.get_ext', return_value='.jpg')
    def test_save_new_image(self, get_ext):
        self.image.name = 'foo.jpg'
        self.image_file.name = self.image.name
        image_data.ImageFile.save(self.image_file, self.image, 'bar', '')
        self.image_file._set_name.assert_called_with('')
        self.image_file.delete.assert_not_called()
        get_ext.assert_called_with('foo.jpg')
        self.assertEqual(self.image_file.name, 'bar.jpg')
        self.image_file._rename_file.assert_not_called()
        self.image_file._change_ext.assert_not_called()
        self.image_file._create_image.assert_called_with(self.image)

    @mock.patch('gallery.utils.get_ext', return_value='.jpg')
    def test_save_image_with_new_file(self, get_ext):
        self.image.name = 'foo.jpg'
        self.image_file.name = 'gallery/bar.jpg'
        image_data.ImageFile.save(
            self.image_file,
            self.image,
            '',
            self.image.name
        )
        self.image_file._set_name.assert_called_with(self.image.name)
        self.image_file.delete.assert_called()
        get_ext.assert_not_called()
        self.assertEqual(self.image_file.name, 'gallery/bar.jpg')
        self.image_file._rename_file.assert_not_called()
        self.image_file._change_ext.assert_called_with(self.image.name)
        self.image_file._create_image.assert_called_with(self.image)

    @mock.patch('gallery.utils.get_ext', return_value='.jpg')
    def test_save_image_change_content_object(self, get_ext):
        self.image_file.name = 'gallery/foo.jpg'
        image_data.ImageFile.save(
            self.image_file,
            self.image,
            'bar',
            self.image.name
        )
        self.image_file._set_name.assert_called_with(self.image.name)
        self.image_file.delete.assert_not_called()
        get_ext.assert_called_with(self.image.name)
        self.assertEqual(self.image_file.name, 'bar.jpg')
        self.image_file._rename_file.assert_called_with('bar.jpg')
        self.image_file._change_ext.assert_not_called()
        self.image_file._create_image.assert_not_called()

    @mock.patch('gallery.utils.get_ext', return_value='.jpg')
    def test_save_image_with_new_file_change_content_object(self, get_ext):
        self.image.name = 'foo.jpg'
        self.image_file.name = 'gallery/bar.jpg'
        image_data.ImageFile.save(
            self.image_file,
            self.image,
            'baz',
            self.image.name
        )
        self.image_file._set_name.assert_called_with(self.image.name)
        self.image_file.delete.assert_called()
        get_ext.assert_not_called()
        self.assertEqual(self.image_file.name, 'baz.jpg')
        self.image_file._rename_file.assert_not_called()
        self.image_file._change_ext.assert_not_called()
        self.image_file._create_image.assert_called_with(self.image)

    @mock.patch('os.rename')
    @mock.patch(
        'gallery.utils.create_path', 
        return_value='gallery/baz_bar.jpg'
    )
    def test_rename_file(self, create_path, rename):
        mock_func = mock.MagicMock(return_value='baz_bar.jpg')
        self.image_file._create_filename = mock_func
        self.image_file.path = 'gallery/foo_bar.jpg'
        image_data.ImageFile._rename_file(self.image_file, 'baz.jpg')
        mock_func.assert_called_with('baz.jpg')
        create_path.assert_called_with('baz_bar.jpg')
        rename.assert_called_with(
            'gallery/foo_bar.jpg',
            'gallery/baz_bar.jpg'
        )

    @mock.patch('os.remove')
    def test_delete_existing_file(self, remove):
        self.image_file.path = 'foo.jpg'
        image_data.ImageFile.delete(self.image_file)
        remove.assert_called_with('foo.jpg')

    @mock.patch('os.remove', side_effect=FileNotFoundError)
    def test_delete_not_existing_file(self, remove):
        self.image_file.path = 'foo.jpg'
        image_data.ImageFile.delete(self.image_file)
        remove.assert_called_with('foo.jpg')

    @mock.patch('gallery.utils.image_resize')
    def test_create_image(self, image_resize):
        self.image_file.path = 'foo.jpg'
        self.image_file.size = (100, 50)
        image_data.ImageFile._create_image(self.image_file, self.image)
        image_resize.assert_called_with(self.image, 'foo.jpg', (100, 50))


class TestInMemoryImageData(MockImageTestCase):

    def setUp(self):
        super().setUp()
        self.memory_data = mock.MagicMock(spec=image_data.InMemoryImageData)

    def test_init(self):
        memory_data = image_data.InMemoryImageData(
            self.image,
            100,
            50
        )
        self.assertEqual(memory_data.name, 'foo.jpg')
        self.assertEqual(memory_data.size[0], 100)
        self.assertEqual(memory_data.size[1], 50)
        self.assertIsNone(memory_data.data)

    def test_create_filename_without_path(self):
        name = image_data.InMemoryImageData._create_filename(
            self.memory_data,
            'foo.jpg'
        )
        self.assertEqual(name, 'foo.jpg')

    def test_create_filename_with_path(self):
        name = image_data.InMemoryImageData._create_filename(
            self.memory_data,
            'gallery/foo.jpg'
        )
        self.assertEqual(name, 'gallery/foo.jpg')

    @mock.patch('gallery.utils.create_in_memory_image', return_value='data')
    def test_create_image(self, create_func):
        self.memory_data.name = 'foo.jpg'
        self.memory_data.size = (100, 50)
        image_data.InMemoryImageData._create_image(
            self.memory_data,
            self.image
        )
        self.assertEqual(self.memory_data.data, 'data')
        create_func.assert_called_with(self.image, 'foo.jpg', (100, 50))

    @mock.patch('gallery.utils.name_in_db', return_value='gallery/foo.jpg')
    def test_name_in_db(self, name_in_db):
        self.memory_data.name = 'foo.jpg'
        name = image_data.InMemoryImageData.name_in_db.fget(self.memory_data)
        self.assertEqual(name, 'gallery/foo.jpg')
        name_in_db.assert_called_with('foo.jpg')
