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

    PYO.villageScroll = function (container, animate) {
        var context = $(container);
        var height = context.get(0).scrollHeight;
        if (animate) {
            context.animate({ scrollTop: height }, 'fast');
        } else {
            context.scrollTop(height);
        }
    };

    PYO.villageHeight = function (container) {
        var headerHeight = $('div[role="banner"]').outerHeight();
        var footerHeight = $('footer').outerHeight();
        var page = $(container);
        var pageHeight;
        var updateHeight = function (animate) {
                pageHeight = $(window).height() - headerHeight - footerHeight;
                if (animate) {
                    page.animate({ height: pageHeight.toString() + 'px' }, 'fast');
                } else {
                    page.css('height', pageHeight.toString() + 'px');
                }
                PYO.villageScroll('.village-feed', animate);
            };
        updateHeight();
        $(window).resize(function () {
            $.doTimeout('resize', 250, function () {
                updateHeight(true);
            });
        });
    };

    return PYO;

}(PYO || {}, jQuery));
