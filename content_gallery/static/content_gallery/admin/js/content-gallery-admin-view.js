(function ($) {
    window.ContentGallery = window.ContentGallery || {};

    var galleryAdminView = (function () {
        var $imageView,
            $imageContainer,
            $img;

        var imageData, image;

        function setImageHeight(height) {
            $imageView.height(height);
            $imageContainer.css({"line-height": height + "px"});
        }

        function init() {
            $imageView = $("#content-gallery-image-view");
            $imageContainer = $imageView.find(".content-gallery-image-container");
            $img = $imageContainer.find("img");
        }

        function getSize(isSmall) {
            var small = isSmall(imageData.image.width, imageData.image.height);
            image = small ? imageData.small_image : imageData.image;
            resize();
            return {width: image.width, height: image.height};
        }

        function resize() {
            setImageHeight(image.height);
            $img.attr("src", image.url);
        }

        function setData(data, callback) {
            imageData = data;
            callback();
        }

        return {
            init: init,
            resize: resize,
            setData: setData,
            getSize: getSize
        };
    })();

    ContentGallery.galleryAdminView = galleryAdminView;

    $(function () {
        galleryAdminView.init();
        ContentGallery.galleryView.init(galleryAdminView);
    });
})(django.jQuery);
