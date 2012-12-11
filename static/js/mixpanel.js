(function ($) {

    $(function () {
        existence ('article.landing', 'viewed landing');
        existence ('article.register', 'viewed register');
        existence ('article.awaiting-activation', 'registered');
        existence ('.login .activated.success', 'activated');

        ajaxclick ('.action-post', 'posted');
        ajaxclick ('.group-posts', 'mass texted');

        mixpanel.track_links ('a.download-pdf', 'downloaded signup pdf');
    });


    var existence = function (sel, event_name) {
        if ($(sel).length) {
            mixpanel.track(event_name);
        }
    };

    var ajaxclick = function (sel, event_name) {
        // This function is only safe to use on clicks that don't reload the page.
        // For normal links, use mixpanel.track_click instead.
        $('body').on('click', sel, function () {
            mixpanel.track(event_name);
        });
    };

}(jQuery));
