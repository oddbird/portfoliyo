(function ($) {

    'use strict';


    // hook function to call when an event of the given name is tracked
    // function is called with event data as only argument
    var eventHooks = {
        'registered': function (data) {
            mixpanel.people.set({$created: new Date()});
        },
        'posted': function (data) {
            mixpanel.people.increment('posts');
            mixpanel.people.set({lastPosted: new Date()});
            mixpanel.people.increment('sentSMSes', data.smsRecipients);
            if (data.groupPost) {
                mixpanel.people.increment('groupPosts');
                mixpanel.people.set({lastGroupPosted: new Date()});
            } else {
                mixpanel.people.increment('singlePosts');
                mixpanel.people.set({lastSinglePosted: new Date()});
            }
        },
        'added group': function (data) {
            mixpanel.people.set({lastAddedGroup: new Date()});
            mixpanel.people.increment('groupsAdded');
        },
        'invited teacher': function (data) {
            mixpanel.people.set({lastInvitedTeacher: new Date()});
            mixpanel.people.increment('teachersInvited');
        }
    };


    var track = function (event, data) {
        // call any registered hook, then send event to mixpanel
        var hook = eventHooks[event];
        if (hook) {
            hook(data);
        }
        mixpanel.track(event, data);
    };


    var registerNewUser = function (sel, dataAttr) {
        // If the user just registered, tell mixpanel that we'll be identifying
        // them by user ID from now on, but they should still be considered the
        // same person who previously viewed the landing and register pages
        // anonymously. If we don't do this, then we can't track users'
        // progression from landing to register to use of the site.
        var events = $(sel).data(dataAttr);
        if (events) {
            $.each(events, function (index, value) {
                if (value[0] === 'registered' && value[1].user_id) {
                    mixpanel.alias(value[1].user_id);
                }
            });
        }
    };

    var serverEvents = function (sel, dataAttr) {
        // Look for and record events the server recorded in a JSON structure
        // in the given data attribute of the element named by the given
        // selector. Expect a list of events, where each element in the list is
        // itself a length-two list, where the first element is the event name
        // and the second a properties object.
        var events = $(sel).data(dataAttr);
        if (events) {
            $.each(events, function (index, value) {
                track(value[0], value[1]);
            });
        }
    };

    var existence = function (sel, eventName) {
        // Fire given event name if the given selector exists on the page.
        if ($(sel).length) {
            track(eventName);
        }
    };

    var identifyUser = function (sel) {
        // Identify the current user to MixPanel, based on data attributes
        // found on the element named by the given selector.
        var elem = $(sel);
        if (elem.length) {
            var userId = elem.data('user-id');
            var userEmail = elem.data('user-email');
            var userName = elem.data('user-name');
            if (userId) {
                mixpanel.identify(userId);
                if (userEmail) {
                    mixpanel.name_tag(userEmail);
                    mixpanel.people.set({
                        $email: userEmail,
                        $name: userName,
                        $last_login: new Date()
                    });
                    mixpanel.register({'email': userEmail});
                }
            }
        }
    };

    var ajaxPageViews = function () {
        var History = window.History;
        if (History.enabled) {
            $(window).on('statechange', function () {
                // by the time we get here, the URL is already changed, so
                // mixpanel gets the right URL automatically.
                mixpanel.track_pageview();
            });
        }
    };

    var postEvents = function (sel) {
        $('body').on('successful-post', sel, function (e, data) {
            data.groupPost = !data.studentId;
            track('posted', data);
        });
    };

    $(function () {
        if (typeof(mixpanel) === 'undefined') {
            return false;
        }

        // These two should come first so that all other events are tagged with
        // the appropriate user data. Registering a new user should come before
        // identifying them by user ID, so we don't lose the association with
        // the prior anonymous user
        registerNewUser('body', 'user-events');
        identifyUser('.meta .settingslink');

        existence('article.landing', 'viewed landing');
        existence('article.register', 'viewed register');
        existence('article.awaiting-activation', 'registered');
        existence('.login .activated.success', 'activated');

        serverEvents('body', 'user-events');

        postEvents('.village-feed');

        ajaxPageViews();
    });

}(jQuery));
