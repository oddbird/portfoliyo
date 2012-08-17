var PYO = (function (PYO, $) {

    'use strict';

    $(function () {
        // plugins
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('#messages').messages({handleAjax: true});

        // local.js
        PYO.ajaxifyForm('.signup .container form');
        PYO.updatePageHeight('div[role="main"]');
        PYO.updateVillageScroll('.village-feed');
    });

    return PYO;

}(PYO || {}, jQuery));
