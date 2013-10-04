var PYO = (function (PYO, $) {

    'use strict';

    $.ajaxSetup({
        timeout: 30000,
        dataType: 'json'
    });

    $(document).ajaxError(function (event, request, settings, error) {
        if (request && request.status === 403) {
            $('#messages').messages('add', {
                tags: 'error',
                message: "Sorry, you don't have permission to access this page. Please <a href='/login/'>log in</a> with an account that does or visit a different page."
            }, {escapeHTML: false});
        }
        var json;
        try {
            json = $.parseJSON(request.responseText);
        } catch (e) {
            json = false;
        }
        if (request && request.responseText && json && json.error) {
            $('#messages').messages('add', {message: json.error, tags: 'error'});
        }
    });

    return PYO;

}(PYO || {}, jQuery));
