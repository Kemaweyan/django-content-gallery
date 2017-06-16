from django.conf.urls import url

from . import views

app_name = 'content_gallery'

urlpatterns = [
    # a URL for getting a list of objets of the model
    url(
        r'^ajax/choices/(?P<pk>\d+)/$',
        views.choices,
        name='choices'
    ),
    # a URL for getting data of all images related to the object
    url(
        r'^ajax/gallery_data/(?P<app_label>\w+)/'
        '(?P<content_type>\w+)/(?P<object_id>\d+)/$',
        views.gallery_data,
        name='gallery_data'
    ),
]
