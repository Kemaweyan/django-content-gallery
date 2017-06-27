import os
import json
import copy

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils import safestring
from django.template import loader
from django.db.models import BLANK_CHOICE_DASH
from django.contrib.admin import widgets
from django.utils import html

from . import utils
from . import settings
from . import fields

class ContentTypeSelect(forms.Select):
    """
    The widget for the content type select in the Image admin.
    """

    # the script that updates the list of objects of the selected model
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

    def _filter_choices(self):
        """
        Removes the ContentType objects that have not
        the 'gallery_visible' attribute set to True.
        """
        filtered_choices = []
        # initially self.choices contains all content types
        for choice in self.choices:
            try:
                if choice[0] == "":
                    # add the empty choice
                    filtered_choices.append(choice)
                    continue
                # get the content type and determine the model
                ctype = ContentType.objects.get(pk=int(choice[0]))
                model_class = ctype.model_class()
                if model_class.gallery_visible:
                    # add the choice if the model has the 'gallery_visible'
                    # attribute and it's set to True
                    filtered_choices.append(choice)
            except:
                # the model has not the 'gallery_visible' attribute
                pass
        # replace original choices
        self.choices = filtered_choices

    def render(self, name, value, attrs=None):
        """
        Filters the choices and adds the JavaScript code
        to the HTML of the widget. Returns the HTML code
        """
        self._filter_choices()  # change choices first
        output = super().render(name, value, attrs)
        # set the URL pattern in the JavaScript code
        js = self.js % utils.get_choices_url_pattern()
        # add the JavaScript code to the HTML
        output += js
        # do not escape the string
        return safestring.mark_safe(output)


class ObjectIdSelect(forms.Select):
    """
    The widget to select the related object in the Image admin.
    """

    def _create_choices(self):
        """
        Adds objects of the selected model to the choices list.
        """
        # copy the empty choice
        # we shouldn't add choices to original list
        # also in that case BLANK_CHOICE_DASH would keep
        # all previously added choices
        choices = copy.copy(BLANK_CHOICE_DASH)
        # add objects only if the model class specified
        if self.model_class:
            items = self.model_class.objects.all()
            for item in items:
                choices.append((str(item.id), item))
        # replace original choices
        self.choices = choices

    def render(self, name, value, attrs=None):
        """
        Returns the HTML code of the widget with available choices.
        """
        self._create_choices()  # create choices first
        return super().render(name, value, attrs)


class ImageWidget(widgets.AdminFileWidget):
    """
    The widget for the image field in the Image admin.
    Contains the image preview instead of simple link in default widget
    """
    # the HTML template of the widget with the image preview
    template = '''
        <p class="file-upload content-gallery-images">
          <span class="content-gallery-preview-container" 
            style="width: {}px; height: {}px;">
              <a class="content-gallery-preview content-gallery-inline-box
                content-gallery-centered-image content-gallery-images
                content-gallery-open-view" style="width: {}px; height: {}px;
                line-height: {}px;" href="#" data-image="{}">
                    <img src="%(initial_url)s" alt="Image preview">
              </a>
              <img src="{}" class="content-gallery-zoom 
                content-gallery-preview-zoom" style="left: {}px;" alt="zoom">
          </span>
          %(clear_template)s
          <br />
          %(input_text)s: %(input)s
        </p>'''

    def render(self, name, value, attrs=None):
        """
        Renders custom widget with the image preview for uploaded images
        or the default widget if the image has not yet been uploaded.
        """
        # if the image is uploaded, the 'image' argument
        # is an instance of GalleryImageFieldFile
        if isinstance(value, fields.GalleryImageFieldFile):
            # get image data
            data = utils.create_image_data(value)
            # fill the template and replace the default one
            self.template_with_initial = self.template.format(
                settings.CONF['preview_width'] + 14,
                settings.CONF['preview_height'] + 14,
                settings.CONF['preview_width'],
                settings.CONF['preview_height'],
                settings.CONF['preview_height'],
                html.escape(json.dumps(data)),
                utils.create_static_url("content_gallery/img/zoom.png"),
                settings.CONF['preview_width'] - 55
            )
        # render the widget
        return super().render(name, value, attrs)


class ImageInlineWidget(forms.Widget):
    """
    The widget for the image in the Image inline admin form.
    """
    template_name = 'content_gallery/admin/edit_inline/image_widget.html'

    def render(self, name, value, attrs=None):
        """
        Renders the widget using the template file.
        """
        # return empty string for non-existing image
        if not value:
            return "";
        # get image data
        data = utils.create_image_data(value)
        # the widget contains the small preview image
        context = {
            "preview_src": value.small_preview_url,
            "image_data": json.dumps(data)
        }
        # render the widget
        return loader.render_to_string(self.template_name, context)
