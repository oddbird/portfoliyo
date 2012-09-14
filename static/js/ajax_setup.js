(function ($) {

    'use strict';

    $(document).ajaxError(function (event, request, settings, error) {
        var json;
        try {
            json = $.parseJSON(request.responseText);
        } catch (e) {
            json = false;
        }
        if (request && request.responseText && json && json.error) {
            ich.message({ message: json.error, tags: "error" }).appendTo('#messages');
            $('#messages').messages();
        } else {
            ich.message({ message: "Bummer! Something bad happened, but we're not sure what. Try reloading the page?", tags: "error" }).appendTo('#messages');
            $('#messages').messages();
        }
    });

}(jQuery));
