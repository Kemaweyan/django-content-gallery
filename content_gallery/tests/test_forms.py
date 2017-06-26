import os

from django.test import mock, TestCase
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms as django_forms
from django.conf import settings as django_settings

from .. import forms
from .. import models

from .models import TestModel
from .utils import get_image_in_memory_data, create_image_file

class TestImageAdminForm(TestCase):
    """
    Tests the Image edit form.
    """

    # a path to a temporary image file
    image_path = os.path.join(django_settings.MEDIA_ROOT, 'foo.jpg')

    @classmethod
    def setUpClass(cls):
        """
        Creates the image file to test form validation
        """
        create_image_file(cls.image_path)
        # save the content type of the TestModel
        cls.ctype = ContentType.objects.get_for_model(TestModel)

    @classmethod
    def tearDownClass(cls):
        """
        Deletes the image file
        """
        os.remove(cls.image_path)

    def setUp(self):
        """
        Creates a mock object used instead of real form and
        a mock for the 'object_id' field
        """
        # create a form mock object
        self.form = mock.MagicMock(spec=forms.ImageAdminForm)
        # 'fields' is a dict
        self.form.fields = {}
        # create a field mock object
        field = mock.MagicMock()
        # initially the 'model_class' attribute is None
        field.widget.model_class = None
        # set the field mock to the form mock
        self.form.fields['object_id'] = field

    def test_valid_form(self):
        """
        Checks whether the form validates correct data
        """
        # open the image file
        with open(self.image_path, 'rb') as upload_file:
            # dict with valid values
            post_dict = {
                'position': 0,
                'content_type': self.ctype.pk,
                'object_id': 1
            }
            # dict with valid uploaded file
            file_dict = {
                # create an uploaded file object
                # using opened image file
                'image': SimpleUploadedFile(
                    upload_file.name,
                    upload_file.read()
                )
            }
            # create a form with both dicts
            form = forms.ImageAdminForm(post_dict, file_dict)
            # check whether the form is valid
            self.assertTrue(form.is_valid())

    def test_invalid_form_without_image(self):
        """
        Checks whether the form without uploaded image is invalid
        """
        # dict with valid values
        post_dict = {
            'position': 0,
            'content_type': self.ctype.pk,
            'object_id': 1
        }
        # create a form without uploaded file
        form = forms.ImageAdminForm(post_dict)
        # check whether the form is not valid
        self.assertFalse(form.is_valid())

    def test_invalid_form_without_content_type(self):
        """
        Checks whether the form without specified content type is invalid
        """
        # open the image file
        with open(self.image_path, 'rb') as upload_file:
            # dict without content_type
            post_dict = {
                'position': 0,
                'object_id': 1
            }
            # dict with valid uploaded file
            file_dict = {
                'image': SimpleUploadedFile(
                    upload_file.name,
                    upload_file.read()
                )
            }
            # create a form with both dicts
            form = forms.ImageAdminForm(post_dict, file_dict)
            # check whether the form is not valid
            self.assertFalse(form.is_valid())

    def test_invalid_form_without_object_id(self):
        """
        Checks whether the form without specified object id is invalid
        """
        # open the image file
        with open(self.image_path, 'rb') as upload_file:
            # dict without object_id
            post_dict = {
                'position': 0,
                'content_type': self.ctype.pk
            }
            # dict with valid uploaded file
            file_dict = {
                'image': SimpleUploadedFile(
                    upload_file.name,
                    upload_file.read()
                )
            }
            # create a form with both dicts
            form = forms.ImageAdminForm(post_dict, file_dict)
            # check whether the form is not valid
            self.assertFalse(form.is_valid())

    def test_valid_form_without_position(self):
        """
        Checks whether the form without specified position
        is valid since the 'posion' field is optional
        """
        # open the image file
        with open(self.image_path, 'rb') as upload_file:
            # dict without position
            post_dict = {
                'content_type': self.ctype.pk,
                'object_id': 1
            }
            # dict with valid uploaded file
            file_dict = {
                'image': SimpleUploadedFile(
                    upload_file.name,
                    upload_file.read()
                )
            }
            # create a form with both dicts
            form = forms.ImageAdminForm(post_dict, file_dict)
            # check whether the form is valid
            self.assertTrue(form.is_valid())

    def test_create_empty_form(self):
        """
        Checks whether the 'model_class' attribute of the 'object_id'
        widget is None and the 'content_type' and 'object_id' widgets
        are not hidden in empty normal form
        """
        # create an empty form
        form = forms.ImageAdminForm()
        # check whether the 'model_class' is None
        self.assertIsNone(form.fields['object_id'].widget.model_class)
        # check whether widgets are not hidden
        self.assertNotIsInstance(
            form.fields['content_type'].widget,
            django_forms.HiddenInput
        )
        self.assertNotIsInstance(
            form.fields['object_id'].widget,
            django_forms.HiddenInput
        )

    def test_create_empty_form_popup(self):
        """
        Checks whether the 'content_type' and 'object_id' widgets
        are hidden in empty popup form (opened from another admin)
        """
        # create an empty form with '_popup' initial
        form = forms.ImageAdminForm(initial={'_popup': True})
        # check whether widgets are hidden
        self.assertIsInstance(
            form.fields['content_type'].widget,
            django_forms.HiddenInput
        )
        self.assertIsInstance(
            form.fields['object_id'].widget,
            django_forms.HiddenInput
        )

    def test_create_form_with_instance(self):
        """
        Checks whether the constructor sets the correct value to
        'model_class' attribute of the 'object_id' widget if the form
        is created with the instance of Image
        """
        # create a content object of TestModel
        obj = TestModel.objects.create(name='Test object')
        # ctreate an image related to the object
        image = models.Image.objects.create(
            image=get_image_in_memory_data(),
            position=0,
            content_type=ContentType.objects.get_for_model(TestModel),
            object_id=obj.id
        )
        # create a form with the image instance
        form = forms.ImageAdminForm(instance=image)
        # check whether the 'model_class' contains the TestModel
        self.assertEqual(
            form.fields['object_id'].widget.model_class,
            TestModel
        )
        # delete temporary objects
        image.delete()
        obj.delete()

    def test_clean_unbounded(self):
        """
        Checks whether parent's 'clean' method has been called
        and the 'model_class' of the 'object_id' widget is still
        None in unbounded form
        """
        # set the form unbound
        self.form.is_bound = False
        # patch the 'clean' method of the parent class
        with mock.patch(
            'django.forms.ModelForm.clean',
            return_value='foo'
        ) as clean:
            # call the method with the mock object
            result = forms.ImageAdminForm.clean(self.form)
            # check whether the parent method has been called
            clean.assert_called_with()
            # check whether the method returns
            # the result of the parent method
            self.assertEqual(result, 'foo')
        # check whether the 'model_class' is still None
        self.assertIsNone(self.form.fields['object_id'].widget.model_class)

    def test_clean_bounded_without_content_type(self):
        """
        Checks whether parent's 'clean' method has been called
        and the 'model_class' of the 'object_id' widget is still
        None in bounded form if the content type is not set
        """
        # set the form bound
        self.form.is_bound = True
        # patch the 'clean' method of the parent class
        with mock.patch(
            'django.forms.ModelForm.clean',
            return_value={}
        ) as clean:
            # call the method with the mock object
            result = forms.ImageAdminForm.clean(self.form)
            # check whether the parent method has been called
            clean.assert_called_with()
            # check whether the method returns
            # the result of the parent method
            self.assertEqual(result, {})
        # check whether the 'model_class' is still None
        self.assertIsNone(self.form.fields['object_id'].widget.model_class)

    def test_clean_bounded_with_content_type(self):
        """
        Checks whether parent's 'clean' method has been called
        and the 'model_class' of the 'object_id' widget has been
        set correctly in bounded form if the content type is set
        """
        # set the form bound
        self.form.is_bound = True
        # specify the cleaned data returned by parent method
        data = {'content_type': self.ctype}
        # patch the 'clean' method of the parent class
        with mock.patch(
            'django.forms.ModelForm.clean',
            return_value=data
        ) as clean:
            # call the method with the mock object
            result = forms.ImageAdminForm.clean(self.form)
            # check whether the parent method has been called
            clean.assert_called_with()
            # check whether the method returns
            # the result of the parent method
            self.assertEqual(result, data)
        # check whether the 'model_class' contains the content type model
        self.assertEqual(
            self.form.fields['object_id'].widget.model_class,
            TestModel
        )
