var PYO = (function (PYO, $) {

    'use strict';

    PYO.initializeRegisterForm = function (container) {
        if ($(container).length) {
            var form = $(container);

            // Toggle profile type functionality
            var toggleParentLink = form.find('.parent-tab');
            var toggleTeacherLink = form.find('.teacher-tab');
            var nameFieldLabel = form.find('.name-field label');
            var roleField = form.find('.role-field');

            toggleParentLink.click(function (e) {
                e.preventDefault();
                toggleParentLink.addClass('active');
                toggleTeacherLink.removeClass('active');
                nameFieldLabel.html('My name is...');
                roleField.fadeOut('fast');
            });

            toggleTeacherLink.click(function (e) {
                e.preventDefault();
                toggleTeacherLink.addClass('active');
                toggleParentLink.removeClass('active');
                nameFieldLabel.html('Students call me...');
                roleField.fadeIn('fast');
            });

            // Add School functionality
            var addSchoolLink = form.find('.add-school-link');
            var selectSchoolLink = form.find('.select-school-link');
            var selectSchool = form.find('.school-field');
            var addSchool = form.find('.add-school');
            var hiddenInput = addSchool.find('#id_addschool');
            var schoolNetworkToggle = form.find('#school-network-toggle');

            // Initialize school open
            schoolNetworkToggle.click();

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
