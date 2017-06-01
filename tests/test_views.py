import json

from django.test import TestCase, mock
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from .. import models
from .. import settings
from .. import utils

from .models import *
from .utils import get_image_in_memory_data

class TestChoices(AjaxRequestMixin, TestCase):

    @staticmethod
    def create_url(pk):
        return reverse('gallery:choices', args=(pk,))

    @classmethod
    def setUpClass(cls):
        cls.obj1 = TestModel.objects.create(name='Test object 1')
        cls.obj2 = TestModel.objects.create(name='Test object 2')
        cls.another_obj = AnotherTestModel.objects.create(
            name='Another object'
        )
        cls.wrong_obj = WrongTestModel.objects.create(name='Wrong object')
        ctype = ContentType.objects.get_for_model(TestModel)
        cls.url = cls.create_url(ctype.pk)

    @classmethod
    def tearDownClass(cls):
        cls.obj1.delete()
        cls.obj2.delete()
        cls.another_obj.delete()
        cls.wrong_obj.delete()

    def test_not_ajax(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_not_existing_content_type(self):
        url = self.create_url(0)
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 404)

    def test_wrong_content_type(self):
        ctype = ContentType.objects.get_for_model(WrongTestModel)
        url = self.create_url(ctype.pk)
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 404)

    def test_invisible_content_object(self):
        ctype = ContentType.objects.get_for_model(AnotherTestModel)
        url = self.create_url(ctype.pk)
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 403)

    def test_correct_response(self):
        resp = self.send_ajax_request(self.url)
        self.assertEqual(resp.status_code, 200)
        choices = json.loads(resp.content.decode("utf-8"))
        self.assertEqual(len(choices), 2)
        obj1 = {
            'name': self.obj1.name,
            'id': str(self.obj1.pk)
        }
        obj2 = {
            'name': self.obj2.name,
            'id': str(self.obj2.pk)
        }
        self.assertIn(obj1, choices)
        self.assertIn(obj2, choices)


class TestGalleryData(AjaxRequestMixin, ViewsTestCase):

    @staticmethod
    def create_url(**kwargs):
        return reverse('gallery:gallery_data', kwargs=kwargs)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.another_image = models.Image.objects.create(
            image=get_image_in_memory_data(),
            position=0,
            content_type=cls.ctype,
            object_id=cls.alone_object.id
        )
        cls.url = cls.create_url(
            app_label='tests',
            content_type=cls.ctype.model,
            object_id=cls.object.pk
        )

    @classmethod
    def tearDownClass(cls):
        cls.another_image.delete()
        super().tearDownClass()

    def test_not_ajax(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)

    def test_not_existing_content_type(self):
        url = self.create_url(
            app_label='asjfdasfdsa',
            content_type=self.ctype.model,
            object_id=self.object.pk
        )
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 404)

    def test_not_existing_object(self):
        url = self.create_url(
            app_label='tests',
            content_type=self.ctype.model,
            object_id=0
        )
        resp = self.send_ajax_request(url)
        self.assertEqual(resp.status_code, 404)

    def test_correct_response(self):
        with mock.patch.object(
            utils,
            'calculate_image_size',
            return_value=(100, 100)
        ):
            resp = self.send_ajax_request(self.url)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode("utf-8"))
        self.assertDictEqual(
            data['image_size'],
            {
                "width": settings.GALLERY_IMAGE_WIDTH,
                "height": settings.GALLERY_IMAGE_HEIGHT
            }
        )
        self.assertDictEqual(
            data['small_image_size'],
            {
                "width": settings.GALLERY_SMALL_IMAGE_WIDTH,
                "height": settings.GALLERY_SMALL_IMAGE_HEIGHT
            }
        )
        self.assertDictEqual(
            data['thumbnail_size'],
            {
                "width": settings.GALLERY_THUMBNAIL_WIDTH,
                "height": settings.GALLERY_THUMBNAIL_HEIGHT
            }
        )
        images = data['images']
        self.assertEqual(len(images), 2)
        self.assertListEqual(
            images,
            [
                {
                    "image": self.image1.image_url,
                    "image_size": {
                        "width": self.image1.image.width,
                        "height": self.image1.image.height
                    },
                    "small_image_size": {
                        "width": 100,
                        "height": 100
                    },
                    "small_image": self.image1.small_image_url,
                    "thumbnail": self.image1.thumbnail_url
                },
                {
                    "image": self.image2.image_url,
                    "image_size": {
                        "width": self.image2.image.width,
                        "height": self.image2.image.height
                    },
                    "small_image_size": {
                        "width": 100,
                        "height": 100
                    },
                    "small_image": self.image2.small_image_url,
                    "thumbnail": self.image2.thumbnail_url
                }
            ]
        )
