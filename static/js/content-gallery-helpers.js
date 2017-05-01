window.django = window.django || {};
django.jQuery = django.jQuery || jQuery;

(function ($) {

    window.ContentGallery = window.ContentGallery || {};

    var winWidth, winHeight;

    function isSmall(width, height) {
        winWidth = $(window).width();
        winHeight = $(window).height();

        return winWidth < width || winHeight < height;
    }
    ContentGallery.isSmallHelper = isSmall;

    function setViewPosition($view) {
        galLeft = (winWidth - $view.outerWidth()) / 2;
        galTop = (winHeight - $view.outerHeight()) / 2;

        $view.css({"top": galTop, "left": galLeft});
    }
    ContentGallery.setViewPositionHelper = setViewPosition;

    function setViewSize($view, $subView, $container, width, height,  additional_width, additional_height) {
        $view.width(width + additional_width);
        $view.height(height + additional_height);
        $subView.height(height);
        $container.css({"line-height": height + "px"});
    }
    ContentGallery.setViewSizeHelper = setViewSize;

})(django.jQuery);
