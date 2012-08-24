var PYO = (function (PYO, $) {

    'use strict';

    $(function () {
        // plugins
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('#messages').messages({handleAjax: true});
        $('.email').defuscate();

        // local.js
        PYO.ajaxifyForm('.village-landing .membership form', '.village-landing .membership');
    });

    return PYO;

}(PYO || {}, jQuery));
