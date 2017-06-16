(function ($) {

    window.ContentGallery = window.ContentGallery || {};

    var animateSync = (function () {
        var activeTasks = 0;

        function safeRun(callback) {
            if (activeTasks > 0) return;

            callback();
        }

        function safeAnimate($obj, css) {
            ++activeTasks;

            return $obj.animate(css)
            .promise()
            .then(function () {
                --activeTasks;
            });
        }

        return {
            safeRun: safeRun,
            safeAnimate: safeAnimate
        };
    })();

    ContentGallery.animateSync = animateSync;

})(jQuery);
