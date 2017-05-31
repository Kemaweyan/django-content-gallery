from django.test import mock, TestCase
from django.contrib.contenttypes.models import ContentType
from django.forms import Select
from django.db.models import BLANK_CHOICE_DASH

from .. import widgets
from .. import utils

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
