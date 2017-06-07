(function ($) {

    window.ContentGallery = window.ContentGallery || {};

    var gallerySiteView = (function (gallery, animateSync) {
        var $imageContainer,
            $image,
            $thumbnails,
            $scrollLeft,
            $scrollRight,
            $choices,
            $thumbnailsView,
            $imageView,
            $thumbnailsContainer;

        var thumbnailWidth, maxOffset, imgSize, thumbnailSize, small;

        function checkScrollButtons(left) {
            if (left < 0)
                $scrollLeft.removeClass("content-gallery-inactive");
            else
                $scrollLeft.addClass("content-gallery-inactive");

            if (left > maxOffset)
                $scrollRight.removeClass("content-gallery-inactive");
            else
                $scrollRight.addClass("content-gallery-inactive");
        }

        function scrollToImage(index) {
            var left = thumbnailsLeft();
            var begin = thumbnailWidth * index;
            var end = thumbnailWidth * (index + 1);

            var newLeft = left;

            if (left + begin >= 0 && left + end <= $thumbnailsContainer.width()) {

                if (left < maxOffset)
                    newLeft = maxOffset;
            } else {

                if (left + begin < 0)
                    newLeft = -begin;

                if (left + end > $thumbnailsContainer.width())
                    newLeft = $thumbnailsContainer.width() - end;
            }

            if (left != newLeft)
                animateSync.safeAnimate($thumbnails, {left: newLeft}, null);

            checkScrollButtons(newLeft);
        }

        function loadImage(src, callback) {
            var img = new Image();
            //img.onload = callback;
            img.src = src;
        }

        function setImage(index, callback) {
            var img = gallery.getImage(index);
            if (!img) return;
            $choices.addClass("choice");
            $($choices[index]).removeClass("choice");
            if (small) {
                src = img.small_image;
                size = img.small_image_size;
            } else {
                src = img.image;
                size = img.image_size;
            }
            loadImage(src, function () {
                callback(size, src);
            });
        }

        function setImageAnim(index) {
            setImage(index, function (size, src) {
                animateSync.safeAnimate($image, {width: 0, height: 0}, function () {
                    $image.attr("src", src);
                    animateSync.safeAnimate($image, {width: size.width, height: size.height}, null);
                });
            });
        }

        function setImageFast(index) {
            setImage(index, function (size, src) {
                $image.attr("src", src).css({width: size.width, height: size.height});
            });
        }

        function slideImage(index) {
            setImageAnim(index);
            scrollToImage(index);
        }

        function setThumbnailViewSize(imgSize, thumbnailSize) {
            $thumbnails.width(thumbnailWidth * gallery.count());

            var container_width = Math.ceil(imgSize.width / thumbnailWidth) * thumbnailWidth;
            if (container_width > imgSize.width + 140)
                container_width -= thumbnailWidth;

            $thumbnailsView.width(container_width + 60);
            $choices.width(thumbnailSize.width)
                    .height(thumbnailSize.height)
                    .css("line-height", thumbnailSize.height + "px");
            $thumbnailsView.height(thumbnailSize.height + 2);
            $thumbnailsContainer.width(container_width);
        }

        function setImageHeight(height) {
            $imageView.height(height);
            $imageContainer.css({"line-height": height + "px"});
        }

        function nextImage() {
            animateSync.safeRun(function () {
                index = gallery.next();
                slideImage(index);
            });
        }

        function previousImage() {
            animateSync.safeRun(function () {
               index = gallery.prev();
               slideImage(index);
            });
        }

        function setImageByIndex(index) {
            animateSync.safeRun(function () {
                setImageAnim(index);
            });
        }

        function thumbnailsLeft() {
            return parseInt($thumbnails.css("left"));
        }

        function thumbnailsReset() {
            $thumbnails.empty();
            $thumbnails.css("left", 0);
        }

        function scrollLeft() {
            animateSync.safeRun(function () {
                left = thumbnailsLeft();
                if (left < 0) {
                    animateSync.safeAnimate($thumbnails, {left: "+=" + thumbnailWidth}, null);
                    checkScrollButtons(left + thumbnailWidth);
                }
            });
        }

        function scrollRight() {
            animateSync.safeRun(function () {
                left = thumbnailsLeft();
                if (left > maxOffset) {
                    animateSync.safeAnimate($thumbnails, {left: "-=" + thumbnailWidth}, null);
                    checkScrollButtons(left - thumbnailWidth);
                }
            });
        }

        function resize() {
            setThumbnailViewSize(imgSize, thumbnailSize);
            maxOffset = $thumbnailsContainer.width() - $thumbnails.width();

            setImageHeight(imgSize.height);

            var index = gallery.current();
            setImageFast(index);
            scrollToImage(index);
        }

        function init() {
            $imageView = $("#content-gallery-image-view");
            $imageContainer = $(".content-gallery-image-container");
            $image = $(".content-gallery-image-container > img");
            $thumbnailsView = $("#content-gallery-thumbnails-view");
            $scrollLeft = $(".content-gallery-scroll-left");
            $scrollRight = $(".content-gallery-scroll-right");
            $thumbnailsContainer = $(".content-gallery-thumbnails-container");
            $thumbnails = $(".content-gallery-thumbnails-container > ul");

            $thumbnails.on("click", "li.choice", function () {
                setImageByIndex($(this).index());
            });

            $(".content-gallery-prev-image").click(previousImage)
            $(".content-gallery-next-image").click(nextImage);
            $scrollLeft.click(scrollLeft);
            $scrollRight.click(scrollRight);
        }

        function getSize(isSmall) {
            var size = gallery.getImageSize();
            thumbnailSize = gallery.getThumbnailSize();
            small = isSmall(size.width + 200, size.height + thumbnailSize.height + 45);
            imgSize = small ? gallery.getSmallImageSize() : gallery.getImageSize();
            thumbnailWidth = thumbnailSize.width + 8;
            resize();
            return {width: imgSize.width + 200, height: imgSize.height + thumbnailSize.height + 45};
        }

        function setData(data, callback) {
            thumbnailsReset();

            gallery.load(data.app_label, data.content_type, data.object_id, function (response) {
                $.each(response, function (index, img) {
                    $thumbnails.append($("<li></li>")
                                .addClass("choice")
                                .addClass("content-gallery-centered-image")
                                .append($("<img>")
                                    .attr("src", img.thumbnail)
                                    )
                                );
                });

                $choices = $thumbnails.children();
                callback();
            });
        }

        return {
            init: init,
            resize: resize,
            setData: setData,
            getSize: getSize
        };
    })(ContentGallery.gallery, ContentGallery.animateSync);

    ContentGallery.gallerySiteView = gallerySiteView;

    $(function () {
        gallerySiteView.init();
        ContentGallery.galleryView.init(gallerySiteView);
    });
})(jQuery);
