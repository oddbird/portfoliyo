var PYO = (function (PYO, $) {

    'use strict';

    $(function () {
        // plugins
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('#messages').messages({
            handleAjax: true,
            closeCallback: function (el) {
                el.addClass('closed');
                $.doTimeout(800, function () { el.remove(); });
                // When an undo-msg is closed, remove the item via Ajax.
                if (el.hasClass('undo-msg')) {
                    PYO.executeActionInQueue(el.data('type'), el.data('id'));
                }
            },
            transientDelay: 15000,
            transientCallback: function (el) {
                el.addClass('closed-timeout');
                $.doTimeout(800, function () { el.remove(); });
                // When an undo-msg times out, remove the item via Ajax.
                if (el.hasClass('undo-msg')) {
                    PYO.executeActionInQueue(el.data('type'), el.data('id'));
                }
            }
        });
        $('.details:not(html)').not('.post .details').html5accordion();
        $('.email').defuscate();

        // base.js
        PYO.activeUserId = $('.village').data('user-id');
        PYO.announcements('#messages .announce');
        PYO.updatePageHeight();
        PYO.ajaxifyVillages('.village');
        PYO.detectFlashSupport('.village');
        PYO.watchForItemRemoval();
        PYO.initializePage();

        // nav.js
        PYO.initializeNav();

        // pusher.js
        PYO.initializePusher();

        // user.js
        PYO.addSchool('#register-form');

        // chat.js
        PYO.initializeSmsDirectLinks();
    });

    return PYO;

}(PYO || {}, jQuery));
