#!/usr/bin/env python3

import os
from setuptools import setup, find_packages
import content_gallery

FILE_TYPES = [
    ".js",
    ".css",
    ".png",
    ".gif",
    ".html"
]

def has_required_files(files):
    for f in files:
        name, ext = os.path.splitext(f)
        if ext in FILE_TYPES:
            return True
    return False

def find_data_dirs(path):
    dirs = []
    for name, dlist, files in os.walk(path):
        if has_required_files(files):
            relpath = os.path.relpath(name, 'content_gallery')
            dirs.append(os.path.join(relpath, '*'))
    return dirs


setup(
    name = "django-content-gallery",
    version = content_gallery.__version__,
    fullname = "Django Content Gallery",
    description = " The Django application allows to attach a collection of images to objects of any model of any app",
    author = "Taras Gaidukov",
    author_email = "kemaweyan@gmail.com",
    keywords = "django image gallery photo",
    long_description = open('README.rst').read(),
    url = "https://github.com/Kemaweyan/django-content-gallery",
    license = "BSD-3-Clause",
    package_data = {"content_gallery": find_data_dirs('content_gallery')},
    packages=find_packages(exclude=["content_gallery.tests", "content_gallery_testapp", "content_gallery_testapp.*"]),
    test_suite='runtests.runtests',
    install_requires=[
        'Django==1.10.5',
        'python-magic==0.4.13',
        'Pillow==4.0.0',
        'awesome-slugify==1.6.5',
        'django-admin-jqueryui112',
    ]
)
