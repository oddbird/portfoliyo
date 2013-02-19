var PYO = (function (PYO, $) {

    'use strict';

    var nav = $('.village-nav');

    PYO.listenForPosts = function () {
        var addNewPost = function (newPostData, unread) {
            var addPost = function () {
                var scroll = PYO.scrolledToBottom();
                if (unread) { newPostData.unread = true; }
                var post_obj = { posts: [newPostData] };
                PYO.addPost(post_obj);
                if (scroll) {
                    PYO.scrollToBottom();
                } else if (unread && newPostData.author_id !== PYO.activeUserId && newPostData.student_id) {
                    incrementUnread(newPostData.student_id);
                }
            };
            var oldPost = $('.village-feed').find('.post.mine[data-author-sequence="' + newPostData.author_sequence_id + '"]');
            if (oldPost.length) {
                if (oldPost.hasClass('pending')) {
                    PYO.replacePost(newPostData, oldPost);
                } else if (oldPost.data('post-id') !== newPostData.post_id) {
                    addPost();
                }
            } else {
                addPost();
            }
        };
        var incrementUnread = function (id) {
            var groups = nav.find('.group .group-link.listitem-select');
            var students = nav.find('.student .listitem-select');
            var increment = function (el) {
                var unread = $(el).find('.unread');
                var count = parseInt($.trim(unread.text()), 10);
                unread.removeClass('zero').text(++count);
            };

            students.filter('[data-id="' + id + '"]').each(function () {
                increment(this);
            });

            groups.filter(function () {
                var students_arr = $.trim($(this).data('students')).split(' ');
                return $.inArray(id.toString(), students_arr) !== -1;
            }).each(function () {
                increment(this);
            });
        };

        PYO.channel.bind('message_posted', function (data) {
            if (data && data.posts && data.posts.length) {
                var feed = $('.village-feed');

                $.each(data.posts, function () {
                    if (this.student_id) {
                        if (feed.length && PYO.activeStudentId && this.student_id === PYO.activeStudentId) {
                            addNewPost(this, true);
                        } else if (this.author_id !== PYO.activeUserId) {
                            incrementUnread(this.student_id);
                        }
                    }

                    if (this.group_id && feed.length && !PYO.activeStudentId && PYO.activeGroupId && this.group_id === PYO.activeGroupId) {
                        addNewPost(this);
                    }
                });
            }
        });
    };

    PYO.listenForStudentChanges = function () {
        PYO.channel.bind('student_added', function (data) {
            if (data && data.objects && data.objects.length) {
                $.each(data.objects, function () {
                    var id = this.id;
                    var all_groups = nav.find('.group .group-link');
                    var group_titles = nav.find('.navtitle .group-feed');
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
                    }
                });
            }
        });

        PYO.channel.bind('student_removed', function (data) {
            if (data && data.objects && data.objects.length) {
                $.each(data.objects, function () {
                    if (this.id) {
                        var id = this.id;
                        var all_groups = nav.find('.group .group-link');
                        var group_titles = nav.find('.navtitle .group-feed');
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
                        }
                    }
                });
            }
        });

        PYO.channel.bind('student_edited', function (data) {
            if (data && data.objects && data.objects.length) {
                $.each(data.objects, function () {
                    if (this.id && this.name && nav.find('.student .listitem-select[data-id="' + this.id + '"]').length) {
                        var id = this.id;
                        var name = this.name;
                        var student = nav.find('.student .listitem-select[data-id="' + id + '"]');
                        if (student.data('name') !== name) {
                            // @@@ student-list should be re-alphabetized (and change active village header?)
                            student.find('.listitem-name').text(name);
                            student.data('name', name).attr('data-name', name);
                        }
                    }
                });
            }
        });
    };

    PYO.listenForGroupChanges = function () {
        PYO.channel.bind('student_added_to_group', function (data) {
            if (data && data.objects && data.objects.length) {
                $.each(data.objects, function () {
                    var evData = this;
                    var id = evData.id;
                    var added_to_groups_arr = evData.groups;
                    var group_titles = nav.find('.navtitle .group-feed');
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

        PYO.channel.bind('student_removed_from_group', function (data) {
            if (data && data.objects && data.objects.length) {
                $.each(data.objects, function () {
                    if (this.id) {
                        var id = this.id;
                        var removed_from_groups_arr = this.groups;
                        var group_titles = nav.find('.navtitle .group-feed');
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

        PYO.channel.bind('group_added', function (data) {
            // If viewing the groups-list
            if (data && data.objects && data.objects.length && nav.find('.group').length) {
                $.each(data.objects, function () {
                    PYO.addGroupToList(this);
                });
            }
        });

        PYO.channel.bind('group_removed', function (data) {
            if (data && data.objects && data.objects.length) {
                $.each(data.objects, function () {
                    if (this.id) {
                        PYO.removeGroupFromList(this.id);
                    }
                });
            }
        });

        PYO.channel.bind('group_edited', function (data) {
            if (data && data.objects && data.objects.length) {
                $.each(data.objects, function () {
                    if (this.id && this.name) {
                        var id = this.id;
                        var name = this.name;
                        var group = nav.find('.group .group-link[data-group-id="' + id + '"]');
                        var grouptitle = nav.find('.navtitle .group-feed[data-group-id="' + id + '"]');
                        // If viewing the groups-list
                        if (group.length && group.data('group-name') !== name) {
                            // @@@ groups list should be re-alphabetized (and update group village header?)
                            group.find('.listitem-name').text(name);
                            group.data('group-name', name).attr('data-group-name', name);
                        }
                        // If viewing the edited group
                        if (grouptitle.length && grouptitle.data('group-name') !== name) {
                            grouptitle.closest('.navtitle').find('.group-name').text(name);
                            grouptitle.data('group-name', name).attr('data-group-name', name);
                        }
                    }
                });
            }
        });
    };

    PYO.preventPusherAfterFormSubmit = function () {
        $('.village').on('submit', 'form', function (e) {
            if (!e.isDefaultPrevented()) {
                PYO.pusher.unsubscribe('private-user_' + PYO.activeUserId);
            }
        });
    };

    PYO.initializePusher = function () {
        PYO.pusherKey = $('.village').data('pusher-key');
        if (PYO.pusherKey) {
            PYO.pusher = new Pusher(PYO.pusherKey, {encrypted: true});
            if (PYO.activeUserId) {
                PYO.channel = PYO.pusher.subscribe('private-user_' + PYO.activeUserId);
                PYO.listenForPosts();
                PYO.listenForStudentChanges();
                PYO.listenForGroupChanges();
                PYO.preventPusherAfterFormSubmit();
            }
        }
    };

    return PYO;

}(PYO || {}, jQuery));
