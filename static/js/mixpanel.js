(function ($) {

    $(function () {
        existence ('article.landing', 'Viewed landing');
        existence ('article.register', 'Viewed register');
        existence ('article.awaiting-activation', 'Registered');
        existence ('.login .activated.success', 'Activated');

        $('body').on('click', '.action-post', function () {
            mixpanel.track('Posted');
        });
        $('body').on('click', '.group-posts .action-post', function () {
            mixpanel.track('Mass texted');
        });
    });


    var existence = function (sel, event) {
        if ($(sel).length) {
            mixpanel.track(event);
        }
    };

}(jQuery));
