var PYO = (function (PYO, $) {

    'use strict';

    PYO.editStudentName = function (container) {
        if ($(container).length) {
            var nav = $(container);
            var selectText = function (element) {
                var el = element[0];
                var range;
                if (document.body.createTextRange) {
                    range = document.body.createTextRange();
                    range.moveToElementText(el);
                    range.select();
                } else if (window.getSelection && document.createRange) {
                    var selection = window.getSelection();
                    range = document.createRange();
                    range.selectNodeContents(el);
                    selection.removeAllRanges();
                    selection.addRange(range);
                }
            };
            var cancel = function (student) {
                var link = student.data('link');
                var edit = student.find('.action-edit');
                var save = student.find('.action-save');
                var editing = student.find('.listitem-select.editing');
                editing.replaceWith(link);
                save.hide();
                edit.show();
            };

            nav.on('click', '.action-edit', function (e) {
                e.preventDefault();
                var edit = $(this);
                var student = edit.closest('.listitem');
                var link = student.find('.listitem-select');
                var name = student.find('.listitem-name').text();
                var save = student.find('.action-save');
                var editing = ich.edit_student({name: name});

                student.data('link', link);
                link.replaceWith(editing);
                editing.focus();
                selectText(editing);
                edit.hide();
                save.show();

                editing.keydown(function (e) {
                    if (e.keyCode === PYO.keycodes.ENTER) {
                        e.preventDefault();
                        $(this).blur();
                        save.click();
                    }
                    if (e.keyCode === PYO.keycodes.ESC) {
                        e.preventDefault();
                        $(this).blur();
                        cancel(student);
                    }
                });
            });

            nav.on('click', '.action-save', function (e) {
                var save = $(this);
                var student = save.closest('.listitem');
                var url = student.data('url');
                var edit = student.find('.action-edit');
                var editing = student.find('.listitem-select.editing');
                var link = student.data('link');
                var name = link.find('.listitem-name');
                var oldName = editing.data('original-name');
                var newName = $.trim(editing.text());

                if (url && newName && newName !== oldName) {
                    student.loadingOverlay();
                    $.post(url, {name: newName}, function (response) {
                        student.loadingOverlay('remove');
                        if (response && response.name && response.success) {
                            name.text(response.name);
                            editing.replaceWith(link);
                            save.hide();
                            edit.show();
                        }
                    });
                } else {
                    cancel(student);
                }
            });

            $('.village').on('pjax-load', function (e) {
                nav.find('.listitem-select.editing').each(function () {
                    var student = $(this).closest('.listitem');
                    cancel(student);
                });
            });
        }
    };

    return PYO;

}(PYO || {}, jQuery));
