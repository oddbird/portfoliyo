(function ($) {

    'use strict';

    $(document).ajaxSend(
        function (event, xhr, settings) {
            function getToken() {
                return document.getElementsByName('csrfmiddlewaretoken')[0].value;
            }
            function safeMethod(method) {
                return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            }

            if (!safeMethod(settings.type) && !settings.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getToken());
            }
        }
    );

}(jQuery));
