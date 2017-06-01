import os

from django.test import mock, TestCase
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms as django_forms

from .. import forms
from .. import models
from .. import settings

from .models import TestModel
from .utils import get_image_in_memory_data, create_image_file

class TestImageAdminForm(TestCase):

    image_path = os.path.join(settings.MEDIA_ROOT, 'foo.jpg')

    @classmethod
    def setUpClass(cls):
        create_image_file(cls.image_path)
        cls.ctype = ContentType.objects.get_for_model(TestModel)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.image_path)

    def setUp(self):
        self.form = mock.MagicMock(spec=forms.ImageAdminForm)
        self.form.fields = {}
        field = mock.MagicMock()
        field.widget.model_class = None
        self.form.fields['object_id'] = field

    def test_valid_form(self):
        upload_file = open(self.image_path, 'rb')
        post_dict = {
            'position': 0,
            'content_type': self.ctype.pk,
            'object_id': 1
        }
        file_dict = {
            'image': SimpleUploadedFile(upload_file.name, upload_file.read())
        }
        form = forms.ImageAdminForm(post_dict, file_dict)
        self.assertTrue(form.is_valid())

    def test_invalid_form_without_image(self):
        post_dict = {
            'position': 0,
            'content_type': self.ctype.pk,
            'object_id': 1
        }
        form = forms.ImageAdminForm(post_dict)
        self.assertFalse(form.is_valid())

    def test_invalid_form_without_content_type(self):
        upload_file = open(self.image_path, 'rb')
        post_dict = {
            'position': 0,
            'object_id': 1
        }
        file_dict = {
            'image': SimpleUploadedFile(upload_file.name, upload_file.read())
        }
        form = forms.ImageAdminForm(post_dict, file_dict)
        self.assertFalse(form.is_valid())

    def test_invalid_form_without_object_id(self):
        upload_file = open(self.image_path, 'rb')
        post_dict = {
            'position': 0,
            'content_type': self.ctype.pk
        }
        file_dict = {
            'image': SimpleUploadedFile(upload_file.name, upload_file.read())
        }
        form = forms.ImageAdminForm(post_dict, file_dict)
        self.assertFalse(form.is_valid())

    def test_valid_form_without_position(self):
        upload_file = open(self.image_path, 'rb')
        post_dict = {
            'content_type': self.ctype.pk,
            'object_id': 1
        }
        file_dict = {
            'image': SimpleUploadedFile(upload_file.name, upload_file.read())
        }
        form = forms.ImageAdminForm(post_dict, file_dict)
        self.assertTrue(form.is_valid())

    def test_create_empty_form(self):
        form = forms.ImageAdminForm()
        self.assertIsNone(form.fields['object_id'].widget.model_class)
        self.assertNotIsInstance(
            form.fields['content_type'].widget,
            django_forms.HiddenInput
        )
        self.assertNotIsInstance(
            form.fields['object_id'].widget,
            django_forms.HiddenInput
        )

    def test_create_empty_form_popup(self):
        form = forms.ImageAdminForm(initial={'_popup': True})
        self.assertIsInstance(
            form.fields['content_type'].widget,
            django_forms.HiddenInput
        )
        self.assertIsInstance(
            form.fields['object_id'].widget,
            django_forms.HiddenInput
        )

    def test_create_form_with_instance(self):
        obj = TestModel.objects.create(name='Test object')
        image = models.Image.objects.create(
            image=get_image_in_memory_data(),
            position=0,
            content_type=ContentType.objects.get_for_model(TestModel),
            object_id=obj.id
        )
        form = forms.ImageAdminForm(instance=image)
        self.assertEqual(
            form.fields['object_id'].widget.model_class,
            TestModel
        )
        image.delete()
        obj.delete()

    def test_clean_unbounded(self):
        self.form.is_bound = False
        with mock.patch.object(
            django_forms.ModelForm,
            'clean',
            return_value='foo'
        ) as clean:
            result = forms.ImageAdminForm.clean(self.form)
            clean.assert_called()
            self.assertEqual(result, 'foo')
        self.assertIsNone(self.form.fields['object_id'].widget.model_class)

    def test_clean_bounded_without_content_type(self):
        self.form.is_bound = True
        with mock.patch.object(
            django_forms.ModelForm,
            'clean',
            return_value={}
        ) as clean:
            result = forms.ImageAdminForm.clean(self.form)
            clean.assert_called()
            self.assertEqual(result, {})
        self.assertIsNone(self.form.fields['object_id'].widget.model_class)

    def test_clean_bounded_with_content_type(self):
        self.form.is_bound = True
        data = {'content_type': self.ctype}
        with mock.patch.object(
            django_forms.ModelForm,
            'clean',
            return_value=data
        ) as clean:
            result = forms.ImageAdminForm.clean(self.form)
            clean.assert_called()
            self.assertEqual(result, data)
        self.assertEqual(
            self.form.fields['object_id'].widget.model_class,
            TestModel
        )
