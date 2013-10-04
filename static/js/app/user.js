var PYO = (function (PYO, $) {

    'use strict';

    PYO.addSchool = function (container) {
        if ($(container).length) {
            var form = $(container);
            var addSchoolLink = form.find('.add-school-link');
            var selectSchoolLink = form.find('.select-school-link');
            var selectSchool = form.find('.school-field');
            var addSchool = form.find('.add-school');
            var hiddenInput = addSchool.find('#id_addschool');

            addSchoolLink.click(function (e) {
                e.preventDefault();
                selectSchool.fadeOut('fast', function () {
                    addSchool.find('input').attr('required', 'required').removeAttr('disabled');
                    hiddenInput.val('True');
                    addSchool.fadeIn('fast');
                    selectSchool.find('input').attr('disabled', 'disabled');
                });
            });

            selectSchoolLink.click(function (e) {
                e.preventDefault();
                addSchool.fadeOut('fast', function () {
                    selectSchool.find('input').removeAttr('disabled');
                    selectSchool.fadeIn('fast');
                    addSchool.find('input').attr('disabled', 'disabled').removeAttr('required');
                });
                hiddenInput.val('False');
            });

            addSchool.find('input').attr('disabled', 'disabled').removeAttr('required');

            if (hiddenInput.val() === 'True') {
                addSchoolLink.click();
            }
        }
    };

    return PYO;

}(PYO || {}, jQuery));
