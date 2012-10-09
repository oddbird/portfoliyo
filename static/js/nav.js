var PYO = (function (PYO, $) {

    'use strict';

    PYO.navHandlers = function () {
        var nav = $('.village-nav');

        nav.on('click', '.action-remove', function (e) {
            e.preventDefault();
            $(this).blur();
            PYO.removeListitem($(this));
        });

        nav.on('click', '.undo-action-remove', function (e) {
            e.preventDefault();
            $(this).blur();
            PYO.undoRemoveListitem($(this));
        });

        nav.on('click', '.group-link', function (e) {
            e.preventDefault();
            var trigger = $(this).blur();
            var api_url = trigger.data('group-api-url');
            var url = trigger.attr('href');
            var name = trigger.data('name');
            var id = trigger.data('group-id');
            var edit_group_url = trigger.data('edit-url');
            var group_resource_url = trigger.closest('.listitem').data('api-url');
            PYO.fetchStudents(url, api_url, name, id, edit_group_url, group_resource_url);
        });

        nav.on('click', '.groups.action-back', function (e) {
            e.preventDefault();
            $(this).blur();
            PYO.fetchGroups();
        });

        nav.on('before-replace', function () {
            PYO.unsubscribeFromPosts();
        });
    };

    PYO.removeListitem = function (trigger) {
        var remove = trigger;
        var listitem = remove.closest('.listitem');
        var link = listitem.find('.listitem-select');
        var url = listitem.data('api-url');
        var name = link.data('name');
        var removed = ich.remove_listitem({name: name});
        var removeItem = function () {
            listitem.hide();
            if (url) {
                $.ajax(url, {
                    type: 'DELETE',
                    success: function () {
                        if (link.hasClass('active')) {
                            window.location.href = '/';
                        } else if (listitem.hasClass('grouptitle')) {
                            var studentsApiUrl = $('.village-nav').data('all-students-api-url');
                            var studentsUrl = $('.village-nav').data('all-students-url');
                            PYO.fetchStudents(studentsUrl, studentsApiUrl, 'All Students', '0');
                        }
                        listitem.remove();
                    },
                    error: function () {
                        ajaxError();
                    }
                });
            } else {
                ajaxError();
            }
        };
        var ajaxError = function () {
            listitem.find('.undo-action-remove').click();
            var msg = ich.ajax_error_msg({
                error_class: 'remove-error',
                message: 'Unable to remove this item.'
            });
            msg.find('.try-again').click(function (e) {
                e.preventDefault();
                msg.remove();
                removeItem();
            });
            listitem.before(msg).show();
            if (msg.parent().is('ul, ol')) {
                msg.wrap('<li />');
            }
        };

        listitem.data('original', listitem.html());
        listitem.html(removed);
        listitem.find('.listitem-select.removed').fadeOut(5000, function () {
            removeItem();
        });
    };

    PYO.undoRemoveListitem = function (trigger) {
        var undo = trigger;
        var listitem = undo.closest('.listitem');
        var original = listitem.data('original');
        listitem.find('.listitem-select.removed').stop();
        listitem.html(original);
    };

    PYO.fetchGroups = function () {
        var nav = $('.village-nav');
        var groups_url = nav.data('groups-url');
        var replaceNav = function (data) {
            nav.loadingOverlay('remove');
            if (data) {
                data.all_students_api_url = nav.data('all-students-api-url');
                data.all_students_url = nav.data('all-students-url');
                data.staff = nav.data('is-staff');
                data.add_group_url = nav.data('add-group-url');
                var newGroups = ich.group_list(data);
                PYO.updateNavActiveClasses(newGroups);
                nav.trigger('before-replace').html(newGroups);
            }
        };

        if (groups_url) {
            nav.loadingOverlay();
            $.get(groups_url, replaceNav).error(function (request, status, error) {
                var msg = ich.ajax_error_msg({
                    error_class: 'nav-error',
                    message: 'Unable to load groups.'
                });
                msg.find('.try-again').click(function (e) {
                    e.preventDefault();
                    msg.remove();
                    PYO.fetchGroups();
                });
                nav.prepend(msg);
                nav.loadingOverlay('remove');
            });
        }
    };

    PYO.fetchStudents = function (group_url, group_api_url, group_name, group_id, edit_group_url, group_resource_url) {
        if (group_url && group_api_url && group_name) {
            var nav = $('.village-nav');
            var replaceNav = function (data) {
                nav.loadingOverlay('remove');
                if (data) {
                    data.group_name = group_name;
                    data.group_url = group_url;
                    data.group_api_url = group_api_url;
                    data.group_id = group_id;
                    data.edit_group_url = edit_group_url;
                    data.group_resource_url = group_resource_url;
                    data.staff = nav.data('is-staff');
                    data.add_student_url = nav.data('add-student-url');
                    var students = ich.student_list(data);
                    PYO.updateNavActiveClasses(students);
                    nav.trigger('before-replace').html(students);
                    PYO.listenForPosts('.village');
                }
            };

            nav.loadingOverlay();
            $.get(group_api_url, replaceNav).error(function (request, status, error) {
                var msg = ich.ajax_error_msg({
                    error_class: 'nav-error',
                    message: 'Unable to load students.'
                });
                msg.find('.try-again').click(function (e) {
                    e.preventDefault();
                    msg.remove();
                    PYO.fetchStudents(group_url, group_api_url, group_name, group_id, edit_group_url, group_resource_url);
                });
                nav.prepend(msg);
                nav.loadingOverlay('remove');
            });
        }
    };

    PYO.listenForPosts = function () {
        if (PYO.pusherKey) {
            var students = $('.village-nav .student a.ajax-link.listitem-select');

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
        }
    };

    PYO.unsubscribeFromPosts = function () {
        if (PYO.pusherKey) {
            var students = $('.village-nav .student a.ajax-link.listitem-select');

            students.each(function () {
                var el = $(this);
                var id = el.data('id');
                PYO.pusher.unsubscribe('student_' + id);
            });
        }
    };

    PYO.initializeNav = function () {
        if ($('.village-nav').length) {
            PYO.navHandlers();
            if (PYO.activeStudentId || $('#add-student-form').length || PYO.activeGroupId === 0) {
                var studentsApiUrl = $('.village-nav').data('all-students-api-url');
                var studentsUrl = $('.village-nav').data('all-students-url');
                PYO.fetchStudents(studentsUrl, studentsApiUrl, 'All Students', '0');
            } else if (PYO.activeGroupId) {
                var group = $('.village-content');
                var group_url = group.data('group-url');
                var group_api_url = group.data('group-api-url');
                var group_name = group.data('group-name');
                var group_id = group.data('group-id');
                var group_edit_url = group.data('group-edit-url');
                var group_resource_url = group.data('group-resource-url');
                PYO.fetchStudents(group_url, group_api_url, group_name, group_id, group_edit_url, group_resource_url);
            } else {
                PYO.fetchGroups();
            }
        }
    };

    return PYO;

}(PYO || {}, jQuery));
