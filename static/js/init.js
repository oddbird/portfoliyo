var PYO = (function (PYO, $) {

    'use strict';

    $(function () {
        // plugins
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('#messages').messages({handleAjax: true});

        // local.js
        PYO.ajaxifyForm('.signup .container form');
        PYO.pageHeight('.village');
        PYO.pageHeight('div[role="main"]');
        PYO.villageScroll('.village-feed');
        PYO.windowResize();
    });

    return PYO;

}(PYO || {}, jQuery));
