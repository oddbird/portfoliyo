var PYO = (function (PYO, $) {

    'use strict';

    PYO.addSchool = function (container) {
        if ($(container).length) {
            var form = $(container);
            var addSchoolLink = form.find('.add-school-link');
            var selectSchoolLink = form.find('.select-school-link');
            var selectSchool = form.find('.school-field');
            var addSchool = form.find('.add-school');

            addSchool.find('input').attr('disabled', 'disabled').removeAttr('required');

            addSchoolLink.click(function (e) {
                e.preventDefault();
                selectSchool.fadeOut('fast', function () {
                    addSchool.find('input').attr('required', 'required').removeAttr('disabled');
                    addSchool.fadeIn('fast');
                }).find('input').attr('disabled', 'disabled');
            });

            selectSchoolLink.click(function (e) {
                e.preventDefault();
                addSchool.fadeOut('fast', function () {
                    selectSchool.find('input').removeAttr('disabled');
                    selectSchool.fadeIn('fast');
                }).find('input').attr('disabled', 'disabled').removeAttr('required');
            });
        }
    };

    return PYO;

}(PYO || {}, jQuery));
