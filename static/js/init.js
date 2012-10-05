var PYO = (function (PYO, $) {

    'use strict';

    $(function () {
        // plugins
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('#messages').messages({handleAjax: true});
        $('.details:not(html)').html5accordion();
        $('.email').defuscate();

        // landing.js
        PYO.ajaxifyForm('.village-landing .membership form', '.village-landing .membership');

        // base.js
        PYO.activeUserId = $('.village').data('user-id');
        PYO.initializePusher();
        PYO.updatePageHeight('.village');
        PYO.ajaxifyVillages('.village');
        PYO.detectFlashSupport('.village');
        PYO.initializePage();

        // nav.js
        PYO.initializeNav();
    });

    return PYO;

}(PYO || {}, jQuery));
