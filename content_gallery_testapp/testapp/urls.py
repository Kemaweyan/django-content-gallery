from django.conf.urls import url

from . import views

app_name = 'testapp'

urlpatterns = [
    url(
        r'^cat/$',
        views.CatListView.as_view(),
        name='cat_list'
    ),
    url(
        r'^cat/(?P<pk>\d+)/$',
        views.CatDetailView.as_view(),
        name='cat_detail'
    ),
]
