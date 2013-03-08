var PYO = (function (PYO, $) {

    'use strict';

    var all_students_group_obj;
    var nav = $('.village-nav');

    PYO.navHandlers = function () {
        var History = window.History;

        if (History.enabled) {
            nav.on('click', '.group-link', function () {
                var trigger = $(this).blur();
                var group_obj = {
                    name: trigger.data('group-name'),
                    url: trigger.attr('href'),
                    students_url: trigger.data('group-students-url'),
                    id: trigger.data('group-id'),
                    edit_url: trigger.data('group-edit-url'),
                    resource_url: trigger.data('group-resource-url'),
                    add_student_url: trigger.data('group-add-student-url')
                };
                PYO.fetchStudents(group_obj);
            });
        }

        nav.on('click', '.action-showgroups', function (e) {
            e.preventDefault();
            $(this).blur();
            PYO.fetchGroups(true);
        });
    };

    PYO.fetchGroups = function (force) {
        var groups_url = nav.data('groups-url');
        var replaceNav = function (data) {
            nav.loadingOverlay('remove');
            if (data && data.objects && data.objects.length) {
                var removed = [];
                var add_student_url;
                $.each(data.objects, function (i) {
                    if (this.id.toString().indexOf('all') !== -1) {
                        add_student_url = this.add_student_uri;
                        if (!all_students_group_obj) {
                            all_students_group_obj = {
                                name: this.name,
                                url: this.group_uri,
                                students_url: this.students_uri,
                                id: this.id,
                                add_student_url: this.add_student_uri
                            };
                        }
                    }
                    if (PYO.removalQueue.group[this.id.toString()]) {
                        PYO.removalQueue.group[this.id.toString()].obj = $.extend(true, {}, this);
                        removed.push(i);
                    }
                });
                for (var i = removed.length - 1; i >= 0; i--) {
                    data.objects.splice(removed[i], 1);
                }
                if (data.objects.length === 1 && all_students_group_obj && !force) {
                    PYO.fetchStudents(all_students_group_obj);
                } else {
                    if (nav.data('is-staff') === 'True') { data.staff = true; }
                    data.add_group_url = nav.data('add-group-url');
                    data.add_student_url = add_student_url;
                    var newGroups = PYO.tpl('group_list', data);
                    PYO.updateNavActiveClasses(newGroups);
                    nav.html(newGroups);
                    PYO.updateContentHeight('.village-nav', '.itemlist');
                    newGroups.find('.details').html5accordion();
                    newGroups.find('input[placeholder], textarea[placeholder]').placeholder();
                    if (!newGroups) { PYO.fetchGroupsError(force); }
                }
            } else { PYO.fetchGroupsError(force); }
        };

        if (groups_url) {
            nav.loadingOverlay();
            $.get(groups_url, replaceNav).error(function () {
                PYO.fetchGroupsError(force);
                nav.loadingOverlay('remove');
            });
        }
    };

    PYO.fetchGroupsError = function (force) {
        var msg = PYO.tpl('ajax_error_msg', {
            error_class: 'nav-error',
            message: 'Unable to load groups.'
        });
        msg.find('.try-again').click(function (e) {
            e.preventDefault();
            msg.remove();
            PYO.fetchGroups(force);
        });
        nav.prepend(msg);
    };

    PYO.fetchStudents = function (group_obj) {
        var replaceNav = function (data) {
            nav.loadingOverlay('remove');
            if (data) {
                if (data.objects && data.objects.length) {
                    var removed = [];
                    data.removed = [];
                    $.each(data.objects, function (i, v) {
                        if (PYO.removalQueue.student[this.id.toString()]) {
                            PYO.removalQueue.student[this.id.toString()].obj = $.extend(true, {}, this);
                            removed.push(i);
                            data.removed.push(v.id);
                        }
                    });
                    for (var i = removed.length - 1; i >= 0; i--) {
                        data.objects.splice(removed[i], 1);
                    }
                }
                data.group_name = group_obj.name;
                data.group_id = group_obj.id;
                data.group_url = group_obj.url;
                data.group_students_url = group_obj.students_url;
                data.group_edit_url = group_obj.edit_url;
                data.group_resource_url = group_obj.resource_url;
                data.group_add_student_url = group_obj.add_student_url;
                if (nav.data('is-staff') === 'True') { data.staff = true; }
                if (group_obj.id.toString().indexOf('all') !== -1) { data.all_students = true; }
                var students = PYO.tpl('student_list', data);
                PYO.updateNavActiveClasses(students);
                nav.html(students);
                PYO.updateContentHeight('.village-nav', '.itemlist');
                students.find('.details').html5accordion();
                students.find('input[placeholder], textarea[placeholder]').placeholder();
            } else { fetchStudentsError(); }
        };
        var fetchStudentsError = function () {
            var msg = PYO.tpl('ajax_error_msg', {
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
                var new_group_obj;
                $.each(data.objects, function () {
                    if (this.id === PYO.activeGroupId) {
                        new_group_obj = {
                            name: this.name,
                            url: this.group_uri,
                            students_url: this.students_uri,
                            id: this.id,
                            edit_url: this.edit_uri,
                            resource_url: this.resource_uri,
                            add_student_url: this.add_student_uri
                        };
                    }
                    if (!all_students_group_obj && this.id.toString().indexOf('all') !== -1) {
                        all_students_group_obj = {
                            name: this.name,
                            url: this.group_uri,
                            students_url: this.students_uri,
                            id: this.id,
                            add_student_url: this.add_student_uri
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
                $.get(groups_url, getActiveGroupInfo).error(PYO.fetchGroupsError);
            } else { fetchStudentsError(); }
        }
    };

    PYO.addStudentToList = function (data, all_students) {
        // Check that a student with this ID is not already in the list
        if (nav.find('.student .listitem-select[data-id="' + data.id + '"]').length === 0) {
            var obj = {};
            if (nav.data('is-staff') === 'True') { obj.staff = true; }
            obj.objects = [data];
            obj.all_students = all_students;
            obj.group_id = data.group_id;
            var student = PYO.tpl('student_list_items', obj).hide();
            var inserted = false;
            nav.find('.student').each(function () {
                if (!inserted && $(this).find('.listitem-select').data('name').toString().toLowerCase() > student.find('.listitem-select').data('name').toString().toLowerCase()) {
                    student.insertBefore($(this)).slideDown(function () { $(this).removeAttr('style'); });
                    inserted = true;
                }
            });
            if (!inserted) {
                student.appendTo(nav.find('.students-list')).slideDown(function () { $(this).removeAttr('style'); });
            }
            student.find('.details').html5accordion();
            student.find('input[placeholder], textarea[placeholder]').placeholder();
        }
    };

    PYO.removeStudentFromList = function (id) {
        if (nav.find('.student .listitem-select[data-id="' + id + '"]').length) {
            var student = nav.find('.student .listitem-select[data-id="' + id + '"]').closest('.student');
            student.slideUp(function () { $(this).remove(); });
            if (id === PYO.activeStudentId) { PYO.showActiveItemRemovedMsg('student', true); }
        }
    };

    PYO.addGroupToList = function (data) {
        // Check that a group with this ID is not already in the list
        if (nav.find('.group .listitem-select[data-group-id="' + data.id + '"]').length === 0) {
            var obj = {};
            if (nav.data('is-staff') === 'True') { obj.staff = true; }
            obj.objects = [data];
            var group = PYO.tpl('group_list_items', obj).hide();
            var inserted = false;
            nav.find('.group').not(':first').each(function () {
                if (!inserted && $(this).find('.group-link').data('group-name').toString().toLowerCase() > group.find('.group-link').data('group-name').toString().toLowerCase()) {
                    group.insertBefore($(this)).slideDown(function () { $(this).removeAttr('style'); });
                    inserted = true;
                }
            });
            if (!inserted) {
                group.appendTo(nav.find('.groups-list')).slideDown(function () { $(this).removeAttr('style'); });
            }
            group.find('.details').html5accordion();
            group.find('input[placeholder], textarea[placeholder]').placeholder();
        }
    };

    PYO.removeGroupFromList = function (id) {
        var group = nav.find('.group .group-link[data-group-id="' + id + '"]');
        var grouptitle = nav.find('.navtitle .group-feed[data-group-id="' + id + '"]');
        // If viewing the groups-list
        if (group.length) {
            var group_container = group.closest('.group');
            group_container.slideUp(function () { $(this).remove(); });
            if (group.hasClass('active')) { PYO.showActiveItemRemovedMsg('group', true); }
        }
        // If viewing the removed group
        if (grouptitle.length) {
            PYO.showActiveItemRemovedMsg('group', grouptitle.hasClass('active'));
        }
    };

    PYO.showActiveItemRemovedMsg = function (item, disable_form) {
        PYO.msgs.messages('add', {
            tags: 'warning',
            message: 'The ' + item + ' you are viewing has been removed. Any further changes will be lost. Please <a href="/">reload your page</a>.'
        }, {escapeHTML: false});
        if (disable_form) { $('.post-add-form .form-actions .action-post').addClass('disabled').attr('disabled', 'disabled'); }
    };

    PYO.updateNavActiveClasses = function (container) {
        var context = container ? container : nav;
        var links = context.find('.ajax-link').removeClass('active');

        if (links.length) {
            var url = window.location.pathname;
            links.filter('[href="' + url + '"]').addClass('active');
            links.filter(function () {
                var id;
                if ($(this).hasClass('group-link') || $(this).hasClass('group-feed')) {
                    id = $(this).data('group-id');
                    if (!PYO.activeStudentId) { return id === PYO.activeGroupId; }
                } else {
                    id = $(this).data('id');
                    return id === PYO.activeStudentId;
                }
            }).addClass('active');
        }
    };

    PYO.initializeNav = function () {
        if (nav.length) {
            PYO.navHandlers();
            if (PYO.activeStudentId || PYO.activeGroupId || $('#add-student-form').length) {
                PYO.fetchStudents();
            } else {
                var force = false;
                if ($('#add-group-form').length) { force = true; }
                PYO.fetchGroups(force);
            }
        }
    };

    return PYO;

}(PYO || {}, jQuery));
