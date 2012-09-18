var PYO = (function (PYO, $) {

    'use strict';

    $(function () {
        // plugins
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('#messages').messages({handleAjax: true});
        $('.email').defuscate();

        // landing.js
        PYO.ajaxifyForm('.village-landing .membership form', '.village-landing .membership');

        // village.js
        PYO.pusherKey = $('.village').data('pusher-key');
        PYO.updatePageHeight('.village');
        PYO.ajaxifyVillages('.village');
        PYO.listenForPusherEvents('.village');
        PYO.initializePage();
    });

    return PYO;

}(PYO || {}, jQuery));
