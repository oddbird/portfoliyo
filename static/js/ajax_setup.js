(function ($) {

    'use strict';

    $.ajaxSetup({
        timeout: 30000,
        dataType: 'json'
    });

    $(document).ajaxError(function (event, request, settings, error) {
        if (request && request.status === 403) {
            ich.ajax_403_msg().appendTo('#messages');
            $('#messages').messages();
        }
        var json;
        try {
            json = $.parseJSON(request.responseText);
        } catch (e) {
            json = false;
        }
        if (request && request.responseText && json && json.error) {
            ich.message({ message: json.error, tags: "error" }).appendTo('#messages');
            $('#messages').messages();
        }
    });

}(jQuery));
