from django.conf.urls import url

from . import views

app_name = 'gallery'

urlpatterns = [
    url(
        r'^ajax/choices/(?P<pk>\d+)$',
        views.choices,
        name='choices'
    ),
    url(
        r'^ajax/gallery_data/(?P<app_label>\w+)/'
        '(?P<content_type>\w+)/(?P<object_id>\d+)/$',
        views.gallery_data,
        name='gallery_data'
    ),
]
