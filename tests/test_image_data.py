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

    #def test_save_
