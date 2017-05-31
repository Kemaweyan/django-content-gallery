import json

from django.test import mock, TestCase
from django.contrib.contenttypes.models import ContentType
from django.forms import Select
from django.db.models import BLANK_CHOICE_DASH
from django.contrib.admin.widgets import AdminFileWidget

from .. import widgets
from .. import utils
from .. import settings

from .models import *

class TestContentTypeSelect(TestCase):

    def test_filter_choices(self):
        ctype = ContentType.objects.get_for_model(TestModel)
        test_choice = (str(ctype.pk), ctype.name)
        ctype = ContentType.objects.get_for_model(AnotherTestModel)
        another_choice = (str(ctype.pk), ctype.name)
        ctype = ContentType.objects.get_for_model(WrongTestModel)
        wrong_choice = (str(ctype.pk), ctype.name)
        widget = mock.MagicMock()
        widget.choices = [
            ("", "----"),
            test_choice,
            another_choice,
            wrong_choice
        ]
        widgets.ContentTypeSelect._filter_choices(widget)
        self.assertIn(("", "----"), widget.choices)
        self.assertIn(test_choice, widget.choices)
        self.assertNotIn(another_choice, widget.choices)
        self.assertNotIn(wrong_choice, widget.choices)

    @mock.patch('django.utils.safestring.mark_safe')
    def test_render_with_mark_safe(self, mark_safe):
        widget = mock.MagicMock(spec=widgets.ContentTypeSelect)
        widget.js = " %s"
        with mock.patch.object(
            utils,
            'get_choices_url_pattern',
            return_value='foo'
        ) as get_url_pattern, mock.patch.object(
            Select,
            'render',
            return_value='bar'
        ) as render:
            widgets.ContentTypeSelect.render(widget, 'name', 'value')
            get_url_pattern.assert_called()
            render.assert_called_with('name', 'value', None)
        mark_safe.assert_called_with('bar foo')

    @mock.patch('django.utils.safestring.mark_safe', lambda x: x)
    def test_render_without_mark_safe(self):
        widget = mock.MagicMock(spec=widgets.ContentTypeSelect)
        widget.js = " %s"
        with mock.patch.object(
            utils,
            'get_choices_url_pattern',
            return_value='foo'
        ) as get_url_pattern, mock.patch.object(
            Select,
            'render',
            return_value='bar'
        ) as render:
            result = widgets.ContentTypeSelect.render(widget, 'name', 'value')
            get_url_pattern.assert_called()
            render.assert_called_with('name', 'value', None)
        self.assertEqual(result, 'bar foo')


class TestObjectIdSelect(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.object1 = TestModel.objects.create(name="Test object 1")
        cls.object2 = TestModel.objects.create(name="Test object 2")

    @classmethod
    def tearDownClass(cls):
        cls.object1.delete()
        cls.object2.delete()

    def test_create_choices_objects_exist(self):
        widget = mock.MagicMock()
        widget.model_class = TestModel
        widgets.ObjectIdSelect._create_choices(widget)
        self.assertEqual(len(widget.choices), 3)
        self.assertIn(BLANK_CHOICE_DASH[0], widget.choices)
        self.assertIn((str(self.object1.pk), self.object1), widget.choices)
        self.assertIn((str(self.object2.pk), self.object2), widget.choices)

    def test_create_choices_objects_do_not_exist(self):
        widget = mock.MagicMock()
        widget.model_class = AnotherTestModel
        widgets.ObjectIdSelect._create_choices(widget)
        self.assertEqual(len(widget.choices), 1)
        self.assertIn(BLANK_CHOICE_DASH[0], widget.choices)

    def test_render(self):
        widget = mock.MagicMock(spec=widgets.ObjectIdSelect)
        with mock.patch.object(
            Select,
            'render',
            return_value='foo'
        ) as render:
            result = widgets.ObjectIdSelect.render(widget, 'name', 'value')
            render.assert_called_with('name', 'value', None)
        self.assertEqual(result, 'foo')
        widget._create_choices.assert_called()


class TestImageWidget(TestCase):

    def test_render_without_image(self):
        widget = mock.MagicMock(spec=widgets.ImageWidget)
        widget.template_with_initial = "bar"
        with mock.patch.object(
            AdminFileWidget,
            'render',
            return_value='foo'
        ) as render:
            result = widgets.ImageWidget.render(widget, 'name', None)
            render.assert_called_with('name', None, None)
        self.assertEqual(result, 'foo')
        self.assertEqual(widget.template_with_initial, 'bar')

    @mock.patch('django.utils.html.escape', return_value='escaped data')
    def test_render_with_image(self, escape):
        widget = mock.MagicMock(spec=widgets.ImageWidget)
        widget.template = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}"
        with mock.patch.object(
            utils,
            'create_image_data',
            return_value='data'
        ) as create_data, mock.patch.object(
            utils,
            'create_static_url',
            return_value='url'
        ) as create_url, mock.patch.object(
            AdminFileWidget,
            'render',
            return_value='foo'
        ) as render:
            result = widgets.ImageWidget.render(widget, 'name', 'image')
            render.assert_called_with('name', 'image', None)
            create_url.assert_called_with("content_gallery/img/zoom.png")
            create_data.assert_called_with('image')
        escape.assert_called_with(json.dumps('data'))
        self.assertEqual(result, 'foo')
        self.assertEqual(
            widget.template_with_initial,
            "\n".join([
                str(settings.GALLERY_PREVIEW_WIDTH + 14),
                str(settings.GALLERY_PREVIEW_HEIGHT + 14),
                str(settings.GALLERY_PREVIEW_WIDTH),
                str(settings.GALLERY_PREVIEW_HEIGHT),
                str(settings.GALLERY_PREVIEW_HEIGHT),
                "escaped data",
                "url",
                str(settings.GALLERY_PREVIEW_WIDTH - 55)
            ])
        )


class TestImageInlineWidget(TestCase):

    def test_render_without_image(self):
        widget = mock.MagicMock(spec=widgets.ImageInlineWidget)
        result = widgets.ImageInlineWidget.render(widget, 'name', None)
        self.assertEqual(result, "")

    @mock.patch('django.template.loader.render_to_string', return_value="foo")
    def test_render_with_image(self, render_to_string):
        widget = mock.MagicMock(spec=widgets.ImageInlineWidget)
        widget.template_name = "bar"
        image = mock.MagicMock()
        image.small_preview_url = 'url'
        with mock.patch.object(
            utils,
            'create_image_data',
            return_value='data'
        ) as create_data:
            result = widgets.ImageInlineWidget.render(widget, 'name', image)
            create_data.assert_called_with(image)
        self.assertEqual(result, "foo")
        render_to_string.assert_called_with(
            'bar',
            {
                'preview_src': 'url',
                'image_data': json.dumps('data')
            }
        )
