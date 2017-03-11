from django.conf.urls import url

from . import views

app_name = 'gallery'

urlpatterns = [
    url(
        r'^ajax/choices/(?P<pk>\d+)$',
        views.choices,
        name='choices'
    ),
]
