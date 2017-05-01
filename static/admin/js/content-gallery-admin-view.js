(function ($) {
    window.ContentGallery = window.ContentGallery || {};

    var galleryAdminView = (function () {
        var $galleryView,
            $imageView,
            $imageContainer,
            $img;

        var imageData, image;

        function isSmall() {
            return ContentGallery.isSmallHelper(imageData.image.width + 40, imageData.image.height + 65);
        }

        function setViewSize() {
            ContentGallery.setViewSizeHelper($galleryView, $imageView, $imageContainer, image.width, image.height, 0, 25);
        }

        function setViewPosition() {
            ContentGallery.setViewPositionHelper($galleryView);
        }

        function init() {
            $galleryView = $("#content-gallery-view");
            $imageView = $("#content-gallery-image-view");
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

    ContentGallery.galleryAdminView = galleryAdminView;
})(django.jQuery);
