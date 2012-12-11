(function ($) {

    $(function () {
        existence ('article.landing', 'viewed landing');
        existence ('article.register', 'viewed register');
        existence ('article.awaiting-activation', 'registered');
        existence ('.login .activated.success', 'activated');

        ajaxclick ('.action-post', 'posted');
        ajaxclick ('.group-posts', 'mass texted');

        serverEvents ('.meta', 'user-events');
    });


    var serverEvents = function (sel, dataAttr) {
        $.each($(sel).data(dataAttr), function(index, value) {
            mixpanel.track(value[0], value[1]);
        });
    };


    var existence = function (sel, event_name) {
        if ($(sel).length) {
            mixpanel.track(event_name);
        }
    };

    var ajaxclick = function (sel, event_name) {
        // This function is only safe to use on clicks that don't reload the
        // page (otherwise the page will reload before this has time to
        // actually send the event off to mixpanel).  For normal links, use
        // mixpanel.track_click (or better, do it on the target page or on the
        // server).
        $('body').on('click', sel, function () {
            mixpanel.track(event_name);
        });
    };

}(jQuery));
