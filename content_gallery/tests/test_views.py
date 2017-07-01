import json

from django.test import TestCase, mock
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from .. import models
from .. import utils
from .. import fields

from .models import *
from .base_test_cases import *
from .utils import get_image_in_memory_data, patch_settings

class TestChoices(AjaxRequestMixin, TestCase):
    """
    Tests for the view returning the list of available objects
    (choices) of the model. Inherits the 'send_ajax_request' method
    """

    @staticmethod
    def create_url(pk):
        """
        A helper method that returns the URL to the view
        """
        return reverse('content_gallery:choices', args=(pk,))

    @classmethod
    def setUpClass(cls):
        """
        Creates two objects of TestModel with gallery_visible=True,
        one object of AnotherTestModel with gallery_visible=False and
        one object of WrongTestModel without the gallery_visible
        """
        cls.obj1 = TestModel.objects.create(name='Test object 1')
        cls.obj2 = TestModel.objects.create(name='Test object 2')
        cls.another_obj = AnotherTestModel.objects.create(
            name='Another object'
        )
        cls.wrong_obj = WrongTestModel.objects.create(name='Wrong object')
        # save the content type of the TestModel
        ctype = ContentType.objects.get_for_model(TestModel)
        # save the URL
        cls.url = cls.create_url(ctype.pk)

    @classmethod
    def tearDownClass(cls):
        """
        Removes all created objects
        """
        cls.obj1.delete()
        cls.obj2.delete()
        cls.another_obj.delete()
        cls.wrong_obj.delete()

    def test_not_ajax(self):
        """
        Checks whether the view returns 403 error
        if the request is not AJAX
        """
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_not_existing_content_type(self):
        """
        Checks whether the view returns 404 error
        if the object does not exist
        """
        url = self.create_url(0)  # an object with id=0 could not exist
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 404)

    def test_wrong_content_type(self):
        """
        Checks whether the view returns 404 error if the object
        has not the 'gallery_visible' attribute
        """
        # get the content type of the WrongTestModel
        ctype = ContentType.objects.get_for_model(WrongTestModel)
        # create the URL with this content type
        url = self.create_url(ctype.pk)
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 404)

    def test_invisible_content_object(self):
        """
        Checks whether the view returns 403 error if the object
        has the 'gallery_visible' attribute set to False
        """
        # get the content type of the AnotherTestModel
        ctype = ContentType.objects.get_for_model(AnotherTestModel)
        # create the URL with this content type
        url = self.create_url(ctype.pk)
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 403)

    def test_correct_response(self):
        """
        Checks whether the view returns correct data if a requested
        model has the 'gallery_visible' attribute set to True
        """
        resp = self.send_ajax_request(self.url)
        self.assertEqual(resp.status_code, 200)
        # decode data
        choices = json.loads(resp.content.decode("utf-8"))
        # create data of the objects
        obj1 = {
            'name': self.obj1.name,
            'id': str(self.obj1.pk)
        }
        obj2 = {
            'name': self.obj2.name,
            'id': str(self.obj2.pk)
        }
        # check whether both objets are in the result
        self.assertIn(obj1, choices)
        self.assertIn(obj2, choices)
        # check whether there are 2 items
        # so only correct objects returned
        self.assertEqual(len(choices), 2)


class TestGalleryData(AjaxRequestMixin, ViewsTestCase):
    """
    Tests for the view returning the list of images related to the
    object. Inherits the TestModel object, two images related to
    that and one another TestModel object that attaches a new
    image to. Also has the 'send_ajax_request' method
    """

    @staticmethod
    def create_url(**kwargs):
        """
        A helper method that returns the URL to the view
        """
        return reverse('content_gallery:gallery_data', kwargs=kwargs)

    @classmethod
    def setUpClass(cls):
        """
        Creates the image related to another object
        """
        super().setUpClass()
        cls.another_image = models.Image.objects.create(
            image=get_image_in_memory_data(),
            position=0,
            content_type=cls.ctype,
            object_id=cls.alone_object.id
        )
        # save the url
        cls.url = cls.create_url(
            app_label='tests',
            content_type=cls.ctype.model,
            object_id=cls.object.pk
        )

    @classmethod
    def tearDownClass(cls):
        """
        Deletes all created objects
        """
        cls.another_image.delete()
        super().tearDownClass()

    def test_not_ajax(self):
        """
        Checks whether the view returns 403 error
        if the request is not AJAX
        """
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_not_existing_content_type(self):
        """
        Checks whether the view returns 404 error
        if the content type does not exist
        """
        url = self.create_url(
            app_label='0',  # a priori not existing app_label
            content_type=self.ctype.model,
            object_id=self.object.pk
        )
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 404)

    def test_not_existing_object(self):
        """
        Checks whether the view returns 404 error
        if requested object does not exist
        """
        url = self.create_url(
            app_label='tests',
            content_type=self.ctype.model,
            object_id=0  # a priori not existing id
        )
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 404)

    def test_correct_response(self):
        """
        Check whether the view returns correct data
        """
        # patch settings to use known values
        with patch_settings(
            {
                'image_width': 1024,
                'image_height': 768,
                'small_image_width': 800,
                'small_image_height': 600,
                'thumbnail_width': 120,
                'thumbnail_height': 80
            }
            # patch the calculate_image_size helper function
            # so that it returns known values
        ), mock.patch.object(
            utils,
            'calculate_image_size',
            return_value=(100, 50)
        ):
            # send a request
            resp = self.send_ajax_request(self.url)
        # check whether the response code is OK
        self.assertEqual(resp.status_code, 200)
        # decode data
        data = json.loads(resp.content.decode("utf-8"))
        # check whether target sizes are correct
        self.assertDictEqual(
            data['image_size'],
            {
                "width": 1024,
                "height": 768
            }
        )
        self.assertDictEqual(
            data['small_image_size'],
            {
                "width": 800,
                "height": 600
            }
        )
        self.assertDictEqual(
            data['thumbnail_size'],
            {
                "width": 120,
                "height": 80
            }
        )
        images = data['images']  # get image list
        # check whether image list contains two related
        # to the object images and their sizes in the correct
        # order (the image1 with position 0 should be the first
        # and the image2 with position 1 should be the second)
        self.assertListEqual(
            images,
            [
                # first image
                {
                    # full-size image URL and its actual size
                    "image": self.image1.image_url,
                    "image_size": {
                        "width": self.image1.image.width,
                        "height": self.image1.image.height
                    },
                    # small image URL and its actual size
                    "small_image": self.image1.small_image_url,
                    "small_image_size": {
                        "width": 100,
                        "height": 50
                    },
                    # thumbnail URL
                    "thumbnail": self.image1.thumbnail_url
                },
                # second image
                {
                    # full-size image URL and its actual size
                    "image": self.image2.image_url,
                    "image_size": {
                        "width": self.image2.image.width,
                        "height": self.image2.image.height
                    },
                    # small image URL and its actual size
                    "small_image": self.image2.small_image_url,
                    "small_image_size": {
                        "width": 100,
                        "height": 50
                    },
                    # thumbnail URL
                    "thumbnail": self.image2.thumbnail_url
                }
            ]
        )

    def test_image_files_do_not_exist(self):
        """
        Checks whether the gallery_data view skips images
        if their image files do not exist.
        """
        # patch the image field in the Image
        # it is an object returned by GalleryImageField.attr_class
        with mock.patch.object(
            fields.GalleryImageField,
            'attr_class'
        ) as field_file:
            # create an object and remove its 'width' attribute
            # it causes raising the AttributeError which is similar
            # to behavior of GalleryImageFieldFile when the image file
            # does not exist
            del field_file().width
            # call the view function
            resp = self.send_ajax_request(self.url)
        # decode JSON response
        data = json.loads(resp.content.decode("utf-8"))
        # check whether the list is empty, i.e. all images have been skipped
        self.assertListEqual(data['images'], [])
