var PYO = (function (PYO, $) {

    'use strict';

    var all_students_group_obj;

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
                name: trigger.data('group-name'),
                url: trigger.attr('href'),
                students_url: trigger.data('group-students-url'),
                id: trigger.data('group-id'),
                edit_url: trigger.data('group-edit-url'),
                resource_url: trigger.data('group-resource-url')
            };
            PYO.fetchStudents(group_obj);
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
        var url = link.data('group-resource-url');
        var name = link.data('group-name');
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
                            PYO.fetchStudents(all_students_group_obj);
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
        listitem.removeAttr('data-original');
    };

    PYO.fetchGroups = function () {
        var nav = $('.village-nav');
        var groups_url = nav.data('groups-url');
        var replaceNav = function (data) {
            nav.loadingOverlay('remove');
            if (data) {
                data.staff = nav.data('is-staff');
                data.add_group_url = nav.data('add-group-url');
                var newGroups = ich.group_list(data);
                PYO.updateNavActiveClasses(newGroups);
                nav.trigger('before-replace').html(newGroups);
                if (!all_students_group_obj && data.objects && data.objects.length) {
                    $.each(data.objects, function () {
                        if (this.id.toString().indexOf('all') !== -1) {
                            all_students_group_obj = {
                                name: this.name,
                                url: this.group_uri,
                                students_url: this.students_uri,
                                id: this.id
                            };
                        }
                    });
                }
            } else { PYO.fetchGroupsError(); }
        };

        if (groups_url) {
            nav.loadingOverlay();
            $.get(groups_url, replaceNav).error(function () {
                PYO.fetchGroupsError();
                nav.loadingOverlay('remove');
            });
        }
    };

    PYO.fetchGroupsError = function () {
        var nav = $('.village-nav');
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
    };

    PYO.fetchStudents = function (group_obj) {
        var nav = $('.village-nav');
        var replaceNav = function (data) {
            nav.loadingOverlay('remove');
            if (data) {
                data.group_name = group_obj.name;
                data.group_id = group_obj.id;
                data.group_url = group_obj.url;
                data.group_students_url = group_obj.students_url;
                data.group_edit_url = group_obj.edit_url;
                data.group_resource_url = group_obj.resource_url;
                data.staff = nav.data('is-staff');
                data.add_student_url = nav.data('add-student-url');
                var students = ich.student_list(data);
                PYO.updateNavActiveClasses(students);
                nav.trigger('before-replace').html(students);
                PYO.listenForPosts('.village');
            } else { fetchStudentsError(); }
        };
        var fetchStudentsError = function () {
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
        };
        var getActiveGroupInfo = function (data) {
            if (data && data.objects && data.objects.length) {
                $.each(data.objects, function () {
                    if (this.id === PYO.activeGroupId) {
                        new_group_obj = {
                            name: this.name,
                            url: this.group_uri,
                            students_url: this.students_uri,
                            id: this.id,
                            edit_url: this.edit_uri,
                            resource_url: this.resource_uri
                        };
                    }
                    if (this.id.toString().indexOf('all') !== -1) {
                        all_students_group_obj = {
                            name: this.name,
                            url: this.group_uri,
                            students_url: this.students_uri,
                            id: this.id
                        };
                    }
                });
                if (!PYO.activeGroupId) { new_group_obj = all_students_group_obj; }
                if (new_group_obj) { PYO.fetchStudents(new_group_obj); } else { fetchStudentsError(); }
            }
        };

        if (group_obj) {
            if (group_obj.name && group_obj.id && group_obj.url && group_obj.students_url) {
                nav.loadingOverlay();
                $.get(group_obj.students_url, replaceNav).error(fetchStudentsError);
            } else { fetchStudentsError(); }
        } else {
            var groups_url = nav.data('groups-url');
            if (groups_url) {
                var new_group_obj;
                $.get(groups_url, getActiveGroupInfo).error(PYO.fetchGroupsError);
            } else { fetchStudentsError(); }
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

    PYO.updateNavActiveClasses = function (container) {
        var context = container ? container : $('.village-nav');
        var links = context.find('.ajax-link').not('.action-edit').removeClass('active');

        if (links.length) {
            var url = window.location.pathname;
            links.filter('[href="' + url + '"]').addClass('active');
            links.filter(function () {
                var id;
                if ($(this).hasClass('group-link')) {
                    id = $(this).data('group-id');
                    return id === PYO.activeGroupId;
                } else {
                    id = $(this).data('id');
                    return id === PYO.activeStudentId;
                }
            }).addClass('active');
        }
    };

    PYO.initializeNav = function () {
        if ($('.village-nav').length) {
            PYO.navHandlers();
            if (PYO.activeStudentId || PYO.activeGroupId || $('#add-student-form').length) {
                PYO.fetchStudents();
            } else {
                PYO.fetchGroups();
            }
        }
    };

    return PYO;

}(PYO || {}, jQuery));
