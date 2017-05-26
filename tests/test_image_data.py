from django.test import mock, TestCase

from .. import image_data

class TestImageFile(TestCase):

    def setUp(self):
        self.image = mock.MagicMock()
        self.image.name = 'gallery/foo.jpg'
        self.image_file = image_data.ImageFile(
            self.image,
            100,
            50,
            'bar'
        )

    def tearDown(self):
        self.image_file.delete()

    def test_init(self):
        self.assertEqual(self.image_file.name, 'foo.jpg')
        self.assertEqual(self.image_file.word, 'bar')
        self.assertEqual(self.image_file.size[0], 100)
        self.assertEqual(self.image_file.size[1], 50)

    def test_set_name_with_path(self):
        self.image_file._set_name('gallery/bar.jpg')
        self.assertEqual(self.image_file.name, 'bar.jpg')

    def test_set_name_without_path(self):
        self.image_file._set_name('bar.jpg')
        self.assertEqual(self.image_file.name, 'bar.jpg')

    def test_create_filename_with_path(self):
        name = self.image_file._create_filename('gallery/foo.jpg')
        self.assertEqual(name, 'gallery/foo_bar.jpg')

    def test_create_filename_without_path(self):
        name = self.image_file._create_filename('foo.jpg')
        self.assertEqual(name, 'foo_bar.jpg')

    def test_filename_property(self):
        mock_func = mock.MagicMock(return_value='foo')
        self.image_file._create_filename = mock_func
        self.assertEqual(self.image_file.filename, 'foo')
        mock_func.assert_called_with(self.image_file.name)

    @mock.patch('gallery.utils.create_path', return_value='foo')
    def test_path_property(self, create_path):
        with mock.patch('gallery.image_data.ImageFile.filename',
                new_callable=mock.PropertyMock(return_value='bar')):
            self.assertEqual(self.image_file.path, 'foo')
            create_path.assert_called_with('bar')

    @mock.patch('gallery.utils.create_url', return_value='foo')
    def test_url_property(self, create_url):
        with mock.patch('gallery.image_data.ImageFile.filename',
                new_callable=mock.PropertyMock(return_value='bar')):
            self.assertEqual(self.image_file.url, 'foo')
            create_url.assert_called_with('bar')

    def test_change_ext(self):
        self.image_file._change_ext('bar.png')
        self.assertEqual(self.image_file.name, 'foo.png')

    @mock.patch('gallery.utils.get_ext', return_value='.jpg')
    def test_save_new_image(self, get_ext):
        self.image.name = 'foo.jpg'
        image_file = mock.MagicMock()
        image_file.name = self.image.name
        image_data.ImageFile.save(image_file, self.image, 'bar', '')
        image_file._set_name.assert_called_with('')
        image_file.delete.assert_not_called()
        get_ext.assert_called_with('foo.jpg')
        self.assertEqual(image_file.name, 'bar.jpg')
        image_file._rename_file.assert_not_called()
        image_file._change_ext.assert_not_called()
        image_file._create_image.assert_called_with(self.image)

    @mock.patch('gallery.utils.get_ext', return_value='.jpg')
    def test_save_image_with_new_file(self, get_ext):
        self.image.name = 'foo.jpg'
        image_file = mock.MagicMock()
        image_file.name = 'gallery/bar.jpg'
        image_data.ImageFile.save(image_file, self.image, '', self.image.name)
        image_file._set_name.assert_called_with(self.image.name)
        image_file.delete.assert_called()
        get_ext.assert_not_called()
        self.assertEqual(image_file.name, 'gallery/bar.jpg')
        image_file._rename_file.assert_not_called()
        image_file._change_ext.assert_called_with(self.image.name)
        image_file._create_image.assert_called_with(self.image)

    @mock.patch('gallery.utils.get_ext', return_value='.jpg')
    def test_save_image_change_content_object(self, get_ext):
        image_file = mock.MagicMock()
        image_file.name = 'gallery/foo.jpg'
        image_data.ImageFile.save(image_file, self.image, 'bar', self.image.name)
        image_file._set_name.assert_called_with(self.image.name)
        image_file.delete.assert_not_called()
        get_ext.assert_called_with(self.image.name)
        self.assertEqual(image_file.name, 'bar.jpg')
        image_file._rename_file.assert_called_with('bar.jpg')
        image_file._change_ext.assert_not_called()
        image_file._create_image.assert_not_called()

    @mock.patch('gallery.utils.get_ext', return_value='.jpg')
    def test_save_image_with_new_file_change_content_object(self, get_ext):
        self.image.name = 'foo.jpg'
        image_file = mock.MagicMock()
        image_file.name = 'gallery/bar.jpg'
        image_data.ImageFile.save(image_file, self.image, 'baz', self.image.name)
        image_file._set_name.assert_called_with(self.image.name)
        image_file.delete.assert_called()
        get_ext.assert_not_called()
        self.assertEqual(image_file.name, 'baz.jpg')
        image_file._rename_file.assert_not_called()
        image_file._change_ext.assert_not_called()
        image_file._create_image.assert_called_with(self.image)

    @mock.patch('os.rename')
    @mock.patch('gallery.utils.create_path', return_value='gallery/baz_bar.jpg')
    def test_rename_file(self, create_path, rename):
        mock_func = mock.MagicMock(return_value='baz_bar.jpg')
        self.image_file._create_filename = mock_func
        with mock.patch('gallery.image_data.ImageFile.path',
                new_callable=mock.PropertyMock(return_value='gallery/foo_bar.jpg')):
            self.image_file._rename_file('baz.jpg')
        mock_func.assert_called_with('baz.jpg')
        create_path.assert_called_with('baz_bar.jpg')
        rename.assert_called_with('gallery/foo_bar.jpg', 'gallery/baz_bar.jpg')

    @mock.patch('os.remove')
    def test_delete_existing_file(self, remove):
        with mock.patch('gallery.image_data.ImageFile.path',
                new_callable=mock.PropertyMock(return_value='foo.jpg')):
            self.image_file.delete()
        remove.assert_called_with('foo.jpg')

    @mock.patch('os.remove', side_effect=FileNotFoundError)
    def test_delete_not_existing_file(self, remove):
        with mock.patch('gallery.image_data.ImageFile.path',
                new_callable=mock.PropertyMock(return_value='foo.jpg')):
            self.image_file.delete()
        remove.assert_called_with('foo.jpg')

    def test_create_filename_with_path(self):
        name = self.image_file._create_filename('gallery/foo.jpg')
        self.assertEqual(name, 'gallery/foo_bar.jpg')

    def test_create_filename_without_path(self):
        name = self.image_file._create_filename('foo.jpg')
        self.assertEqual(name, 'foo_bar.jpg')

    @mock.patch('gallery.utils.image_resize')
    def test_create_image(self, image_resize):
        image_file = mock.MagicMock()
        image_file.path = 'foo.jpg'
        image_file.size = (100, 50)
        image_data.ImageFile._create_image(image_file, self.image)
        image_resize.assert_called_with(self.image, 'foo.jpg', (100, 50))
