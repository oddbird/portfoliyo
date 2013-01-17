var PYO = (function (PYO, $) {

    'use strict';

    var all_students_group_obj;

    PYO.navHandlers = function () {
        var nav = $('.village-nav');
        var History = window.History;

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
                    add_student_url: trigger.data('group-add-student-url'),
                    add_students_bulk_url: trigger.data('group-add-students-bulk-url')
                };
                PYO.fetchStudents(group_obj);
            });
        }

        nav.on('click', '.groups.action-back', function (e) {
            e.preventDefault();
            $(this).blur();
            PYO.fetchGroups(true);
        });
    };

    PYO.removeListitem = function (trigger) {
        var relationshipsUrl = $('.village').data('relationships-url');
        var remove = trigger;
        var listitem = remove.closest('.listitem');
        var link = listitem.find('.listitem-select');
        var url = listitem.hasClass('student') ? relationshipsUrl + '?student=' + link.data('id') : link.data('group-resource-url');
        var name = listitem.hasClass('student') ? link.data('name') : link.data('group-name');
        var removed = PYO.tpl('remove_listitem', {name: name});
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
            var msg = PYO.tpl('ajax_error_msg', {
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
        listitem.removeData('original');
    };

    PYO.fetchGroups = function (force) {
        var nav = $('.village-nav');
        var groups_url = nav.data('groups-url');
        var replaceNav = function (data) {
            nav.loadingOverlay('remove');
            if (data && data.objects && data.objects.length) {
                var add_student_url, add_students_bulk_url;
                $.each(data.objects, function () {
                    if (this.id.toString().indexOf('all') !== -1) {
                        add_student_url = this.add_student_uri;
                        add_students_bulk_url = this.add_students_bulk_uri;
                        if (!all_students_group_obj) {
                            all_students_group_obj = {
                                name: this.name,
                                url: this.group_uri,
                                students_url: this.students_uri,
                                id: this.id,
                                add_student_url: this.add_student_uri,
                                add_students_bulk_url: this.add_students_bulk_uri
                            };
                        }
                    }
                });
                if (data.objects.length === 1 && all_students_group_obj && !force) {
                    PYO.fetchStudents(all_students_group_obj);
                } else {
                    if (nav.data('is-staff') === 'True') { data.staff = true; }
                    data.add_group_url = nav.data('add-group-url');
                    data.add_student_url = add_student_url;
                    data.add_students_bulk_url = add_students_bulk_url;
                    var newGroups = PYO.tpl('group_list', data);
                    PYO.updateNavActiveClasses(newGroups);
                    nav.html(newGroups);
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
        var nav = $('.village-nav');
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
                data.group_add_student_url = group_obj.add_student_url;
                data.group_add_students_bulk_url = group_obj.add_students_bulk_url;
                if (nav.data('is-staff') === 'True') { data.staff = true; }
                if (group_obj.id.toString().indexOf('all') !== -1) { data.all_students = true; }
                var students = PYO.tpl('student_list', data);
                PYO.updateNavActiveClasses(students);
                nav.html(students);
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
                            add_student_url: this.add_student_uri,
                            add_students_bulk_url: this.add_students_bulk_uri
                        };
                    }
                    if (!all_students_group_obj && this.id.toString().indexOf('all') !== -1) {
                        all_students_group_obj = {
                            name: this.name,
                            url: this.group_uri,
                            students_url: this.students_uri,
                            id: this.id,
                            add_student_url: this.add_student_uri,
                            add_students_bulk_url: this.add_students_bulk_uri
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
        var nav = $('.village-nav');
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
                if (!inserted && $(this).find('.listitem-select').data('name').toLowerCase() > student.find('.listitem-select').data('name').toLowerCase()) {
                    student.insertBefore($(this)).slideDown(function () { $(this).removeAttr('style'); });
                    inserted = true;
                }
            });
            if (!inserted) {
                student.appendTo(nav.find('.itemlist')).slideDown(function () { $(this).removeAttr('style'); });
            }
            student.find('.details').html5accordion();
            student.find('input[placeholder], textarea[placeholder]').placeholder();
        }
    };

    PYO.removeStudentFromList = function (id) {
        var nav = $('.village-nav');
        if (nav.find('.student .listitem-select[data-id="' + id + '"]').length) {
            var student = nav.find('.student .listitem-select[data-id="' + id + '"]').closest('.student');
            student.slideUp(function () { $(this).remove(); });
            if (id === PYO.activeStudentId) { PYO.showActiveItemRemovedMsg('student', true); }
        }
    };

    PYO.showActiveItemRemovedMsg = function (item, disable_form) {
        $('#messages').messages('add', {
            tags: 'warning',
            message: 'The ' + item + ' you are viewing has been removed. Any further changes will be lost. Please <a href="/">reload your page</a>.'
        }, {escapeHTML: false});
        if (disable_form) { $('.post-add-form .form-actions .action-post').addClass('disabled').attr('disabled', 'disabled'); }
    };

    PYO.updateNavActiveClasses = function (container) {
        var context = container ? container : $('.village-nav');
        var links = context.find('.ajax-link').not('.action-edit').removeClass('active');

        if (links.length) {
            var url = window.location.pathname;
            links.filter('[href="' + url + '"]').each(function () {
                var el = $(this);
                if (el.hasClass('action-addsingle')) {
                    el.closest('.addstudent').find('.ajax-link.additem-link').addClass('active');
                } else {
                    el.addClass('active');
                }
            });
            links.filter(function () {
                var id;
                if ($(this).hasClass('group-link')) {
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
        if ($('.village-nav').length) {
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
