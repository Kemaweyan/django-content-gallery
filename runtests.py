#!/usr/bin/env python3

import os
import sys

# create a path to the content_gallery_testapp
base_dir = os.path.dirname(os.path.abspath(__file__)) 
path = os.path.join(base_dir, 'content_gallery_testapp')
# insert the path right after current directory
sys.path.insert(1, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'content_gallery_testapp.settings_test'

import django
from django.test.utils import get_runner
from django.conf import settings


def runtests():
    django.setup()
    TestRunner = get_runner(settings)
    runner = TestRunner(verbosity=1, interactive=True)
    failures = runner.run_tests(['content_gallery'])
    sys.exit(failures)

if __name__ == '__main__':
    runtests()
