(function ($) {

    $(function () {
        landing ('article.landing');
        register ('article.register');
    });


    var landing = function (sel) {
        if ($(sel).length) {
            mixpanel.track('Viewed landing');
        }
    };

    var register = function (sel) {
        var container = $(sel);
        if (container.length) {
            mixpanel.track('Viewed register');
            container.on('click', 'button.go-network', function () {
                mixpanel.track('Registered!');
            });
        }
    };

}(jQuery));
