from django import forms

from . import models
from . import widgets

class ImageAdminForm(forms.ModelForm):
    """
    A form for the ImageAdmin.
    """

    def __init__(self, *args, **kwargs):
        # get 'initial' argument to determine whether the form
        # has been opened as a popup window
        initial = kwargs.get('initial')
        super(ImageAdminForm, self).__init__(*args, **kwargs)
        try:
            # get the class of the related model if it exists
            model_class = self.instance.content_type.model_class()
        except:
            # the related object is not specified
            model_class = None
        if initial and initial.get('_popup'):
            # do not show 'content_type' and 'object' id fields in
            # popup window to avoid changing related object since a popup
            # window could be opened from inline admin on the admin page
            # of existing object a new image will be attached to.
            self.fields['content_type'].widget = forms.HiddenInput()
            self.fields['object_id'].widget = forms.HiddenInput()
        else:
            # in general case set the model class to ObjectIdSelect
            self.fields['object_id'].widget.model_class = model_class

    def clean(self):
        """
        Sets the model class in the ObjectIdSelect to fill it with objects
        of selected model and returns cleaned data. 
        If the ObjectIdSelect widget has not specified model class, it would
        be empty in unproperly filled forms sent by user even if its value
        was selected before sending.
        """
        cleaned_data = super().clean()
        # with bound forms only
        if self.is_bound:
            try:
                # determine the model class if it exists
                # and set it to the ObjectIdSelect widget
                ctype = cleaned_data.get('content_type')
                model_class = ctype.model_class()
                self.fields['object_id'].widget.model_class = model_class
            except:
                pass
        return cleaned_data

    class Meta:
        model = models.Image
        # the form does not contain the 'position' field
        # since its value should be set automatically
        fields = ('image', 'content_type', 'object_id')
        widgets = {
            'image': widgets.ImageWidget,
            'content_type': widgets.ContentTypeSelect,
            'object_id': widgets.ObjectIdSelect,
        }


class ImageAdminInlineForm(forms.ModelForm):
    """
    A form for the Image admin inline.
    """
    class Meta:
        widgets = {
            # use hidden input for position, user would not
            # edit its value manually since it's set by JavaScript
            # when user sort images using drag'n'drop technique
            'position': forms.HiddenInput(
                attrs={
                    # the class used by JavaScript
                    'class': 'content-gallery-image-position'
                }
            ),
            'image': widgets.ImageInlineWidget()
        }
