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

        nav.on('before-replace', function () {
            var items = nav.find('.listitem.grouptitle, .listitem.student');
            if (items.length) { PYO.unsubscribeFromPosts(items); }
            PYO.unsubscribeFromGroupPosts();
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
                    nav.trigger('before-replace').html(newGroups);
                    newGroups.find('.details').html5accordion();
                    newGroups.find('input[placeholder], textarea[placeholder]').placeholder();
                    PYO.listenForGroupPosts();
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
                nav.trigger('before-replace').html(students);
                students.find('.details').html5accordion();
                students.find('input[placeholder], textarea[placeholder]').placeholder();
                PYO.listenForPosts(students);
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

    PYO.listenForPosts = function (items) {
        if (PYO.pusherKey && items && items.length) {
            items.find('.ajax-link.listitem-select').each(function () {
                var el = $(this);
                var unread = el.find('.unread');
                var id;
                var channel;
                var group = el.hasClass('group-link');
                if (group) {
                    id = el.data('group-id');
                    channel = PYO.pusher.subscribe('private-group_' + id);
                } else {
                    id = el.data('id');
                    channel = PYO.pusher.subscribe('private-student_' + id);
                }

                channel.bind('message_posted', function (data) {
                    var feed = $('.village-feed');
                    var contextId;
                    var count = parseInt($.trim(unread.text()), 10);
                    if (group) {
                        if (!PYO.activeStudentId) { contextId = PYO.activeGroupId; }
                    } else {
                        contextId = PYO.activeStudentId;
                    }
                    if (data && data.posts && data.posts.length) {
                        var scroll = PYO.scrolledToBottom();
                        var addNewPost = function (newPostData) {
                            newPostData.unread = true;
                            var post_obj = { posts: [newPostData] };
                            PYO.addPost(post_obj);
                            if (scroll) {
                                PYO.scrollToBottom();
                            } else if (newPostData.author_id !== PYO.activeUserId) {
                                unread.removeClass('zero').text(++count);
                            }
                        };
                        $.each(data.posts, function () {
                            if (contextId && id === contextId) {
                                if (this.author_sequence_id) {
                                    var oldPost = feed.find('.post.mine[data-author-sequence="' + this.author_sequence_id + '"]');
                                    if (oldPost.length) {
                                        if (oldPost.hasClass('local')) {
                                            PYO.replacePost(this, oldPost);
                                        } else if (oldPost.data('post-id') !== this.post_id) {
                                            addNewPost(this);
                                        }
                                    } else {
                                        addNewPost(this);
                                    }
                                } else {
                                    addNewPost(this);
                                }
                            } else if (this.author_id !== PYO.activeUserId) {
                                unread.removeClass('zero').text(++count);
                            }
                        });
                    }
                });
            });
        }
    };

    PYO.listenForGroupPosts = function () {
        if (PYO.pusherKey) {
            var nav = $('.village-nav');
            var groups = nav.find('.group .group-link.ajax-link.listitem-select');
            if (groups.length) {
                var allStudentsEl = groups.filter(function () {
                    return $(this).data('group-id').toString().indexOf('all') !== -1;
                });
                var students = $.trim(allStudentsEl.data('students')).split(' ');

                $.each(students, function () {
                    var id = this;
                    if (id) { PYO.subscribeToGroupChannel(id); }
                });
            }
        }
    };

    PYO.subscribeToGroupChannel = function (id) {
        var nav = $('.village-nav');
        var channel = PYO.pusher.subscribe('private-student_' + id);

        channel.bind('message_posted', function (data) {
            if (data && data.posts && data.posts.length) {
                $.each(data.posts, function () {
                    if (this.author_id !== PYO.activeUserId) {
                        var groups = nav.find('.group .group-link.ajax-link.listitem-select');
                        var thisId = this.student_id.toString();
                        var thisGroup = groups.filter(function () {
                            var students_arr = $.trim($(this).data('students')).split(' ');
                            return $.inArray(thisId, students_arr) !== -1;
                        });

                        thisGroup.each(function () {
                            var unread = $(this).find('.unread');
                            var count = parseInt($.trim(unread.text()), 10);
                            unread.removeClass('zero').text(++count);
                        });
                    }
                });
            }
        });
    };

    PYO.unsubscribeFromPosts = function (items) {
        if (PYO.pusherKey && items && items.length) {
            items.find('.ajax-link.listitem-select').each(function () {
                var el = $(this);
                var group = el.hasClass('group-link');
                var id;
                if (group) {
                    id = el.data('group-id');
                    PYO.pusher.unsubscribe('private-group_' + id);
                } else {
                    id = el.data('id');
                    PYO.pusher.unsubscribe('private-student_' + id);
                }
            });
        }
    };

    PYO.unsubscribeFromGroupPosts = function () {
        if (PYO.pusherKey) {
            var nav = $('.village-nav');
            var groups = nav.find('.group .group-link.ajax-link.listitem-select');
            if (groups.length) {
                var allStudentsEl = groups.filter(function () {
                    return $(this).data('group-id').toString().indexOf('all') !== -1;
                });
                var students = $.trim(allStudentsEl.data('students')).split(' ');

                $.each(students, function () {
                    var id = this;
                    if (id) { PYO.pusher.unsubscribe('private-student_' + id); }
                });
            }
        }
    };

    PYO.addStudentToList = function (data, all_students) {
        var nav = $('.village-nav');
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
        PYO.listenForPosts(student);
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
        var msg = PYO.tpl('active_item_removed_msg', {item: item});
        msg.appendTo($('#messages'));
        $('#messages').messages();
        if (disable_form) { $('.post-add-form .form-actions .action-post').addClass('disabled').attr('disabled', 'disabled'); }
    };

    PYO.listenForStudentChanges = function () {
        if (PYO.pusherKey && PYO.activeUserId) {
            var nav = $('.village-nav');
            var channel = PYO.pusher.subscribe('private-students_of_' + PYO.activeUserId);

            channel.bind('student_added', function (data) {
                if (data && data.objects && data.objects.length) {
                    $.each(data.objects, function () {
                        var id = this.id;
                        var all_groups = nav.find('.group .group-link');
                        var group_titles = nav.find('.grouptitle .group-link');
                        var all_students_group = all_groups.filter(function () {
                            return $(this).data('group-id').toString().indexOf('all') !== -1;
                        });
                        var all_students_dashboard = group_titles.filter(function () {
                            return $(this).data('group-id').toString().indexOf('all') !== -1;
                        });
                        // If viewing the all-students group
                        if (all_students_dashboard.length) {
                            PYO.addStudentToList(this, true);
                        }
                        // If viewing the groups-list (and the all-students group is visible)
                        if (all_students_group.length && id) {
                            var students = $.trim(all_students_group.data('students')) + ' ';
                            students = students + id.toString() + ' ';
                            all_students_group.data('students', students);
                            PYO.subscribeToGroupChannel(id);
                        }
                    });
                }
            });

            channel.bind('student_removed', function (data) {
                if (data && data.objects && data.objects.length) {
                    $.each(data.objects, function () {
                        if (this.id) {
                            var id = this.id;
                            var all_groups = nav.find('.group .group-link');
                            var group_titles = nav.find('.grouptitle .group-link');
                            var all_students_group = all_groups.filter(function () {
                                return $(this).data('group-id').toString().indexOf('all') !== -1;
                            });
                            var all_students_dashboard = group_titles.filter(function () {
                                return $(this).data('group-id').toString().indexOf('all') !== -1;
                            });
                            // If viewing the all-students group
                            if (all_students_dashboard.length) {
                                PYO.removeStudentFromList(id);
                            }
                            // If viewing the groups-list (and the all-students group is visible)
                            if (all_students_group.length) {
                                var students_arr = $.trim(all_students_group.data('students')).split(' ');
                                if ($.inArray(id.toString(), students_arr) !== -1) {
                                    students_arr.splice($.inArray(id.toString(), students_arr), 1);
                                    all_students_group.data('students', students_arr.join(' '));
                                }
                                PYO.pusher.unsubscribe('private-student_' + id);
                            }
                        }
                    });
                }
            });

            channel.bind('student_edited', function (data) {
                if (data && data.objects && data.objects.length) {
                    $.each(data.objects, function () {
                        if (this.id && this.name && nav.find('.student .listitem-select[data-id="' + this.id + '"]').length) {
                            var id = this.id;
                            var name = this.name;
                            var student = nav.find('.student .listitem-select[data-id="' + id + '"]');
                            if (student.data('name') !== name) {
                                student.find('.listitem-name').text(name);
                                student.data('name', name).attr('data-name', name);
                            }
                        }
                    });
                }
            });
        }
    };

    PYO.listenForGroupChanges = function () {
        if (PYO.pusherKey && PYO.activeUserId) {
            var nav = $('.village-nav');
            var channel = PYO.pusher.subscribe('private-groups_of_' + PYO.activeUserId);

            channel.bind('student_added_to_group', function (data) {
                if (data && data.objects && data.objects.length) {
                    $.each(data.objects, function () {
                        var evData = this;
                        var id = evData.id;
                        var added_to_groups_arr = evData.groups;
                        var group_titles = nav.find('.grouptitle .group-link');
                        var all_groups = nav.find('.group .group-link');
                        var group_dashboard = group_titles.filter(function () {
                            return $.inArray($(this).data('group-id'), added_to_groups_arr) !== -1;
                        });
                        var added_to_groups = all_groups.filter(function () {
                            return $.inArray($(this).data('group-id'), added_to_groups_arr) !== -1;
                        });
                        // If viewing the groups-list (and relevant groups exist)
                        if (added_to_groups.length && id) {
                            added_to_groups.each(function () {
                                var thisGroup = $(this);
                                var students = $.trim(thisGroup.data('students')) + ' ';
                                students = students + id.toString() + ' ';
                                thisGroup.data('students', students);
                            });
                        }
                        // If viewing the group that includes the new student
                        if (group_dashboard.length) {
                            group_dashboard.each(function () {
                                evData.group_id = $(this).data('group-id');
                                PYO.addStudentToList(evData);
                            });
                        }
                    });
                }
            });

            channel.bind('student_removed_from_group', function (data) {
                if (data && data.objects && data.objects.length) {
                    $.each(data.objects, function () {
                        if (this.id) {
                            var id = this.id;
                            var removed_from_groups_arr = this.groups;
                            var group_titles = nav.find('.grouptitle .group-link');
                            var all_groups = nav.find('.group .group-link');
                            var group_dashboard = group_titles.filter(function () {
                                return $.inArray($(this).data('group-id'), removed_from_groups_arr) !== -1;
                            });
                            var removed_from_groups = all_groups.filter(function () {
                                return $.inArray($(this).data('group-id'), removed_from_groups_arr) !== -1;
                            });
                            // If viewing the groups-list (and relevant groups exist)
                            if (removed_from_groups.length) {
                                removed_from_groups.each(function () {
                                    var thisGroup = $(this);
                                    var students_arr = $.trim(thisGroup.data('students')).split(' ');
                                    if ($.inArray(id.toString(), students_arr) !== -1) {
                                        students_arr.splice($.inArray(id.toString(), students_arr), 1);
                                        thisGroup.data('students', students_arr.join(' '));
                                    }
                                });
                            }
                            // If viewing the group that includes the removed student
                            if (group_dashboard.length) {
                                PYO.removeStudentFromList(id);
                            }
                        }
                    });
                }
            });

            channel.bind('group_added', function (data) {
                // If viewing the groups-list
                if (data && data.objects && data.objects.length && nav.find('.group').length) {
                    $.each(data.objects, function () {
                        var obj = {};
                        if (nav.data('is-staff') === 'True') { obj.staff = true; }
                        obj.objects = [this];
                        var group = PYO.tpl('group_list_items', obj).hide();
                        var inserted = false;
                        nav.find('.group').not(':first').each(function () {
                            if (!inserted && $(this).find('.group-link').data('group-name').toLowerCase() > group.find('.group-link').data('group-name').toLowerCase()) {
                                group.insertBefore($(this)).slideDown(function () { $(this).removeAttr('style'); });
                                inserted = true;
                            }
                        });
                        if (!inserted) {
                            group.appendTo(nav.find('.itemlist')).slideDown(function () { $(this).removeAttr('style'); });
                        }
                        group.find('.details').html5accordion();
                        group.find('input[placeholder], textarea[placeholder]').placeholder();
                    });
                }
            });

            channel.bind('group_removed', function (data) {
                if (data && data.objects && data.objects.length) {
                    $.each(data.objects, function () {
                        if (this.id) {
                            var id = this.id;
                            var group = nav.find('.group .group-link[data-group-id="' + id + '"]');
                            var grouptitle = nav.find('.grouptitle .group-link[data-group-id="' + id + '"]');
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
                        }
                    });
                }
            });

            channel.bind('group_edited', function (data) {
                if (data && data.objects && data.objects.length) {
                    $.each(data.objects, function () {
                        if (this.id && this.name) {
                            var id = this.id;
                            var name = this.name;
                            var group = nav.find('.group .group-link[data-group-id="' + id + '"]');
                            var grouptitle = nav.find('.grouptitle .group-link[data-group-id="' + id + '"]');
                            // If viewing the groups-list
                            if (group.length && group.data('group-name') !== name) {
                                group.find('.listitem-name').text(name);
                                group.data('group-name', name).attr('data-group-name', name);
                            }
                            // If viewing the edited group
                            if (grouptitle.length && grouptitle.data('group-name') !== name) {
                                grouptitle.find('.listitem-name').text(name);
                                grouptitle.data('group-name', name).attr('data-group-name', name);
                            }
                        }
                    });
                }
            });
        }
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
            PYO.listenForStudentChanges();
            PYO.listenForGroupChanges();
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
