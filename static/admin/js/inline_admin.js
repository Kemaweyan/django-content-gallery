(function ($) {

    var galleryView = (function () {
            var $imageView,
                $imageContainer,
                $img;

            var winWidth, winHeight, imageData, image;

            function isSmall() {
                winWidth = $(window).width();
                winHeight = $(window).height();

                return winWidth < imageData.image.width + 40 ||
                       winHeight < imageData.image.height + 65;
            }

            function setViewSize() {
                $imageView.width(image.width);
                $imageView.height(image.height + 25);
                $imageContainer.height(image.height);
                $imageContainer.css({"line-height": image.height + "px"});
            }

            function setViewPosition() {
                galLeft = (winWidth - $imageView.outerWidth()) / 2;
                galTop = (winHeight - $imageView.outerHeight()) / 2;

                $imageView.css({"top": galTop, "left": galLeft});
            }

            function init() {
                $imageView = $("#content-gallery-view");
                $imageContainer = $imageView.find(".content-gallery-image-container");
                $img = $imageContainer.find("img");
            }

            function resize() {
                image = isSmall() ? imageData.small_image : imageData.image;
                setViewSize();
                setViewPosition();
                $img.attr("src", image.url);
            }

            function setImage(data) {
                imageData = data;
                resize();
            }

            return {
                init: init,
                resize: resize,
                setImage: setImage
            };
        })();

    $(function () {

        $(".images-container").sortable({
            cursor: "move",
            revert: 200,
            tolerance: "pointer",
            connectWith: ".images-container",
            handle: ".image-header",
            items: "> :not(.add-new-image)",
            placeholder: "placeholder",
            update: function (event, ui) {
                $("#gallery-sorted-images").find(".image-position").each(function (i) {
                    $(this).val(i);
                });
                $("#gallery-sorted-images").find(".image-delete").find("input").removeAttr("value");
                $("#gallery-images-to-delete").find(".image-delete").find("input").val(1);
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
            var new_forms_count = parseInt(new_id) + 1;

            var new_prefix = prefix + "-" + new_id;
            $totla_forms.val(new_forms_count);
            $group.find("#id_" + prefix + "-INITIAL_FORMS").val(new_forms_count);

            var url = "/admin/gallery/image/ajax/preview/" + image_id;
            $.ajax({
                url: url,
                dataType: "json",
                beforeSend: function(xhr) {
                    if (xhr.overrideMimeType)
                        xhr.overrideMimeType("application/json");
                },
                success: function (response) {
                    $("#gallery-sorted-images").find(".add-new-image").before(
                        $("<div></div>")
                        .addClass("image-object")
                        .append(
                            $("<div></div>")
                            .addClass("image-header")
                        )
                        .append(
                            $("<div></div>")
                            .addClass("image-content")
                            .append(
                                $("<span></span>")
                                .addClass("image-delete")
                                .append(
                                    $("<input>")
                                    .attr("type", "hidden")
                                    .attr("id", "id_" + new_prefix + "-DELETE")
                                    .attr("name", new_prefix + "-DELETE")
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

        galleryView.init();
        $(window).resize(galleryView.resize);

        var $adminImageView = $("#content-gallery-admin-preview");

        $(".gallery-inline-formset").on("click", ".gallery-image-preview", function (e) {
            e.preventDefault();

            var data = JSON.parse($(this).attr("data-image"));
            galleryView.setImage(data);

            $adminImageView.show();
        });

        $("#content-gallery-admin-preview").on("click", ".content-gallery-close", function () {
            $adminImageView.hide();
        });
    });
})(django.jQuery);
