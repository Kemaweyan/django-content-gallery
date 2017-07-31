django-content-gallery
======================

.. image:: https://travis-ci.org/Kemaweyan/django-content-gallery.svg?branch=master
    :target: https://travis-ci.org/Kemaweyan/django-content-gallery
.. image:: https://coveralls.io/repos/github/Kemaweyan/django-content-gallery/badge.svg?branch=master
    :target: https://coveralls.io/github/Kemaweyan/django-content-gallery?branch=master

**django-content-gallery** is a Django application that allows to attach a collection
of images to objects of any models in you Django projects. It also allows you easily
add and remove images, re-attach images to another object (i.e. move an image to another
collection) and change an order of images in the collection as well.

The **django-content-gallery** creates 5 images with different sizes for each uploaded image:

* a large image viewed in the gallery for users with high-resulution displays
* a small image viewed in the gallery for users with low-resulution displays
* a large preview image used in a preview
* a small preview image used in a small preview
* a thumbnail viewed in the list of available images


Requirements
============

* **Python** 3.4+
* **Django** 1.10+
* **Pillow** 3.0.0+
* **python-magic** 0.4.2+
* **awesome-slugify** 1.6+
* **django-admin-jqueryui112** 1.12.1+

.. NOTE::
	Windows users should also copy ``magic1.dll``, ``regex2.dll`` and ``zlib1.dll`` onto
	the PATH. These libraries are required by the **python-magic** package and could be
	downloaded on the `File for Windows <http://gnuwin32.sourceforge.net/packages/file.htm>`_
	official page.


Installation
============

To install the **django-content-gallery** type following command:

.. code-block::

    $ pip install django-content-gallery

Then in ``settings.py``:

* Add the ``content_gallery`` to INSTALLED_APPS in the settings of your project
  and the ``admin_jqueryui`` to enable sorting images in the admin panel.

* Add the ``django.template.context_processors.media`` context processor to the
  the ``context_processor`` list under the ``OPTIONS`` dict in ``TEMPLATES``

* Add the path to  ``MEDIA_ROOT`` and ``MEDIA_URL``

.. code-block::

    INSTALLED_APPS = [
        ...
        'content_gallery',
        'admin_jqueryui',
    ]

    TEMPLATES = [
        {
            ...
            'OPTIONS': {
                'context_processors': [
                    ...
                    'django.template.context_processors.media',
                     ],
            },
        },
    ]

    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'


Add the ``content_gallery.urls`` to the urls.py of your project (you could use any
URL pattern, not only ``^content_gallery\``), and add the handling of
``MEDIA_ROOT`` when working locally/in debug mode:


.. code-block::

    urlpatterns = [
        ...
        url(r'^content_gallery/', include('content_gallery.urls')),
    ]

    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

Create tables in the database using the ``migrate`` command:

.. code-block::

    $ python manage.py migrate content_gallery

Now the **django-content-gallery** is ready for use!


Configuration
=============

To change settings of the **django-content-gallery** set the ``CONTENT_GALLERY`` dict
in your ``settings.py`` module. The dict could contain following items:

* **image_width** - the target width of the large image
* **image_height** - the target height of the large image

* **small_image_width** - the target width of the small image
* **small_image_height** - the target height of the small image

* **thumbnail_width** - the target width of the thumbnail
* **thumbnail_height** - the target height of the thumbnail

* **preview_width** - the target width of the large preview
* **preview_height** - the target height of the large preview

* **small_preview_width** - the target width of the small preview
* **small_preview_height** - the target height of the small preview

* **path** - the subdirectory in the ``MEDIA_ROOT`` where image files would be stored

Default values of these settings are

* **image_width** = 752
* **image_height** = 608
* **small_image_width** = 564
* **small_image_height** = 456
* **thumbnail_width** = 94
* **thumbnail_height** = 76
* **preview_width** = 376
* **preview_height** = 304
* **small_preview_width** = 141
* **small_preview_height** =114
* **path** = 'content_gallery'

You could change some of these settings and keep the rest undefined in you ``settings.py``,
in this case the default values would be used instead:

.. code-block::

	CONTENT_GALLERY = {
		"image_width": 1024,
		"image_height": 768,
	}

This code changes size of the large image only, the rest of settings values would be default.

Usage
=====

To make your models able to attach a gallery, use the ``ContentGalleryMixin`` in
models you want to use the content-gallery with:

.. code-block::

    from django.db import models
    from content_gallery.models import ContentGalleryMixin

    class YourModel(ContentGalleryMixin, models.Model):
        ...

Also to be able to edit attached image collection on the admin page of your model,
you need to add the ``ImageAdminInline`` to inlines of your model admin. Add following
code to your admin.py

.. code-block::

    from django.contrib import admin
    from content_gallery.admin import ImageAdminInline
    from . import models

    class YourModelAdmin(admin.ModelAdmin):
        inlines = [
            ImageAdminInline,
        ]

    admin.site.register(models.YourModel, YourModelAdmin)

Now the **django-content-gallery** is available for your models. Then you need to add the
content-gallery to your pages.

First of all add the ``content_gallery/_image_view.html`` template to your templates where you
want the content-gallery to be available:

.. code-block::

    {% include "content_gallery/_image_view.html" %}

The **django-content-gallery** uses jQuery within its scripts, so make sure that jQuery is
available on your pages where the content-gallery is used.

To add the gallery related to your objects onto your pages the **django-content-gallery** provides
two template tags. Those template tags are located in the ``content_gallery`` template tag set, so
before use them you should load this set:

.. code-block::

	{% load content_gallery %}

The first template tag named ``gallery_preview`` adds the large preview. It uses one argument which
is your object. This tag is meant to be used generally in templates of detail views:

.. code-block::

	{% gallery_preview your_object %}

This code adds the preview widget that shows a preview of the first image related to the object.

The ``gallery_small_preview`` tag adds a small preview onto the page, it uses such object as an
argument as well, and is meant to be used generally in templates of list views:

.. code-block::

	{% gallery_small_preview your_object %}

This code adds the small preview widget that shows a small preview of the first image related
to the object.

Also the **django-content-gallery** provides a simple template tag named ``gallery_image_data``
that also gets an object as an argument and returns a dict object that contains an object of
the first image and JSON data for constructing a link to the object. You could use this template
tag to construct you own custom widgets.

For simply accessing all images data associated with an object from within a
template, you can generate a queryset like this:

.. code-block::

  {% for image in myobject.content_gallery.all %}
    <img src="{{ image.thumbnail_url }}">
  {% endfor %}

For more details, see the **content_gallery_testapp** which is an example of
the **django-content-gallery** usage.
