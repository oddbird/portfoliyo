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
                }
            }
        });
    };

    PYO.updatePageHeight = function (container) {
        if ($(container).length) {
            var headerHeight = $('div[role="banner"]').outerHeight();
            var footerHeight = $('footer').outerHeight();
            var page = $(container);
            var pageHeight = $(window).height() - headerHeight - footerHeight;
            page.css('height', pageHeight.toString() + 'px');
        }
    };

    PYO.updateVillageScroll = function (container) {
        if ($(container).length) {
            var context = $(container);
            var height = context.get(0).scrollHeight;
            context.scrollTop(height);
        }
    };

    PYO.onWindowResize = function () {
        $(window).resize(function () {
            $.doTimeout('resize', 250, function () {
                PYO.updatePageHeight('.village');
                PYO.updatePageHeight('div[role="main"]');
                PYO.updateVillageScroll('.village-feed');
            });
        });
    };

    return PYO;

}(PYO || {}, jQuery));
