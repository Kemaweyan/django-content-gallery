from django.utils.safestring import mark_safe
from django import forms
from django.contrib.contenttypes.models import ContentType

class ContentTypeSelect(forms.Select):

    def render(self, name, value, attrs=None):
        filtered_choices = []
        for choice in self.choices:
            try:
                if choice[0] == "":
                    filtered_choices.append(choice)
                    continue
                ctype = ContentType.objects.get(pk=int(choice[0]))
                model_class = ctype.model_class()
                if model_class.gallery_visible:
                    filtered_choices.append(choice)
            except:
                pass
        self.choices = filtered_choices
        return super().render(name, value, attrs)

