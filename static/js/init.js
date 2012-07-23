var PYO = (function (PYO, $) {

    'use strict';

    $(function () {
        // plugins
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('#messages').messages({handleAjax: true});

        // local.js
        PYO.ajaxifyForm(
            '.signup .container form',
            '#id_email',
            '.signup .container'
        );
    });

    return PYO;

}(PYO || {}, jQuery));
