var PORTFOLIYO = (function (PORTFOLIYO, $) {

    'use strict';

    $(function () {
        // plugins
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('#messages').messages({handleAjax: true});
    });

    return PORTFOLIYO;

}(PORTFOLIYO || {}, jQuery));
