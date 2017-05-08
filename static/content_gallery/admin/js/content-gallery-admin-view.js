(function ($) {
    window.ContentGallery = window.ContentGallery || {};

    var galleryAdminView = (function () {
        var $imageView,
            $imageContainer,
            $img;

        var imageData, imageSize, small, image;

        function setViewSize() {
            $imageView.height(height);
            $imageContainer.css({"line-height": height + "px"});
        }

        function init(size) {
            imageSize = size;
            $imageView = $("#content-gallery-image-view");
            $imageContainer = $imageView.find(".content-gallery-image-container");
            $img = $imageContainer.find("img");
        }

        function resize(isSmall) {
            var small = isSmall(imageSize.width, imageSize.height)
            var image = small ? imageData.small_image : imageData.image;
            setViewSize();
            setViewPosition();
            $img.attr("src", image.url);
        }

        function setData(data) {
            imageData = data;
        }

        return {
            init: init,
            resize: resize,
            setData: setData
        };
    })();

    ContentGallery.galleryAdminView = galleryAdminView;

    $(function () {
        $.ajax({
            url: "/gallery/ajax/gallery_sizes/",
            dataType: "json",
            beforeSend: function(xhr) {
                if (xhr.overrideMimeType)
                    xhr.overrideMimeType("application/json");
            },
            success: function (response) {
                var size = response.image_size;
                galleryAdminView.init(size);
                ContentGallery.galleryView.init(galleryAdminView);
            }
        });
    });
})(django.jQuery);
