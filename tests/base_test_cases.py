from django.test import TestCase, mock
from django.contrib.contenttypes.models import ContentType

from .. import models
from .. import settings

from .utils import get_image_in_memory_data, clean_db
from .models import *

class ImageTestCase(TestCase):
    """
    A base test case class for test cases that use one 
    common content object and one unique image per test.
    """

    @classmethod
    def setUpClass(cls):
        """
        Creates common object for all tests
        """
        clean_db()  # delete all objets created by another tests
        # create a content object
        cls.object = TestModel.objects.create(name="TestObject")

    def setUp(self):
        """
        Creates the image object for each test
        """
        # slugify_unique should return 'foo
        # so image names would be just 'foo.jpg'
        with mock.patch.object(
            models,
            'slugify_unique',
            return_value='foo'
        ):
            # create an image attached to the content object
            self.image = models.Image.objects.create(
                image=get_image_in_memory_data(),
                position=0,
                content_type=ContentType.objects.get_for_model(TestModel),
                object_id=self.object.id
            )
        # load created image from the database
        # it's necessary because the Image.image value differs
        # in loaded images (the field adds the path while saving)
        # created image: foo.jpg
        # loaded image: gallery/foo.jpg
        self.image = self.get_image()

    def tearDown(self):
        """
        Removes the image after each test
        """
        self.image.delete()

    @classmethod
    def tearDownClass(cls):
        """
        Removes the common content object when
        all tests has been performed
        """
        cls.object.delete()

    @staticmethod
    def get_image():
        """
        Returns an image loaded from the database
        """
        return models.Image.objects.all()[0]

    @staticmethod
    def get_name(name):
        """
        Returns the name of the image as it is in the database
        """
        return "/".join([settings.CONF['path'], name])


class MultipleObjectsImageTestCase(ImageTestCase):
    """
    A base test case class for tests that require multiple common
    content objects and one unique image per test
    """

    @classmethod
    def setUpClass(cls):
        """
        Creates common objects for all tests.
        """
        super().setUpClass()  # creates the first object
        # create the second onject of the same model
        cls.second_object = TestModel.objects.create(
            name="SecondTestObject"
        )
        # create an object of anther model
        cls.another_object = AnotherTestModel.objects.create(
            name="AnotherTestObject"
        )

    @classmethod
    def tearDownClass(cls):
        """
        Removes the common content objects when
        all tests has been performed
        """
        super().tearDownClass()  # delete the first object
        cls.second_object.delete()
        cls.another_object.delete()


class ViewsTestCase(TestCase):
    """
    A base test case class for test cases that require
    the content object with two related images and one
    alone object without images. All objects are common
    for all tests
    """

    @classmethod
    def setUpClass(cls):
        """
        Creates common objects for all tests.
        """
        clean_db()  # remove all objects created by another tests
        # save the link to the content type
        cls.ctype = ContentType.objects.get_for_model(TestModel)
        # create an object
        cls.object = TestModel.objects.create(name="Test object")
        # create two images related to the object
        cls.image1 = models.Image.objects.create(
            image=get_image_in_memory_data(),
            position=0,
            content_type=cls.ctype,
            object_id=cls.object.id
        )
        cls.image2 = models.Image.objects.create(
            image=get_image_in_memory_data(),
            position=1,
            content_type=cls.ctype,
            object_id=cls.object.id
        )
        # create another object without related images
        cls.alone_object = TestModel.objects.create(
            name="Alone test object"
        )

    @classmethod
    def tearDownClass(cls):
        """
        Removes all objects when all tests has been performed
        """
        cls.image1.delete()
        cls.image2.delete()
        cls.object.delete()
        cls.alone_object.delete()


class MockImageTestCase(TestCase):
    """
    A base test case with a mock image object
    """

    def setUp(self):
        """
        Creates a new mock Image object for each test
        Sets a known name of the image
        """
        self.image = mock.MagicMock(spec=models.Image)
        self.image.name = 'gallery/foo.jpg'


class AjaxRequestMixin:
    """
    A mixin provides emulation of AJAX requests
    """

    def send_ajax_request(self, url):
        """
        Sends a request to a view using built-in HTTP client.
        Views determine these requests as AJAX requests.
        """
        return self.client.get(
            url,
            # emulate sending requests using XMLHttpRequest
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
