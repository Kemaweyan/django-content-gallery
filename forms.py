from django.forms import ModelForm

from . import models
from . import widgets

class ImageAdminForm(ModelForm):

    class Meta:
        model = models.Image
        fields = ('src', 'content_type', 'object_id')
        widgets = {'content_type': widgets.ContentTypeSelect}
