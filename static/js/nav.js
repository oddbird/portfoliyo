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
            $(this).blur();
            var url = $(this).data('group-url');
            var name = $(this).data('name');
            PYO.fetchStudents(url, name);
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
                    success: function (response) {
                        if (link.hasClass('active')) {
                            window.location.href = '/';
                        }
                        listitem.remove();
                    },
                    error: function (request, status, error) {
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
                        msg.wrap('<li />');
                    }
                });
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
        var url = nav.data('groups-url');
        var studentsUrl = nav.data('students-url');
        var replaceNav = function (data) {
            nav.loadingOverlay('remove');
            if (data) {
                data.all_students_uri = studentsUrl;
                data.staff = nav.data('is-staff');
                var newGroups = ich.group_list(data);
                nav.trigger('before-replace').html(newGroups);
            }
        };

        if (url) {
            nav.loadingOverlay();
            $.get(url, replaceNav).error(function (request, status, error) {
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

    PYO.fetchStudents = function (group_url, group_name) {
        if (group_url && group_name) {
            var nav = $('.village-nav');
            var replaceNav = function (data) {
                nav.loadingOverlay('remove');
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

            nav.loadingOverlay();
            $.get(group_url, replaceNav).error(function (request, status, error) {
                var msg = ich.ajax_error_msg({
                    error_class: 'nav-error',
                    message: 'Unable to load students.'
                });
                msg.find('.try-again').click(function (e) {
                    e.preventDefault();
                    msg.remove();
                    PYO.fetchStudents(group_url, group_name);
                });
                nav.prepend(msg);
                nav.loadingOverlay('remove');
            });
        }
    };

    PYO.listenForPosts = function () {
        if (PYO.pusherKey) {
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
        }
    };

    PYO.unsubscribeFromPosts = function () {
        if (PYO.pusherKey) {
            var students = $('.village-nav .student a.ajax-link');

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
