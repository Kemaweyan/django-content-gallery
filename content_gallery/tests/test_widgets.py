import json

from django.test import mock, TestCase
from django.contrib.contenttypes.models import ContentType
from django.forms import Select
from django.db.models import BLANK_CHOICE_DASH
from django.contrib.admin.widgets import AdminFileWidget
from django.core.files.uploadedfile import InMemoryUploadedFile

from .. import widgets
from .. import utils
from .. import fields

from .models import *
from .base_test_cases import *
from .utils import patch_settings

class TestContentTypeSelect(TestCase):
    """
    Tests for the widget for selecting models in the Image admin
    """

    def test_filter_choices(self):
        """
        Checks whether the _filter_choices method removes from
        the choices list all models unless it has the gallery_visible
        attribute with True value. Also an empty choice should remain
        """
        # create a choice of TestModel (gallery_visible=True)
        ctype = ContentType.objects.get_for_model(TestModel)
        test_choice = (str(ctype.pk), ctype.name)
        # create a choice of AnotherTestModel (gallery_visible=False)
        ctype = ContentType.objects.get_for_model(AnotherTestModel)
        another_choice = (str(ctype.pk), ctype.name)
        # create a choice of WrongTestModel (has not gallery_visible)
        ctype = ContentType.objects.get_for_model(WrongTestModel)
        wrong_choice = (str(ctype.pk), ctype.name)
        # create a mock widget object
        widget = mock.MagicMock(spec=widgets.ContentTypeSelect)
        # set initial choices
        widget.choices = [
            ("", "----"),
            test_choice,
            another_choice,
            wrong_choice
        ]
        # call the _filter_choices method
        widgets.ContentTypeSelect._filter_choices(widget)
        # check whether an empty choice is in the list
        self.assertIn(("", "----"), widget.choices)
        # check whether the TestModel choice is in the list
        self.assertIn(test_choice, widget.choices)
        # check whether the AnotherTestModel choice is not in the list
        self.assertNotIn(another_choice, widget.choices)
        # check whether the WrongTestModel choice is not in the list
        self.assertNotIn(wrong_choice, widget.choices)

    @mock.patch('django.utils.safestring.mark_safe', return_value='baz')
    def test_render_with_mark_safe(self, mark_safe):
        """
        Checks whether the widget is rendered properly
        """
        # create a mock widget object
        widget = mock.MagicMock(spec=widgets.ContentTypeSelect)
        # set the js template
        # it should contain %s for URL pattern subtitution
        widget.js = " %s"
        # patch the get_choices_url_pattern helper function
        # so that it returns known value
        with mock.patch.object(
            utils,
            'get_choices_url_pattern',
            return_value='foo'
        ) as get_url_pattern, mock.patch.object(
            Select,  # patch parent's method
            'render',
            return_value='bar'
        ) as render:
            # call the render method
            result = widgets.ContentTypeSelect.render(widget, 'name', 'value')
            # check whether the helper function has been called
            get_url_pattern.assert_called_with()
            # check whether the parent's method has been called
            # with the same arguments
            render.assert_called_with('name', 'value', None)
        # check whether the mark_safe function has been called with rendered
        # template containing a result of the parent's method + the js
        # pattern where %s is replaced with the URL pattern
        # i.e. 'bar' + ' %s' % 'foo'
        mark_safe.assert_called_with('bar foo')
        # check whether the render method returns a result of the mark_safe
        self.assertEqual(result, "baz")


class TestObjectIdSelect(TestCase):
    """
    Tests for the widget for selecting the object of the model
    """

    @classmethod
    def setUpClass(cls):
        """
        Creates two objects of the TestModel in the database
        """
        cls.widget = mock.MagicMock(spec=widgets.ObjectIdSelect)
        cls.object1 = TestModel.objects.create(name="Test object 1")
        cls.object2 = TestModel.objects.create(name="Test object 2")

    @classmethod
    def tearDownClass(cls):
        """
        Deletes all created objects
        """
        cls.object1.delete()
        cls.object2.delete()

    def setUp(self):
        """
        Creates a mock widget object
        """
        self.widget = mock.MagicMock(spec=widgets.ObjectIdSelect)

    def test_create_choices_objects_exist(self):
        """
        Checks whether the _create_choices method creates choices for
        all objects of the selected model if objects exist. Also the list
        should include an empty choice.
        """
        # set selected model class with existing objects
        self.widget.model_class = TestModel
        # call the _create_choices method
        widgets.ObjectIdSelect._create_choices(self.widget)
        # check whether the list contains an empty choice
        self.assertIn(BLANK_CHOICE_DASH[0], self.widget.choices)
        # create choices
        choice1 = (str(self.object1.pk), self.object1)
        choice2 = (str(self.object2.pk), self.object2)
        # check whether the list contains both TestModel objects
        self.assertIn(choice1, self.widget.choices)
        self.assertIn(choice2, self.widget.choices)
        # check whether there are 3 choices so the list contains nothing
        # but two objects of the TestModel and an empty choice
        self.assertEqual(len(self.widget.choices), 3)

    def test_create_choices_objects_do_not_exist(self):
        """
        Checks whether the _create_choices method creates an empty choice
        only if there is no objects of the selected model
        """
        # set selected model class without existing objects
        self.widget.model_class = AnotherTestModel
        # call the _create_choices method
        widgets.ObjectIdSelect._create_choices(self.widget)
        # check whether the list contains only one choice
        self.assertEqual(len(self.widget.choices), 1)
        # check whether an empty choice presents in the list
        self.assertIn(BLANK_CHOICE_DASH[0], self.widget.choices)

    def test_render(self):
        """
        Checks whether the render method calls the _create_choices method
        and returns a result of parent's render method. The _create_choices
        should be called before the parent's render.
        """
        # create a mock for logging calls to determine call order
        call_logger = mock.Mock()
        # attach the _create_choices mock to the logger
        call_logger.attach_mock(self.widget._create_choices, 'create_choices')
        # patch the parent's render method
        with mock.patch.object(
            Select,
            'render',
            return_value='foo'
        ) as render:
            # attach the parent's render mock to the logger
            call_logger.attach_mock(render, 'parent_render')
            # call the render method
            result = widgets.ObjectIdSelect.render(self.widget, 'name', 'value')
        # check whether the method returns the result of the parent's render
        self.assertEqual(result, 'foo')
        # create an expected calls list where the create_choices is called
        # before the parent's render
        expected_calls = [
            mock.call.create_choices(),
            # the parent's render should be called with the same arguments
            mock.call.parent_render('name', 'value', None)
        ]
        # check whether functions has been called in the proper order
        self.assertListEqual(call_logger.mock_calls, expected_calls)


class TestImageWidget(TestCase):
    """
    Tests for the widget displaying a preview of image in the Image admin
    """

    def setUp(self):
        """
        Creates a mock widget object
        """
        self.widget = mock.MagicMock(spec=widgets.ImageWidget)

    def test_render_without_image(self):
        """
        Checks whether the template_with_initial is not affected by
        the render method if it has been called without an image
        """
        # set initial template_with_initial value
        self.widget.template_with_initial = "bar"
        # patch parent's render method
        with mock.patch.object(
            AdminFileWidget,
            'render',
            return_value='foo'
        ) as render:
            # call the method with None image argument
            result = widgets.ImageWidget.render(self.widget, 'name', None)
            # check whether the parent's method has been called
            # with the same arguments
            render.assert_called_with('name', None, None)
        # check whether the method returns the result of the parent's method
        self.assertEqual(result, 'foo')
        # check whether the template_with_initial has not been changed
        self.assertEqual(self.widget.template_with_initial, 'bar')

    @mock.patch('django.utils.html.escape', return_value='escaped data')
    def test_render_with_image(self, escape):
        """
        Checks whether the template_with_initial is filled properly
        if the render method has been called with saved image
        """
        # set initial template_with_initial value
        self.widget.template = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}"
        # create a mock image field file object
        image = mock.MagicMock(spec=fields.GalleryImageFieldFile)
        # set known settings and patch helper functions
        with patch_settings(
            {
                'preview_width': 400,
                'preview_height': 300,
            }
        ), mock.patch.object(
            utils,
            'create_image_data',
            return_value='data'
        ) as create_data, mock.patch.object(
            utils,
            'create_static_url',
            return_value='url'
        ) as create_url, mock.patch.object(
            AdminFileWidget,  # patch the parent's render method
            'render',
            return_value='foo'
        ) as render:
            # call the method with an image field file mock
            result = widgets.ImageWidget.render(self.widget, 'name', image)
            # check whether the parent's method has been called
            # with the same arguments
            render.assert_called_with('name', image, None)
            # check whether tha create_static_url helper function has been
            # called with the path to zoom image
            create_url.assert_called_with("content_gallery/img/zoom.png")
            # check whether the create_image_data helper function has been
            # called with the image filed file mock
            create_data.assert_called_with(image)
        # check whether the escape has been called with the returned by
        # create_image_data value in JSON format
        escape.assert_called_with(json.dumps('data'))
        # check whether the method returns the result of the parent's method
        self.assertEqual(result, 'foo')
        # check whether the template has been filled properly
        self.assertEqual(
            self.widget.template_with_initial,
            "\n".join([
                # the size of the container
                str(400 + 14),
                str(300 + 14),
                # the size of the image
                str(400),
                str(300),
                # the line-height
                str(300),
                # the result of the escape function
                "escaped data",
                # the result of create_static_url function
                "url",
                # the left offset of the zoom image
                str(400 - 55)
            ])
        )

    def test_render_with_uploaded_image(self):
        """
        Checks whether the template_with_initial is not affected by
        the render method if it has been called with just uploaded image
        """
        # set initial template_with_initial value
        self.widget.template_with_initial = "bar"
        # create a mock object of just uploaded image
        image = mock.MagicMock(spec=InMemoryUploadedFile)
        # patch the parent's render method
        with mock.patch.object(
            AdminFileWidget,
            'render',
            return_value='foo'
        ) as render:
            # call the method with just uploaded image mock
            result = widgets.ImageWidget.render(self.widget, 'name', image)
            # check whether the parent's method has been called
            # with the same arguments
            render.assert_called_with('name', image, None)
        # check whether the method returns the result of the parent's method
        self.assertEqual(result, 'foo')
        # check whether the template_with_initial has not been changed
        self.assertEqual(self.widget.template_with_initial, 'bar')


class TestImageInlineWidget(TestCase):
    """
    Tests for the widget displaying a small preview of image in inline admins
    """

    def setUp(self):
        """
        Creates a mock widget object
        """
        self.widget = mock.MagicMock(spec=widgets.ImageInlineWidget)

    def test_render_without_image(self):
        """
        Checks whether the render method returns an empty string if
        it has been called None image argument
        """
        # call the method with None image argument
        result = widgets.ImageInlineWidget.render(self.widget, 'name', None)
        # check whether the result is an empty string
        self.assertEqual(result, "")

    @mock.patch('django.template.loader.render_to_string', return_value="foo")
    def test_render_with_image(self, render_to_string):
        """
        Checks whether the render method returns a result of
        the render_to_string function if the method has been
        called with an image
        """
        # set a template name
        self.widget.template_name = "bar"
        # create an image mock
        image = mock.MagicMock()
        # set an URL of the small preview
        image.small_preview_url = 'url'
        # patch the create_image_url so that it returns known result
        with mock.patch.object(
            utils,
            'create_image_data',
            return_value='data'
        ) as create_data:
            # call the method with the image mock
            result = widgets.ImageInlineWidget.render(
                self.widget,
                'name',
                image
            )
            # check whether the create_image_data helper function has been
            # called with the image
            create_data.assert_called_with(image)
        # check whether the method returns the result of
        # the render_to_string function
        self.assertEqual(result, "foo")
        # check whether the render_to_string function has been called
        # with proper arguments
        render_to_string.assert_called_with(
            'bar',  # the template name
            {
                'preview_src': 'url',  # the URL of small preview
                # the result of the create_image_data function
                # in JSON format
                'image_data': json.dumps('data')
            }
        )
