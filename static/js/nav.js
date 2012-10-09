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
            var group_obj = {
                name: trigger.data('name'),
                url: trigger.attr('href'),
                students_url: trigger.data('group-api-url'),
                id: trigger.data('group-id'),
                edit_url: trigger.data('edit-url'),
                resource_url: trigger.closest('.listitem').data('api-url')
            };
            PYO.fetchStudents(group_obj);
        });

        nav.on('click', '.groups.action-back', function (e) {
            e.preventDefault();
            $(this).blur();
            PYO.fetchGroups();
        });

        nav.on('before-replace', function () {
            var students = nav.find('.student');
            PYO.unsubscribeFromPosts(students);
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
                            var group_obj = {
                                name: 'All Students',
                                url: $('.village-nav').data('all-students-url'),
                                students_url: $('.village-nav').data('all-students-api-url'),
                                id: '0'
                            };
                            PYO.fetchStudents(group_obj);
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

    PYO.fetchStudents = function (group_obj) {
        if (group_obj && group_obj.url && group_obj.students_url && group_obj.name) {
            var nav = $('.village-nav');
            var replaceNav = function (data) {
                nav.loadingOverlay('remove');
                if (data) {
                    data.group_name = group_obj.name;
                    data.group_url = group_obj.url;
                    data.group_api_url = group_obj.students_url;
                    data.group_id = group_obj.id;
                    data.edit_group_url = group_obj.edit_url;
                    data.group_resource_url = group_obj.resource_url;
                    data.staff = nav.data('is-staff');
                    data.add_student_url = nav.data('add-student-url');
                    var students = ich.student_list(data);
                    PYO.updateNavActiveClasses(students);
                    nav.trigger('before-replace').html(students);
                    PYO.listenForPosts(students.find('.student'));
                }
            };

            nav.loadingOverlay();
            $.get(group_obj.students_url, replaceNav).error(function (request, status, error) {
                var msg = ich.ajax_error_msg({
                    error_class: 'nav-error',
                    message: 'Unable to load students.'
                });
                msg.find('.try-again').click(function (e) {
                    e.preventDefault();
                    msg.remove();
                    PYO.fetchStudents(group_obj);
                });
                nav.prepend(msg);
                nav.loadingOverlay('remove');
            });
        }
    };

    PYO.listenForPosts = function (students) {
        if (PYO.pusherKey && students) {
            students.find('.ajax-link.listitem-select').each(function () {
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

    PYO.unsubscribeFromPosts = function (students) {
        if (PYO.pusherKey && students) {
            students.find('.ajax-link.listitem-select').each(function () {
                var el = $(this);
                var id = el.data('id');
                PYO.pusher.unsubscribe('student_' + id);
            });
        }
    };

    PYO.listenForStudentChanges = function () {
        if (PYO.pusherKey && PYO.activeUserId) {
            var nav = $('.village-nav');
            var channel = PYO.pusher.subscribe('students_of_' + PYO.activeUserId);

            channel.bind('student_added', function (data) {
                if (data && nav.find('.grouptitle .group-link[data-name="All Students"]').length) {
                    data.staff = nav.data('is-staff');
                    var student = ich.student_list_item(data);
                    var url = window.location.pathname;
                    var inserted = false;
                    student.hide().find('a.ajax-link[href="' + url + '"]').addClass('active');
                    nav.find('.student').each(function () {
                        if (!inserted && $(this).find('.listitem-select').data('name').toLowerCase() > student.find('.listitem-select').data('name').toLowerCase()) {
                            student.insertBefore($(this)).slideDown();
                            inserted = true;
                        }
                    });
                    if (!inserted) {
                        nav.find('.itemlist').append(student);
                        student.slideDown();
                    }
                    PYO.listenForPosts(student);
                }
            });

            channel.bind('student_edited', function (data) {
                if (data && data.objects && data.objects[0] && data.objects[0].id && data.objects[0].name && nav.find('.student .listitem-select[data-id="' + data.objects[0].id + '"]').length) {
                    var student = nav.find('.student .listitem-select[data-id="' + data.objects[0].id + '"]');
                    student.find('.listitem-name').text(data.objects[0].name);
                    student.data('name', data.objects[0].name);
                }
            });

            channel.bind('student_removed', function (data) {
                if (data && data.objects && data.objects[0] && data.objects[0].id && nav.find('.student .listitem-select[data-id="' + data.objects[0].id + '"]').length) {
                    var student = nav.find('.student .listitem-select[data-id="' + data.objects[0].id + '"]').closest('.student');
                    student.slideUp(function () { $(this).remove(); });
                }
            });
        }
    };

    PYO.initializeNav = function () {
        if ($('.village-nav').length) {
            var group_obj;
            PYO.navHandlers();
            PYO.listenForStudentChanges();
            if (PYO.activeStudentId || $('#add-student-form').length || PYO.activeGroupId === 0) {
                group_obj = {
                    name: 'All Students',
                    url: $('.village-nav').data('all-students-url'),
                    students_url: $('.village-nav').data('all-students-api-url'),
                    id: '0'
                };
                PYO.fetchStudents(group_obj);
            } else if (PYO.activeGroupId) {
                var group = $('.village-content');
                group_obj = {
                    name: group.data('group-name'),
                    url: group.data('group-url'),
                    students_url: group.data('group-api-url'),
                    id: group.data('group-id'),
                    edit_url: group.data('group-edit-url'),
                    resource_url: group.data('group-resource-url')
                };
                PYO.fetchStudents(group_obj);
            } else {
                PYO.fetchGroups();
            }
        }
    };

    return PYO;

}(PYO || {}, jQuery));
