var PYO = (function (PYO, $) {

    'use strict';

    PYO.ajaxifyForm = function (form, loading) {
        var thisForm = $(form);
        var loadingContainer = loading ? $(loading) : thisForm;

        if (thisForm.length) {
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
        }
    };

    return PYO;

}(PYO || {}, jQuery));
