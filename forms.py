from django.forms import ModelForm

from . import models
from . import widgets

class ImageAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ImageAdminForm, self).__init__(*args, **kwargs)
        try:
            model_class = self.instance.content_type.model_class()
        except:
            model_class = None
        self.fields['object_id'].widget.model_class = model_class

    def clean(self):
        cleaned_data = super().clean()
        if self.is_bound:
            try:
                ctype = cleaned_data.get('content_type')
                model_class = ctype.model_class()
                self.fields['object_id'].widget.model_class = model_class
            except:
                pass
        return cleaned_data

    class Meta:
        model = models.Image
        fields = ('image', 'content_type', 'object_id')
        widgets = {
            'content_type': widgets.ContentTypeSelect,
            'object_id': widgets.ObjectIdSelect,
        }
