from django.views import generic

from . import models

class CatListView(generic.ListView):
    model = models.Cat
    template_name = 'testapp/cat_list.html'
    context_object_name = 'cats'


class CatDetailView(generic.DetailView):
    model = models.Cat
    template_name = 'testapp/cat_detail.html'
    context_object_name = 'cat'
