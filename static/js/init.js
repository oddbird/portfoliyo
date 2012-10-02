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
        PYO.updatePageHeight('.village');
        PYO.ajaxifyVillages('.village');
        PYO.detectFlashSupport('.village');
        PYO.initializePage();

        // nav.js
        PYO.studentActionHandlers('.village-nav');
        PYO.initializeNav();

        // chat.js
        PYO.pusherKey = $('.village').data('pusher-key');
        PYO.listenForPosts('.village');
    });

    return PYO;

}(PYO || {}, jQuery));
