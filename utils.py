import re

from django.core import urlresolvers as ur

def get_choices_url_pattern():
    choices_url = ur.reverse('gallery:choices', args=(0,))
    return re.sub(r'\d+$', '', choices_url)
