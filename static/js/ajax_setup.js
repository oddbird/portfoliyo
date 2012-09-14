(function ($) {

    'use strict';

    $(document).ajaxError(function (event, request, settings, error) {
        if (request && request.responseText && $.parseJSON(request.responseText).error) {
            ich.message({ message: $.parseJSON(request.responseText).error, tags: "error" }).appendTo('#messages');
            $('#messages').messages();
        } else {
            ich.message({ message: "Bummer! Something bad happened, but we're not sure what. Try reloading the page?", tags: "error" }).appendTo('#messages');
            $('#messages').messages();
        }
    });

}(jQuery));
