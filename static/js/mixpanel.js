(function ($) {

    $(function () {
        existence ('article.landing', 'viewed landing');
        existence ('article.register', 'viewed register');
        existence ('article.awaiting-activation', 'registered');
        existence ('.login .activated.success', 'activated');

        ajaxclick ('.action-post', 'posted');
        ajaxclick ('.group-posts', 'mass texted');

        serverEvents ('.meta', 'user-events');

        // this should come last, to make sure that on registration we call
        // mixpanel.alias() with their user id (so mixpanel knows that user ID
        // is the same user as the previously-anonymous one it saw on the
        // landing and registration pages) before we try to identify the user
        // using their user-id.
        identifyUser ('.meta .settingslink');
    });


    var serverEvents = function (sel, dataAttr) {
        // Look for and record events the server recorded in a JSON structure
        // in the given data attribute of the element named by the given
        // selector. Expect a list of events, where each element in the list is
        // itself a length-two list, where the first element is the event name
        // and the second a properties object.
        var events = $(sel).data(dataAttr);
        if (events) {
            $.each(events, function(index, value) {
                mixpanel.track(value[0], value[1]);
                // if the user just registered, note
                if (value[0] == 'registered') {
                    mixpanel.alias(value[1].user_id);
                }
            });
        }
    };


    var existence = function (sel, eventName) {
        // Fire given event name if the given selector exists on the page.
        if ($(sel).length) {
            mixpanel.track(eventName);
        }
    };

    var ajaxclick = function (sel, eventName) {
        // This function is only safe to use on clicks that don't reload the
        // page (otherwise the page will reload before this has time to
        // actually send the event off to mixpanel).  For normal links, use
        // mixpanel.track_click (or better, do it on the target page or on the
        // server).
        $('body').on('click', sel, function () {
            mixpanel.track(eventName);
        });
    };

    var identifyUser = function (sel) {
        // Identify the current user to MixPanel, based on data attributes
        // found on the element named by the given selector.
        var elem = $(sel);
        if (elem.length) {
            var userId = elem.data('user-id');
            var userEmail = elem.data('user-email');
            if (userId) {
                mixpanel.identify(userId);
                if (userEmail) {
                    mixpanel.name_tag(userEmail);
                    mixpanel.people.set({
                        $email: userEmail
                    });
                }
            }
        }
    };

}(jQuery));
