var PYO = (function (PYO, $) {

    'use strict';

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

    PYO.studentActionHandlers = function (container) {
        if ($(container).length) {
            var nav = $(container);
            var cancelEdits = function () {
                nav.find('.select-student.editing').each(function () {
                    var listitem = $(this).closest('.student');
                    PYO.cancelEditStudent(listitem);
                });
            };

            nav.on('click', '.edit-student', function (e) {
                e.preventDefault();
                cancelEdits();
                PYO.editStudent($(this));
            });

            nav.on('click', '.save-student', function (e) {
                e.preventDefault();
                PYO.saveStudent($(this));
            });

            nav.on('click', '.remove-student', function (e) {
                e.preventDefault();
                var listitem = $(this).closest('.student');
                PYO.cancelEditStudent(listitem);
                PYO.removeStudent($(this));
            });

            nav.on('click', '.undo-remove-student', function (e) {
                e.preventDefault();
                PYO.undoRemoveStudent($(this));
            });

            $('.village').on('pjax-load', function (e) {
                cancelEdits();
            });
        }
    };

    PYO.editStudent = function (trigger) {
        var edit = trigger;
        var listitem = edit.closest('.student');
        var original = listitem.find('.select-student');
        var name = listitem.find('.student-name').text();
        var save = listitem.find('.save-student');
        var editing = ich.edit_student({name: name});

        listitem.data('original-link', original);
        original.replaceWith(editing);
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
                PYO.cancelEditStudent(listitem);
            }
        });
    };

    PYO.saveStudent = function (trigger) {
        var save = trigger;
        var listitem = save.closest('.student');
        var url = listitem.data('url');
        var edit = listitem.find('.edit-student');
        var editing = listitem.find('.select-student.editing');
        var original = listitem.data('original-link');
        var name = original.find('.student-name');
        var oldName = editing.data('original-name');
        var newName = $.trim(editing.text());

        if (url && newName && newName !== oldName) {
            listitem.loadingOverlay();
            $.post(url, {name: newName}, function (response) {
                listitem.loadingOverlay('remove');
                if (response && response.name && response.success) {
                    name.text(response.name);
                    editing.replaceWith(original);
                    save.hide();
                    edit.show();
                }
            });
        } else {
            PYO.cancelEditStudent(listitem);
        }
    };

    PYO.cancelEditStudent = function (listitem) {
        var original = listitem.data('original-link');
        var edit = listitem.find('.edit-student');
        var save = listitem.find('.save-student');
        var editing = listitem.find('.select-student.editing');
        editing.replaceWith(original);
        save.hide();
        edit.show();
    };

    PYO.removeStudent = function (trigger) {
        var remove = trigger;
        var listitem = remove.closest('.student');
        var link = listitem.find('.select-student');
        var url = listitem.data('url');
        var name = listitem.find('.student-name').text();
        var removed = ich.remove_student({name: name});

        listitem.data('original', listitem.html());
        listitem.html(removed);
        listitem.find('.select-student.removed').fadeOut(5000, function () {
            if (url) {
                $.post(url, {remove: true}, function (response) {
                    if (response && response.success) {
                        if (link.hasClass('active')) {
                            window.location.href = '/';
                        }
                        listitem.remove();
                    }
                });
            }
        });
    };

    PYO.undoRemoveStudent = function (trigger) {
        var undo = trigger;
        var listitem = undo.closest('.student');
        var original = listitem.data('original');
        listitem.find('.select-student.removed').stop();
        listitem.html(original);
    };

    return PYO;

}(PYO || {}, jQuery));
