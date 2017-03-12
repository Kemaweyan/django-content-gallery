import re
import os

from django.core import urlresolvers as ur

def get_choices_url_pattern():
    choices_url = ur.reverse('gallery:choices', args=(0,))
    return re.sub(r'\d+$', '', choices_url)

def create_thumbnail_path(path):
    name, ext = os.path.splitext(path)
    return "{}_thumbnail.{}".format(name, ext)
