from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

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
        output += '''<script type="text/javascript">
            (function($) {
                $(document).ready(function() {
                    $("#id_content_type").change(function() {
                        $("#id_object_id option:gt(0)").remove();
                        if (!this.value) return
                        $.ajax({
                            url: "/gallery/ajax/choices/" + this.value,
                            dataType: "json",
                            success: function (result) {
                                $el = $("#id_object_id");
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
        return mark_safe(output)


class ObjectIdSelect(forms.Select):

    def _create_choices(self):
        choices = [("", "---------")]
        if self.model_class:
            items = self.model_class.objects.all()
            for item in items:
                choices.append((str(item.id), item))
        self.choices = choices

    def render(self, name, value, attrs=None):
        self._create_choices()
        return super().render(name, value, attrs)
