from django.test import TestCase, mock

from .. import utils

class TestGetChoicesUrlPattern(TestCase):

    @mock.patch('django.core.urlresolvers.reverse',
                return_value='/gallery/ajax/choices/0')
    def test_removing_pk(self, reverse_mock):
        url = utils.get_choices_url_pattern()
        self.assertEqual(url, '/gallery/ajax/choices/')
        reverse_mock.assert_called_once_with('gallery:choices', args=(0,))
