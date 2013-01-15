var PYO = (function (PYO, $) {

    'use strict';

    $(function () {
        // plugins
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('#messages').messages({
            handleAjax: true,
            transientFadeSpeed: 2000
        });
        $('.details:not(html)').html5accordion();
        $('.email').defuscate();

        // base.js
        PYO.activeUserId = $('.village').data('user-id');
        PYO.ieInputBootstrapHandler();
        PYO.announcements('#messages .announce');
        PYO.initializePusher();
        PYO.updatePageHeight('.village');
        PYO.ajaxifyVillages('.village');
        PYO.detectFlashSupport('.village');
        PYO.initializePage();

        // nav.js
        PYO.initializeNav();

        // user.js
        PYO.addSchool('#register-form');

        // chat.js
        PYO.initializeSmsDirectLinks();
    });

    return PYO;

}(PYO || {}, jQuery));
