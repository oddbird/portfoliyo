var PYO = (function (PYO, $) {

    'use strict';

    $(function () {
        // plugins
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('#messages').messages({
            handleAjax: true,
            transientDelay: 15000,
            transientCallback: function (el) {
                el.addClass('removing');
                $.doTimeout(2000, function () { el.remove(); });
            }
        });
        $('.details:not(html)').not('.post .details').html5accordion();
        $('.email').defuscate();

        // base.js
        PYO.activeUserId = $('.village').data('user-id');
        PYO.announcements('#messages .announce');
        PYO.updatePageHeight('.village');
        PYO.ajaxifyVillages('.village');
        PYO.detectFlashSupport('.village');
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
