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
                $("#sortedImages").find(".image-delete").val(0);
                $("#imagesToDelete").find(".image-delete").val(1);
            }
        });
    });
})(django.jQuery);
