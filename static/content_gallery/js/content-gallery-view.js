(function ($) {

    window.ContentGallery = window.ContentGallery || {};

    var galleryView = (function (gallery, animateSync) {
        var $galleryView,
            $imageContainer,
            $image,
            $thumbnails,
            $scrollLeft,
            $scrollRight,
            $choices,
            $thumbnailsView,
            $imageView,
            $thumbnailsContainer;

        var thumbnailWidth, maxOffset;
        var ready = false;

        function isSmall() {
            return ContentGallery.isSmallHelper(gallery.getImageSize().width + 220,
                gallery.getImageSize().height + gallery.getThumbnailSize().height + 85);
        }

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
            left = parseInt($thumbnails.css("left"));
            begin = thumbnailWidth * index;
            end = thumbnailWidth * (index + 1);

            if (left + begin >= 0 && left + end <= $thumbnailsContainer.width())
                return;

            if (left + begin < 0)
                newLeft = -begin;

            if (left + end > $thumbnailsContainer.width())
                newLeft = $thumbnailsContainer.width() - end;

            animateSync.safeAnimate($thumbnails, {left: newLeft}, null);
            checkScrollButtons(newLeft);
        }

        function setImage(index, callback) {
            img = gallery.getImage(index);
            if (!img) return;
            $choices.addClass("choice");
            $($choices[index]).removeClass("choice");
            if (isSmall()) {
                src = img.small_image;
                size = img.small_image_size;
            } else {
                src = img.image;
                size = img.image_size;
            }
            callback(size, src);
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

            container_width = Math.ceil(imgSize.width / thumbnailWidth) * thumbnailWidth;
            if (container_width > imgSize.width + 140)
                container_width -= thumbnailWidth;

            $thumbnailsView.width(container_width + 60);
            $choices.width(thumbnailSize.width)
                    .height(thumbnailSize.height)
                    .css("line-height", thumbnailSize.height + "px");
            $thumbnailsView.height(thumbnailSize.height + 2);
            $thumbnailsContainer.width(container_width);
        }

        function setGalleryViewSize(imgSize, thumbnailSize) {
            ContentGallery.setViewSizeHelper($galleryView, $imageView, $imageContainer,
                                            imgSize.width, imgSize.height, 200, thumbnailSize.height + 45);
        }

        function setGalleryViewPosition() {
            ContentGallery.setViewPositionHelper($galleryView);
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

        function scrollLeft() {
            animateSync.safeRun(function () {
                left = parseInt($thumbnails.css("left"));
                if (left < 0) {
                    animateSync.safeAnimate($thumbnails, {left: "+=" + thumbnailWidth}, null);
                    checkScrollButtons(left + thumbnailWidth);
                }
            });
        }

        function scrollRight() {
            animateSync.safeRun(function () {
                left = parseInt($thumbnails.css("left"));
                if (left > maxOffset) {
                    animateSync.safeAnimate($thumbnails, {left: "-=" + thumbnailWidth}, null);
                    checkScrollButtons(left - thumbnailWidth);
                }
            });
        }

        function resize() {
            if (!ready) return;

            imgSize = isSmall() ? gallery.getSmallImageSize() : gallery.getImageSize();
            thumbnailSize = gallery.getThumbnailSize()
                
            thumbnailWidth = thumbnailSize.width + 8;

            setThumbnailViewSize(imgSize, thumbnailSize);

            maxOffset = $thumbnailsContainer.width() - $thumbnails.width();

            checkScrollButtons(0);

            setGalleryViewSize(imgSize, thumbnailSize);
            setGalleryViewPosition();

            index = gallery.current();
            setImageFast(index);
        }

        function init(app_label, content_type, object_id) {
            $galleryView = $("#content-gallery-view");
            $imageView = $("#content-gallery-image-view");
            $imageContainer = $(".content-gallery-image-container");
            $image = $(".content-gallery-image-container > img");
            $thumbnailsView = $("#content-gallery-thumbnails-view");
            $scrollLeft = $(".content-gallery-scroll-left");
            $scrollRight = $(".content-gallery-scroll-right");
            $thumbnailsContainer = $(".content-gallery-thumbnails-container");
            $thumbnails = $(".content-gallery-thumbnails-container > ul");

            if (!ready) {
                $thumbnails.on("click", "li.choice", function () {
                    setImageByIndex($(this).index());
                });

                $(".content-gallery-prev-image").click(previousImage)
                $(".content-gallery-next-image").click(nextImage);
                $scrollLeft.click(scrollLeft);
                $scrollRight.click(scrollRight);
            }

            $thumbnails.empty();

            gallery.load(app_label, content_type, object_id, function (data) {
                $.each(data, function (index, img) {
                    $thumbnails.append($("<li></li>")
                                .addClass("choice")
                                .addClass("content-gallery-centered-image")
                                .append($("<img>")
                                    .attr("src", img.thumbnail)
                                    )
                                );
                });

                $choices = $thumbnails.children();

                ready = true;
                resize();

                $("#content-gallery").show();
            });
        }

        return {
            init: init,
            resize: resize
        };
    })(ContentGallery.gallery, ContentGallery.animateSync);

    ContentGallery.galleryView = galleryView;

    $(window).resize(galleryView.resize);

    $(function () {
        $(".content-gallery-open-view").click(function() {
            matches = $(this).attr("id").match(/^gallery-(\w+)-(\w+)-(\d+)$/i);
            if (!matches) return;
            app_label = matches[1];
            content_type = matches[2];
            object_id = matches[3];
            galleryView.init(app_label, content_type, object_id);
        });

        $(".content-gallery-close").click(function() {
            $("#content-gallery").hide();
        });
    });
})(jQuery);
