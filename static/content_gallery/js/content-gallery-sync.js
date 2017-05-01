(function ($) {

    window.ContentGallery = window.ContentGallery || {};

    var animateSync = (function () {
        var activeTasks = 0;

        function safeRun(callback) {
            if (activeTasks > 0) return;

            callback();
        }

        function safeAnimate($obj, css, callback) {
            ++activeTasks;

            $obj.animate(css, function () {
                --activeTasks;

                if (callback)
                    callback();
            });
        }

        return {
            safeRun: safeRun,
            safeAnimate: safeAnimate
        };
    })();

    ContentGallery.animateSync = animateSync;

})(jQuery);
