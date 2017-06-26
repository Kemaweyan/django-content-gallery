from django.test import mock, TestCase
from django.contrib.contenttypes.models import ContentType

from .. import models
from .. import utils

from .models import *
from .base_test_cases import *
from .utils import get_image_in_memory_data


class TestUniqueSlugCheck(ImageTestCase):
    """
    Tests for the _unique_slug_check function
    The test case inherits a test object created once for
    all tests and an image created for each test
    """

    def test_name_exisits(self):
        """
        Tests whether the _unique_slug_check function returns
        False if there is an image with given name in the database
        """
        # patch the utils.name_in_db helper function
        # it should return the same name as the existing image has
        with mock.patch.object(
            utils,
            'name_in_db',
            return_value='content_gallery/foo.jpg'
        ) as name_in_db:
            # call the function
            result = models._unique_slug_check("foo.jpg", [])
            # check whether result is False
            self.assertFalse(result)
            # check whether the helper function has been called
            # with first argument passed into the _unique_slug_check
            name_in_db.assert_called_once_with("foo.jpg")

    def test_name_does_not_exisit(self):
        """
        Tests whether the _unique_slug_check function returns
        True if there is no image with given name in the database
        """
        # patch the utils.name_in_db helper function
        # it should return a name that does not belong
        # to any image in the database
        with mock.patch.object(
            utils,
            'name_in_db',
            return_value='gallery/bar.jpg'
        ) as name_in_db:
            result = models._unique_slug_check("bar.jpg", [])
            self.assertTrue(result)
            name_in_db.assert_called_once_with("bar.jpg")


class TestImage(MultipleObjectsImageTestCase):
    """
    Tests for the Image model. Inherits three objects created
    once for all tests and an image related to the first object.
    A new image is created for each test. Also the get_name method
    returning the name os an image in the database is inherited.
    """

    def test_create_empty_image(self):
        """
        Checks whether the constructor creates
        an empty image object properly
        """
        # create an empty image object
        image = models.Image()
        # check whether init_type and init_id are None
        self.assertIsNone(image.init_type)
        self.assertIsNone(image.init_id)
        # check whether the image_name is empty
        self.assertEqual(image.image_name, "")

    def test_create_atatched_to_object_image(self):
        """
        Checks whether the constructor fills the related to
        object image attributes properly
        """
        # the image is created by setUp
        # get content_type of the TestModel
        ctype = ContentType.objects.get_for_model(TestModel)
        # get the name of the image
        name = self.get_name('foo.jpg')
        # check whether the image is related to the object
        self.assertEqual(self.image.init_type, ctype)
        self.assertEqual(self.image.init_id, self.object.id)
        # check whether the name of the image equals
        # with the created name
        self.assertEqual(self.image.image_name, name)

    def test_image_str(self):
        """
        Checks whether the __str__ method returns proper value
        """
        # the image is created by setUp
        # check str version of the image
        self.assertEqual(str(self.image), "TestObject photo #1")

    def test_get_position_with_existing_images(self):
        """
        Checks whether the _get_position method sets the position
        value 1 if there is an image with position 0 related
        to the same object
        """
        # create a new image related to the same object
        image = models.Image(
            image=get_image_in_memory_data(),
            position=0,
            content_type=ContentType.objects.get_for_model(TestModel),
            object_id=self.object.id
        )
        # call the get_position method
        image._get_position()
        # check whether the position value is 1
        self.assertEqual(image.position, 1)

    def test_get_position_with_new_object_id(self):
        """
        Checks whether the _get_position method sets the position
        value 0 if there is no image with related to the same object,
        but to another object of the same model
        """
        # create a new image related to another object
        image = models.Image(
            image=get_image_in_memory_data(),
            position=0,
            content_type=ContentType.objects.get_for_model(TestModel),
            object_id=self.second_object.id
        )
        # call the get_position method
        image._get_position()
        # check whether the position value is 1
        self.assertEqual(image.position, 0)

    def test_get_position_with_new_content_type(self):
        """
        Checks whether the _get_position method sets the position
        value 0 if there is no image with related to the same object
        and any other objects of the same model
        """
        # create a new image related to the object of another model 
        image = models.Image(
            image=get_image_in_memory_data(),
            position=0,
            content_type=ContentType.objects.get_for_model(AnotherTestModel),
            object_id=self.another_object.id
        )
        # call the get_position method
        image._get_position()
        # check whether the position value is 0
        self.assertEqual(image.position, 0)

    def test_object_changed_has_not_been_changed(self):
        """
        Checks whether the _object_changed method of just loaded
        image object returns False
        """
        self.assertFalse(self.image._object_changed())

    def test_object_changed_object_id_changed(self):
        """
        Checks whether the _object_changed method of an image object
        with changed object_id returns True
        """
        # change the object_id
        self.image.content_object = self.second_object
        # save image
        self.image.save()
        self.assertTrue(self.image._object_changed())

    def test_object_changed_object_ctype_changed(self):
        """
        Checks whether the _object_changed method of an image object
        with changed content_type returns True
        """
        # change the related object
        self.image.content_object = self.another_object
        # save image
        self.image.save()
        self.assertTrue(self.image._object_changed())

    def test_get_slug(self):
        """
        Checks whether the _get_slug method returns a result
        of the slugify_unique function called with the title
        of the related object as an argument
        """
        # patch the slugify_unique function
        with mock.patch.object(
            models,
            'slugify_unique',
            return_value='foo'
        ) as slugify_unique:
            # check whether the method returns the result
            # of the slugify_unique function
            self.assertEqual('foo', self.image._get_slug())
            # check whether the slugify_unique function has been called
            # with the title of the related object 
            slugify_unique.assert_called_once_with('TestObject')

    def test_save_data_new_image(self):
        """
        Checks whether saving data of a new image creates a new slug
        and sets a position
        """
        # create a new image
        image = models.Image(
            image=get_image_in_memory_data(),
            position=0,
            content_type=ContentType.objects.get_for_model(TestModel),
            object_id=self.object.id
        )
        # use mocks for methods could be called
        image._get_slug = mock.MagicMock(return_value='foo')
        image._get_position = mock.MagicMock()
        image.image.save_files = mock.MagicMock()
        # call the _save_data method
        image._save_data()
        # check whether the _get_slug and the _get_position methods
        # have been called
        image._get_slug.assert_called_once_with()
        image._get_position.assert_called_once_with()
        # check whether the save_files method of the image field
        # has been called with the slug and the name of the image
        image.image.save_files.assert_called_once_with('foo', 'foo.jpg')

    def test_save_data_unchanged_image(self):
        """
        Checks whether saving data of an unchanged image does not call
        the _get_slug and _get_position methods
        """
        # use mocks for methods could be called
        self.image._get_slug = mock.MagicMock()
        self.image._get_position = mock.MagicMock()
        self.image.image.save_files = mock.MagicMock()
        self.image._object_changed = mock.MagicMock(return_value=False)
        # call the _save_data method
        self.image._save_data()
        # check whether the _get_slug and _get_position methods
        # has not been called
        self.image._get_slug.assert_not_called()
        self.image._get_position.assert_not_called()
        # get a name of the image
        name = self.get_name('foo.jpg')
        # check whether the save_files method of the image field
        # has been called with empty slug and the name of the image
        self.image.image.save_files.assert_called_once_with('', name)

    def test_save_data_changed_image(self):
        """
        Checks whether saving data of a changed image creates a new slug
        and sets a position
        """
        # use mocks for methods could be called
        self.image._get_slug = mock.MagicMock(return_value='foo')
        self.image._get_position = mock.MagicMock()
        self.image.image.save_files = mock.MagicMock()
        # object_changed should return True
        self.image._object_changed = mock.MagicMock(return_value=True)
        # call the _save_data method
        self.image._save_data()
        # check whether the _get_slug and the _get_position methods
        # have been called
        self.image._get_slug.assert_called_once_with()
        self.image._get_position.assert_called_once_with()
        # get a name of the image
        name = self.get_name('foo.jpg')
        # check whether the save_files method of the image field
        # has been called with a new slug and the name of the image
        self.image.image.save_files.assert_called_once_with('foo', name)

    def test_delete_files_image(self):
        """
        Checks whether the delete_files method calls the delete_files
        method of the image field
        """
        # set a mock to the method could be called
        self.image.image.delete_files = mock.MagicMock()
        # call the delete_files method
        self.image.delete_files()
        # check whether the delete_files method of the image field
        # has been called
        self.image.image.delete_files.assert_called_once_with()

    def test_thumbnail_url_property(self):
        """
        Checks whether the thumbnail_url property returns a result
        of the thumbnail_url property of the image field
        """
        # mock the image field and set the thumbnail_url value
        image_mock = mock.MagicMock()
        image_mock.thumbnail_url = 'foo'
        # patch the image object
        with mock.patch.object(self.image, 'image', image_mock):
            # check whether the thumbnail_url property returns
            # a value of the thumbnail_url of the mock
            self.assertEqual(self.image.thumbnail_url, 'foo')

    def test_image_url_property(self):
        """
        Checks whether the image_url property returns a result
        of the image_url property of the image field
        """
        # mock the image field and set the image_url value
        image_mock = mock.MagicMock()
        image_mock.image_url = 'foo'
        # patch the image object
        with mock.patch.object(self.image, 'image', image_mock):
            # check whether the image_url property returns
            # a value of the image_url of the mock
            self.assertEqual(self.image.image_url, 'foo')

    def test_preview_url_property(self):
        """
        Checks whether the preview_url property returns a result
        of the preview_url property of the image field
        """
        # mock the image field and set the preview_url value
        image_mock = mock.MagicMock()
        image_mock.preview_url = 'foo'
        # patch the image object
        with mock.patch.object(self.image, 'image', image_mock):
            # check whether the preview_url property returns
            # a value of the preview_url of the mock
            self.assertEqual(self.image.preview_url, 'foo')

    def test_small_image_url_property(self):
        """
        Checks whether the small_image_url property returns a result
        of the small_image_url property of the image field
        """
        # mock the image field and set the small_image_url value
        image_mock = mock.MagicMock()
        image_mock.small_image_url = 'foo'
        # patch the image object
        with mock.patch.object(self.image, 'image', image_mock):
            # check whether the small_image_url property returns
            # a value of the small_image_url of the mock
            self.assertEqual(self.image.small_image_url, 'foo')

    def test_small_preview_url_property(self):
        """
        Checks whether the small_preview_url property returns a result
        of the small_preview_url property of the image field
        """
        # mock the image field and set the small_preview_url value
        image_mock = mock.MagicMock()
        image_mock.small_preview_url = 'foo'
        # patch the image object
        with mock.patch.object(self.image, 'image', image_mock):
            # check whether the small_preview_url property returns
            # a value of the small_preview_url of the mock
            self.assertEqual(self.image.small_preview_url, 'foo')


class TestImageQuerySet(TestCase):
    """
    Tests for ImageQuerySet
    """

    def test_delete(self):
        """
        Tests whether the delete method calls the delete_files
        methods of all contained objects
        """
        # create two mock objects
        obj1 = mock.MagicMock()
        obj2 = mock.MagicMock()
        # create a mock query set object
        query_set = mock.MagicMock(spec=models.ImageQuerySet)
        # the query set iteration yields objects created before
        query_set.__iter__.return_value = [obj1, obj2]
        # patch the delete method of the parent class
        with mock.patch('django.db.models.QuerySet.delete') as delete:
            # call the delete method
            models.ImageQuerySet.delete(query_set)
            # check whether the parent's delete method has been called
            delete.assert_called_with()
        # check whether the delete_files methods
        # of both objects have been called
        obj1.delete_files.assert_called_with()
        obj2.delete_files.assert_called_with()
