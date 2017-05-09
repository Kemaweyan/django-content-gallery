(function ($) {

    window.ContentGallery = window.ContentGallery || {};

    var galleryView = (function () {
        var contentView,
            $galleryViewBox,
            $galleryView;

        var winWidth, winHeight;

        function isSmall(width, height) {
            winWidth = $(window).width();
            winHeight = $(window).height();

            return winWidth < width + 40 || winHeight < height + 65;
        }

        function setViewPosition() {
            galLeft = (winWidth - $galleryView.outerWidth()) / 2;
            galTop = (winHeight - $galleryView.outerHeight()) / 2;

            $galleryView.css({"top": galTop, "left": galLeft});
        }

        function resize() {
            var size = contentView.getSize(isSmall);
            $galleryView.width(size.width);
            $galleryView.height(size.height + 25);
            setViewPosition();
        }

        function show(data) {
            contentView.setData(data, function () {
                resize();
                $galleryViewBox.show();
            });
        }

        function hide() {
            $galleryViewBox.hide();
        }

        function init(view) {
            contentView = view;
            $galleryViewBox = $("#content-gallery");
            $galleryView = $("#content-gallery-view");
        }

        return {
            init: init,
            resize: resize,
            show: show,
            hide: hide
        };
    })();

    ContentGallery.galleryView = galleryView;

    $(function () {
        $(window).resize(galleryView.resize);

        $(".content-gallery-open-view").click(function(e) {
            e.preventDefault();

            var data = JSON.parse($(this).attr("data-image"));
            galleryView.show(data);
        });

        $(".content-gallery-close").click(galleryView.hide);
    });
})(jQuery);
