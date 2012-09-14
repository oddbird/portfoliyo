(function ($) {

    'use strict';

    $(document).ajaxError(function (event, request, settings, error) {
        if (request && request.responseText && $.parseJSON(request.responseText).error) {
            ich.message({ message: $.parseJSON(request.responseText).error, tags: "error" }).appendTo('#messages');
            $('#messages').messages();
        } else {
            ich.message({ message: "An error has occurred. Try reloading your page.", tags: "error" }).appendTo('#messages');
            $('#messages').messages();
        }
    });

}(jQuery));
