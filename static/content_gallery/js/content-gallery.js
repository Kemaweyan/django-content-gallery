(function ($) {

    window.ContentGallery = window.ContentGallery || {};

    var gallery = (function () {
        var images = [];
        var currentImage = 0;

        var imageSize = null;
        var smallImageSize = null;
        var thumbnailSize = null;

        function getImage(index) {
            currentImage = index;
            if (currentImage >= images.length)
                return null;
            return images[currentImage];
        }

        function getCurrent() {
            return currentImage;
        }

        function getNext() {
            ++currentImage;
            if (currentImage >= images.length)
                currentImage = 0;
            return getCurrent();
        }

        function getPrevious() {
            if (currentImage <= 0)
                currentImage = images.length;
            --currentImage;
            return getCurrent();
        }

        function loadData(app_label, content_type, object_id, callback) {
            currentImage = 0;
            var url = $("#content-gallery").attr("data-url-pattern") + app_label + "/" + content_type + "/" + object_id;

            $.ajax({
                url: url,
                dataType: "json",
                beforeSend: function(xhr) {
                    if (xhr.overrideMimeType)
                        xhr.overrideMimeType("application/json");
                },
                success: function (response) {
                    images= response.images;
                    imageSize = response.image_size;
                    smallImageSize = response.small_image_size;
                    thumbnailSize = response.thumbnail_size;
                    callback(images);
                }
            });
        }

        function getImageSize() {
            return imageSize;
        }

        function getSmallImageSize() {
            return smallImageSize;
        }

        function getThumbnailSize() {
            return thumbnailSize;
        }

        function getCount() {
            return images.length;
        }

        return {
            getImage: getImage,
            current: getCurrent,
            next: getNext,
            prev: getPrevious,
            load: loadData,
            getImageSize: getImageSize,
            getSmallImageSize: getSmallImageSize,
            getThumbnailSize: getThumbnailSize,
            count: getCount
        };
    })();

    ContentGallery.gallery = gallery;

})(jQuery);
