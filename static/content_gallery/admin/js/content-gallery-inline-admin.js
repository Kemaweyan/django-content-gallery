(function ($) {

    window.ContentGallery = window.ContentGallery || {};

    galleryAdminView = ContentGallery.galleryAdminView;

    $(function () {

        $(".content-gallery-images-container").sortable({
            cursor: "move",
            revert: 200,
            tolerance: "pointer",
            connectWith: ".content-gallery-images-container",
            handle: ".content-gallery-image-header",
            items: "> :not(.content-gallery-add-new-image)",
            placeholder: "content-gallery-placeholder",
            update: function (event, ui) {
                $("#content-gallery-sorted-images").find(".content-gallery-image-position").each(function (i) {
                    $(this).val(i);
                });
                $("#content-gallery-sorted-images").find(".content-gallery-image-delete").find("input").removeAttr("value");
                $("#content-gallery-images-to-delete").find(".content-gallery-image-delete").find("input").val(1);
            }
        });

        $("#id_image").on("change", function () {
            var image_id = this.value;

            var $group = $(".content-gallery-images");

            var opts = $group.attr("data-inline-formset");
            var obj = JSON.parse(opts);
            var prefix = obj.options.prefix;

            var $totla_forms = $group.find("#id_" + prefix + "-TOTAL_FORMS");
            var new_id = $totla_forms.val();
            var new_forms_count = parseInt(new_id) + 1;

            var new_prefix = prefix + "-" + new_id;
            $totla_forms.val(new_forms_count);
            $group.find("#id_" + prefix + "-INITIAL_FORMS").val(new_forms_count);

            var url = $group.attr("data-preview-url-pattern") + image_id;
            $.ajax({
                url: url,
                dataType: "json",
                beforeSend: function(xhr) {
                    if (xhr.overrideMimeType)
                        xhr.overrideMimeType("application/json");
                },
                success: function (response) {
                    $("#content-gallery-sorted-images").find(".content-gallery-add-new-image").before(
                        $("<div></div>")
                        .addClass("content-gallery-image-object")
                        .append(
                            $("<div></div>")
                            .addClass("content-gallery-image-header")
                        )
                        .append(
                            $("<div></div>")
                            .addClass("content-gallery-image-content")
                            .append(
                                $("<span></span>")
                                .addClass("content-gallery-image-delete")
                                .append(
                                    $("<input>")
                                    .attr("type", "hidden")
                                    .attr("id", "id_" + new_prefix + "-DELETE")
                                    .attr("name", new_prefix + "-DELETE")
                                )
                            )
                            .append(
                                $("<span></span>")
                                .addClass("content-gallery-preview-container")
                                .append(
                                    $("<a></a>")
                                    .addClass("content-gallery-image-content-link")
                                    .addClass("content-gallery-open-view")
                                    .addClass("content-gallery-block-box")
                                    .addClass("content-gallery-centered-image")
                                    .attr("href", "#")
                                    .attr("data-image", response.image_data)
                                    .append(
                                        $("<img>")
                                        .addClass("content-gallery-image-preview")
                                        .attr("src", response.small_preview_url)
                                    )
                                )
                                .append(
                                    $("<img>")
                                    .addClass("content-gallery-zoom")
                                    .addClass("content-gallery-inline-preview-zoom")
                                    .attr("src", response.zoom_url)
                                )
                            )
                            .append(
                                $("<input>")
                                .addClass("content-gallery-image-position")
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
