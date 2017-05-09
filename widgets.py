import os
import json

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.db.models import BLANK_CHOICE_DASH
from django.contrib.admin import widgets
from django.utils.html import escape

from . import utils
from . import settings

class ContentTypeSelect(forms.Select):

    def _filter_choices(self):
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

    def render(self, name, value, attrs=None):
        self._filter_choices()
        output = super().render(name, value, attrs)
        js = '''<script type="text/javascript">
            (function($) {
                $(function() {
                    $("#id_content_type").change(function() {
                        $("#id_object_id option:gt(0)").remove();
                        if (!this.value) return
                        $.ajax({
                            url: "%s" + this.value,
                            dataType: "json",
                            success: function (result) {
                                var $el = $("#id_object_id");
                                $.each(result, function (i, product) {
                                    $el.append($("<option></option>")
                                        .attr("value", product.id)
                                        .text(product.name));
                                });
                            }
                        });
                    });
                });
            })(django.jQuery);
        </script>'''
        output += js % utils.get_choices_url_pattern()
        return mark_safe(output)


class ObjectIdSelect(forms.Select):

    def _create_choices(self):
        choices = BLANK_CHOICE_DASH
        if self.model_class:
            items = self.model_class.objects.all()
            for item in items:
                choices.append((str(item.id), item))
        self.choices = choices

    def render(self, name, value, attrs=None):
        self._create_choices()
        return super().render(name, value, attrs)


class ImageWidget(widgets.AdminFileWidget):
    template = (
        '<p class="file-upload">'
        '<span class="content-gallery-preview content-gallery-inline-box '
        'content-gallery-centered-image content-gallery-images" '
        'style="width: {}px; height: {}px; line-height: {}px;">'
        '<a href="#" data-image="{}" class="content-gallery-open-view">'
        '<img src="%(initial_url)s" alt="Image preview"></a></span>'
        '%(clear_template)s<br />%(input_text)s: %(input)s</p>'
    )

    def render(self, name, image, attrs=None):
        if image:
            data = utils.create_image_data(image)
            self.template_with_initial = self.template.format(
                settings.GALLERY_PREVIEW_WIDTH,
                settings.GALLERY_PREVIEW_HEIGHT,
                settings.GALLERY_PREVIEW_HEIGHT,
                escape(json.dumps(data))
            )
        return super().render(name, image, attrs)


class ImageInlineWidget(forms.Widget):
    template_name = 'content_gallery/admin/edit_inline/image_widget.html'

    def render(self, name, image, attrs=None):
        if not image:
            return "";
        data = utils.create_image_data(image)
        context = {
            "preview_src": image.small_preview_url,
            "image_data": json.dumps(data)
        }
        return render_to_string(self.template_name, context)
