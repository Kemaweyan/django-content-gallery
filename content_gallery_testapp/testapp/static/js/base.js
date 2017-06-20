(function ($) {
    function setContentHeight() {
        var winHeight = $(window).height();
        var height = winHeight - 274;
        if (height < 500)
            height = 500;
        $(".cat-content").css({'min-height': height + "px"});
    }

    $(window).resize(setContentHeight);

    $(function () {
        setContentHeight();
    });
})(jQuery);
