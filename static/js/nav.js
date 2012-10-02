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
                nav.find('.listitem-select.editing').each(function () {
                    var listitem = $(this).closest('.listitem');
                    PYO.cancelEditStudent(listitem);
                });
            };

            nav.on('click', '.student .action-edit', function (e) {
                e.preventDefault();
                cancelEdits();
                PYO.editStudent($(this));
            });

            nav.on('click', '.student .action-save', function (e) {
                e.preventDefault();
                PYO.saveStudent($(this));
            });

            nav.on('click', '.student .action-remove', function (e) {
                e.preventDefault();
                var listitem = $(this).closest('.listitem');
                PYO.cancelEditStudent(listitem);
                PYO.removeStudent($(this));
            });

            nav.on('click', '.student .undo-action-remove', function (e) {
                e.preventDefault();
                PYO.undoRemoveStudent($(this));
            });

            $('.village').on('pjax-load', function () {
                cancelEdits();
            });
        }
    };

    PYO.editStudent = function (trigger) {
        var edit = trigger;
        var listitem = edit.closest('.listitem');
        var original = listitem.find('.listitem-select');
        var name = listitem.find('.listitem-name').text();
        var save = listitem.find('.action-save');
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
        var listitem = save.closest('.listitem');
        var url = listitem.data('url');
        var edit = listitem.find('.action-edit');
        var editing = listitem.find('.listitem-select.editing');
        var original = listitem.data('original-link');
        var name = original.find('.listitem-name');
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
        var edit = listitem.find('.action-edit');
        var save = listitem.find('.action-save');
        var editing = listitem.find('.listitem-select.editing');
        editing.replaceWith(original);
        save.hide();
        edit.show();
    };

    PYO.removeStudent = function (trigger) {
        var remove = trigger;
        var listitem = remove.closest('.listitem');
        var link = listitem.find('.listitem-select');
        var url = listitem.data('url');
        var name = listitem.find('.listitem-name').text();
        var removed = ich.remove_student({name: name});

        listitem.data('original', listitem.html());
        listitem.html(removed);
        listitem.find('.listitem-select.removed').fadeOut(5000, function () {
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
        var listitem = undo.closest('.listitem');
        var original = listitem.data('original');
        listitem.find('.listitem-select.removed').stop();
        listitem.html(original);
    };

    PYO.navHandlers = function () {
        var nav = $('.village-nav');
        nav.on('click', '.group-link', function (e) {
            e.preventDefault();
            $(this).blur();
            var url = $(this).attr('href');
            var name = $(this).data('group-name');
            PYO.fetchStudents(url, name);
        });

        nav.on('click', '.groups.action-back', function (e) {
            e.preventDefault();
            PYO.fetchGroups();
        });

        nav.on('before-replace', function (e) {
            PYO.unsubscribeFromPosts();
        });
    };

    PYO.fetchGroups = function () {
        var nav = $('.village-nav');
        var url = nav.data('groups-url');
        var studentsUrl = nav.data('students-url');
        var replaceNav = function (data) {
            if (data) {
                var allStudents = {
                    name: 'All Students',
                    members_uri: studentsUrl
                };
                data.staff = nav.data('is-staff');
                data.objects.unshift(allStudents);
                var newGroups = ich.group_list(data);
                nav.trigger('before-replace').html(newGroups);
            }
        };

        if (url) {
            $.get(url, replaceNav);
        }
    };

    PYO.fetchStudents = function (group_url, group_name) {
        if (group_url && group_name) {
            var nav = $('.village-nav');
            var replaceNav = function (data) {
                if (data) {
                    data.group_name = group_name;
                    data.group_uri = group_url;
                    data.staff = nav.data('is-staff');
                    var students = ich.student_list(data);
                    var url = window.location.pathname;
                    students.find('a.ajax-link[href="' + url + '"]').addClass('active');
                    nav.trigger('before-replace').html(students);
                    PYO.listenForPosts('.village');
                }
            };

            $.get(group_url, replaceNav);
        }
    };

    PYO.listenForPosts = function () {
        var students = $('.village-nav .student a.ajax-link');

        students.each(function () {
            var el = $(this);
            var id = el.data('id');
            var unread = el.find('.unread');
            var channel = PYO.pusher.subscribe('student_' + id);

            channel.bind('message_posted', function (data) {
                if (id === PYO.activeStudentId && PYO.scrolledToBottom()) {
                    if (!PYO.replacePost(data)) {
                        PYO.addPost(data);
                        PYO.scrollToBottom();
                    }
                } else {
                    var count = parseInt(unread.text(), 10);
                    unread.removeClass('zero').text(++count);
                }
            });
        });
    };

    PYO.unsubscribeFromPosts = function () {
        var students = $('.village-nav .student a.ajax-link');

        students.each(function () {
            var el = $(this);
            var id = el.data('id');
            PYO.pusher.unsubscribe('student_' + id);
        });
    };

    PYO.initializeNav = function () {
        if ($('.village-nav').length) {
            PYO.navHandlers();
            if ($('.village-feed').length || $('#add-student-form').length) {
                var studentsUrl = $('.village-nav').data('students-url');
                PYO.fetchStudents(studentsUrl, 'All Students');
            } else {
                PYO.fetchGroups();
            }
        }
    };

    return PYO;

}(PYO || {}, jQuery));
