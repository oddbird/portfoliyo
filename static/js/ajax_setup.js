var PYO = (function (PYO, $) {

    'use strict';

    $.ajaxSetup({
        timeout: 30000,
        dataType: 'json'
    });

    $(document).ajaxError(function (event, request, settings, error) {
        if (request && request.status === 403) {
            PYO.tpl('message.html', {
                tags: 'error',
                message: "Sorry, you don't have permission to access this page. Please <a href='/login/'>log in</a> with an account that does or visit a different page.",
                no_escape: true
            }).appendTo('#messages');
            $('#messages').messages();
        }
        var json;
        try {
            json = $.parseJSON(request.responseText);
        } catch (e) {
            json = false;
        }
        if (request && request.responseText && json && json.error) {
            PYO.tpl('message.html', { message: json.error, tags: 'error' }).appendTo('#messages');
            $('#messages').messages();
        }
    });

    return PYO;

}(PYO || {}, jQuery));
