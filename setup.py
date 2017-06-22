#!/usr/bin/env python3

import os
from setuptools import setup, find_packages
import content_gallery

data_files = [
    "static/content_gallery/img/*",
    "static/content_gallery/css/*",
    "static/content_gallery/js/*",
    "static/content_gallery/admin/img/*",
    "static/content_gallery/admin/css/*",
    "static/content_gallery/admin/js/*",
    "templates/content_gallery/*",
    "templates/content_gallery/templatetags/*",
    "templates/content_gallery/admin/*",
    "templates/content_gallery/admin/edit_inline/*",
]

setup(
    name = "django-content-gallery",
    version = content_gallery.__version__,
    fullname = "Django Content Gallery",
    description = " The Django application allows to attach a collection of images to objects of any model of any app",
    author = "Taras Gaidukov",
    author_email = "kemaweyan@gmail.com",
    keywords = "django image gallery photo",
    # long_description = open('README').read(),
    url = "https://github.com/Kemaweyan/django-content-gallery",
    license = "BSD-3-Clause",
    package_data = {"content_gallery": data_files},
    packages=find_packages(exclude=["content_gallery.tests", "content_gallery_testapp", "content_gallery_testapp.*"]),
    test_suite='runtests.runtests'
)
