django-content-gallery
======================

**django-content-gallery** is a Django application that allows to attach a collection
of images to objects of any models in you Django projects. It also allows you easily
add and remove images, re-attach images to another object (i.e. move an image to another
collection) and change an order of images in the collection as well.


Installation
============

To install the django-content-gallery type following command:

.. code-block::

    $ pip install django-content-gallery

Then add the ``content_gallery`` to INSTALLED_APPS in the settings of your project:

.. code-block::

    INSTALLED_APPS = [
        ...
        'content_gallery',
    ]

Add the ``content_gallery.urls`` to the urls.py of your project (you could use any
URL pattern, not only ``^content_gallery\``):

.. code-block::

    urlpatterns = [
        ...
        url(r'^content_gallery/', include('content_gallery.urls')),
    ]

Create tables in the database using the ``migrate`` command:

.. code-block::

    $ python manage.py migrate content_gallery

Now to make your models able to attach a gallery, use the ``ContentGalleryMixin`` in
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

Now the **django-content-gallery** is available for your models. For more details, see the
**content_gallery_testapp** which is an example of the **django-content-gallery** usage.


