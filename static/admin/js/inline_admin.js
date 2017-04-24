(function ($) {
    $(function () {

        $(".imagesContainer").sortable({
            cursor: "move",
            revert: 200,
            tolerance: "pointer",
            connectWith: ".imagesContainer",
            handle: ".imageHeader",
            items: "> :not(.addNewImage)",
            placeholder: "placeholder",
            update: function (event, ui) {
                $("#sortedImages").find(".image-position").each(function (i) {
                    $(this).val(i);
                });
                $("#sortedImages").find(".image-delete").find("input").val();
                $("#imagesToDelete").find(".image-delete").find("input").val(1);
            }
        });

        $("#id_image").on("change", function () {
            var image_id = this.value;

            var $group = $(".gallery-inline-formset");

            var opts = $group.attr("data-inline-formset");
            var obj = JSON.parse(opts);
            var prefix = obj.options.prefix;

            var $totla_forms = $group.find("#id_" + prefix + "-TOTAL_FORMS");
            var new_id = $totla_forms.val();

            var new_prefix = prefix + "-" + new_id;
            $totla_forms.val(parseInt(new_id) + 1);

            var url = "/admin/gallery/image/ajax/preview/" + image_id;
            $.ajax({
                url: url,
                dataType: "json",
                beforeSend: function(xhr) {
                    if (xhr.overrideMimeType)
                        xhr.overrideMimeType("application/json");
                },
                success: function (response) {
                    $("#sortedImages").find(".addNewImage").before(
                        $("<div></div>")
                        .addClass("imageObject")
                        .append(
                            $("<div></div>")
                            .addClass("imageHeader")
                            .addClass("imageHeaderBg")
                        )
                        .append(
                            $("<div></div>")
                            .addClass("imageContent")
                            .append(
                                $("<span></span>")
                                .addClass("image-delete")
                                .append(
                                    $("<input>")
                                    .attr("type", "hidden")
                                    .attr("id", "id_" + new_prefix + "-DELETE")
                                    .attr("name", new_prefix + "-DELETE")
                                    .val(0)
                                )
                            )
                            .append(
                                $("<img>")
                                .attr("src", response.preview_url)
                            )
                                .append(
                                $("<input>")
                                .addClass("image-position")
                                .attr("type", "hidden")
                                .attr("id", "id_" + new_prefix + "-position")
                                .attr("name", new_prefix + "-position")
                                .val(response.position)
                            )
                            .append(
                                $("<input>")
                                .attr("type", "hidden")
                                .attr("id", "id_" + new_prefix + "-id")
                                .attr("name", new_prefix + "-id")
                                .val(image_id)
                            )
                        )
                    );
                }
            });
        });
    });
})(django.jQuery);
