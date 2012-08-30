var PYO = (function (PYO, $) {

    'use strict';

    // Store keycode variables for easier readability
    PYO.keycodes = {
        SPACE: 32,
        ENTER: 13,
        TAB: 9,
        ESC: 27,
        BACKSPACE: 8,
        SHIFT: 16,
        CTRL: 17,
        ALT: 18,
        CAPS: 20,
        LEFT: 37,
        UP: 38,
        RIGHT: 39,
        DOWN: 40
    };

    PYO.ajaxifyForm = function (form, loading) {
        var thisForm = $(form);
        var loadingContainer = loading ? $(loading) : thisForm;

        thisForm.ajaxForm({
            beforeSubmit: function (arr, form, options) {
                loadingContainer.loadingOverlay();
            },
            success: function (response) {
                var newForm = $(response.html);
                loadingContainer.loadingOverlay('remove');
                if (response.html) {
                    thisForm.replaceWith(newForm);
                    PYO.ajaxifyForm(newForm, loading);
                    newForm.find('input[placeholder], textarea[placeholder]').placeholder();
                }
            }
        });
    };

    return PYO;

}(PYO || {}, jQuery));
