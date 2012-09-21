var PYO = (function (PYO, $) {

    'use strict';

    var pageAjax = {
        XHR: null,
        count: 0
    };
    var postAjax = {
        XHR: {},
        count: 0
    };
    var feedAjax = {
        XHR: null,
        count: 0
    };

    PYO.updatePageHeight = function (container) {
        if ($(container).length) {
            var page = $(container);
            var headerHeight = $('div[role="banner"]').outerHeight();
            var footerHeight = $('footer').outerHeight();
            var pageHeight, transition;
            var updateHeight = function (animate) {
                pageHeight = $(window).height() - headerHeight - footerHeight;
                if (animate) {
                    page.css('height', pageHeight.toString() + 'px');
                } else {
                    transition = page.css('transition');
                    page.css({
                        'transition': 'none',
                        'height': pageHeight.toString() + 'px'
                    });
                    $(window).load(function () {
                        page.css('transition', transition);
                    });
                }
            };
            updateHeight();

            $(window).resize(function () {
                $.doTimeout('resize', 250, function () {
                    updateHeight(true);
                });
            });
        }
    };

    PYO.scrollToBottom = function (container) {
        if ($(container).length) {
            var context = $(container);
            var height = parseInt(context.get(0).scrollHeight, 10);
            context.scrollTop(height);
        }
    };

    PYO.renderPost = function (data) {
        var post;
        if (data) {
            post = ich.post(data);
        }
        if (post) {
            post.find('.nametag[data-user-id="' + PYO.activeUserId + '"]').addClass('me');
            post.filter('.post[data-author-id="' + PYO.activeUserId + '"]').addClass('mine');
            return post;
        }
    };

    PYO.addPost = function (data) {
        if (data) {
            var post = PYO.renderPost(data);
            $('.village-feed').append(post);
            PYO.scrollToBottom('.village-feed');
            return post;
        }
    };

    PYO.replacePost = function (data) {
        if (data && data.posts[0] && data.posts[0].author_sequence_id && data.posts[0].author_id) {
            var feed = $('.village-feed');
            var author_sequence_id = data.posts[0].author_sequence_id;
            var author_id = data.posts[0].author_id;
            var oldPost = feed.find('.post[data-author-id="' + author_id + '"][data-author-sequence="' + author_sequence_id + '"]');
            if (oldPost && oldPost.length) {
                var newPost = PYO.renderPost(data);
                oldPost.replaceWith(newPost);
                PYO.scrollToBottom('.village-feed');
                $.doTimeout('new-post-' + author_sequence_id);
                return true;
            }
        }
    };

    PYO.createPostObj = function (author_sequence, xhr_count) {
        var feed = $('.village-feed');
        var textarea = $('#post-text');
        var author = feed.data('author');
        var role = feed.data('author-role');
        var today = new Date();
        var day = today.getDate();
        var month = today.getMonth() + 1;
        var year = today.getFullYear();
        var date = month + '/' + day + '/' + year;
        var hour = today.getHours();
        var minute = today.getMinutes();
        minute = (minute < 10) ? '0' + minute : minute;
        var period = (hour > 12) ? 'p.m.' : 'a.m.';
        hour = (hour > 12) ? hour - 12 : hour;
        var time = hour + ':' + minute + ' ' + period;
        var text = textarea.val();
        var postObj = {
            posts: {
                author: author,
                author_id: PYO.activeUserId,
                role: role,
                date: date,
                time: time,
                text: text,
                author_sequence_id: author_sequence,
                xhr_count: xhr_count,
                escape: true
            }
        };
        return postObj;
    };

    PYO.submitPost = function (container) {
        if ($(container).length) {
            var feed = $(container);
            var context = feed.closest('.village');
            var form = context.find('form.post-add-form');
            var button = form.find('.action-post');
            var textarea = form.find('#post-text');

            form.submit(function (event) {
                event.preventDefault();
                if (textarea.val().length) {
                    var text = textarea.val();
                    var author_sequence_id = ++PYO.authorPosts;
                    var url = feed.data('post-url');
                    var count = ++postAjax.count;
                    var postObj = PYO.createPostObj(author_sequence_id, count);
                    var post = PYO.addPost(postObj);
                    var postData = {
                        text: text,
                        author_sequence_id: author_sequence_id
                    };

                    if (url) {
                        postAjax.XHR[count] = $.post(url, postData, function (response) {
                            PYO.postAjaxSuccess(response, author_sequence_id, count);
                        }).error(function (request, status, error) {
                            PYO.postAjaxError(post, author_sequence_id, status, count);
                            postAjax.XHR[count] = null;
                        });
                    }

                    textarea.val('').change();
                    PYO.addPostTimeout(post, author_sequence_id, count);
                }
            });

            textarea.keydown(function (event) {
                if (event.keyCode === PYO.keycodes.ENTER && !event.shiftKey) {
                    event.preventDefault();
                    if (!button.is(':disabled')) {
                        form.submit();
                    }
                }
            });
        }
    };

    PYO.postAjaxSuccess = function (response, old_author_sequence, xhr_count) {
        if (response && response.posts[0] && response.posts[0].student_id && response.posts[0].student_id === PYO.activeStudentId) {
            if (response.posts[0].author_sequence_id) {
                var feed = $('.village-feed');
                var author_sequence_id = response.posts[0].author_sequence_id;
                var oldPost = feed.find('.post.mine[data-author-sequence="' + author_sequence_id + '"]');
                if (oldPost && oldPost.length) {
                    oldPost.loadingOverlay('remove');
                }
            }
            if (response.success && !PYO.pusherKey) {
                PYO.replacePost(response);
            }
        }
        PYO.removePostTimeout(old_author_sequence);
        postAjax.XHR[xhr_count] = null;
    };

    PYO.postAjaxError = function (post, author_sequence_id, status, xhr_count) {
        if (status !== 'abort' && status !== 'timeout') {
            var msg = ich.post_timeout_msg();
            msg.find('.resend').click(function (e) {
                e.preventDefault();
                var thisPost = $(this).closest('.post');
                PYO.resendPost(thisPost);
                if (postAjax.XHR[xhr_count]) { postAjax.XHR[xhr_count].abort(); }
            });
            msg.find('.cancel').click(function (e) {
                e.preventDefault();
                post.remove();
                if (postAjax.XHR[xhr_count]) { postAjax.XHR[xhr_count].abort(); }
            });
            post.addClass('not-posted').prepend(msg).loadingOverlay('remove');
            PYO.scrollToBottom('.village-feed');
            PYO.removePostTimeout(author_sequence_id);
        }
    };

    PYO.removePostTimeout = function (author_sequence_id) {
        $.doTimeout('new-post-' + author_sequence_id);
    };

    PYO.addPostTimeout = function (post, author_sequence_id, xhr_count) {
        $.doTimeout('new-post-' + author_sequence_id, 10000, function () {
            PYO.postAjaxError(post, author_sequence_id, 'warning', xhr_count);
        });
    };

    PYO.resendPost = function (post) {
        var feed = $('.village-feed');
        var url = feed.data('post-url');
        var author_sequence_id = post.data('author-sequence');
        var text = post.find('.post-text').text();
        var postData = {
            author_sequence_id: author_sequence_id,
            text: text
        };
        var count = ++postAjax.count;

        if (url) {
            postAjax.XHR[count] = $.post(url, postData, function (response) {
                PYO.postAjaxSuccess(response, author_sequence_id, count);
            }).error(function (request, status, error) {
                PYO.postAjaxError(post, author_sequence_id, status, count);
                postAjax.XHR[count] = null;
            });
        }

        post.find('.timeout').remove();
        post.loadingOverlay();
        PYO.addPostTimeout(post, author_sequence_id, count);
    };

    PYO.listenForPusherEvents = function (container) {
        if ($(container).length && PYO.pusherKey) {
            var pusher = new Pusher(PYO.pusherKey, {encrypted: true});
            var students = $('.village-nav .student a');

            students.each(function () {
                var el = $(this);
                var id = el.data('id');
                var unread = el.find('.unread');
                var channel = pusher.subscribe('student_' + id);

                channel.bind('message_posted', function (data) {
                    if (id === PYO.activeStudentId) {
                        if (!PYO.replacePost(data)) {
                            PYO.addPost(data);
                        }
                    } else {
                        var count = parseInt(unread.text(), 10);
                        unread.removeClass('zero').text(++count);
                    }
                });
            });
        }
    };

    PYO.fetchBacklog = function (container) {
        if (feedAjax.XHR) { feedAjax.XHR.abort(); }
        if ($(container).length) {
            var feed = $(container);
            var context = feed.closest('.village-main');
            var url = feed.data('backlog-url');
            var count = ++feedAjax.count;
            var loadFeed = function () {
                if (url) {
                    context.loadingOverlay();
                    feedAjax.XHR = $.get(url, function (response) {
                        context.loadingOverlay('remove');
                        if (response && feedAjax.count === count) {
                            PYO.addPost(response);
                            PYO.authorPosts = feed.find('.post.mine').length;
                        }
                        feedAjax.XHR = null;
                    }).error(function (request, status, error) {
                        if (status !== 'abort') {
                            var msg = ich.feed_error_msg();
                            msg.find('.reload-feed').click(function (e) {
                                e.preventDefault();
                                msg.remove();
                                loadFeed();
                            });
                            feed.prepend(msg);
                        }
                        context.loadingOverlay('remove');
                        feedAjax.XHR = null;
                    });
                }
            };

            loadFeed();
        }
    };

    PYO.characterCount = function (container) {
        if ($(container).length) {
            var context = $(container);
            var form = context.find('form.post-add-form');
            var textarea = form.find('#post-text');
            var limit = form.data('char-limit');
            var count = form.find('.charcount');
            var button = form.find('.action-post');
            var updateCount = function () {
                var chars = textarea.val().length;
                var remain = limit - chars;
                if (remain < 0) {
                    count.addClass('overlimit');
                    button.attr('disabled', 'true');
                } else {
                    count.removeClass('overlimit');
                    button.removeAttr('disabled');
                }
                count.text(remain + ' characters remaining...');
            };

            textarea.keyup(updateCount).change(updateCount);
        }
    };

    PYO.pageAjaxError = function (url) {
        var container = $('.village-content');
        var msg = ich.pjax_error_msg();
        msg.find('.reload-pjax').click(function (e) {
            e.preventDefault();
            msg.remove();
            PYO.pageAjaxLoad(url);
        });
        container.loadingOverlay('remove');
        container.html(msg);
    };

    PYO.pageAjaxLoad = function (url) {
        if (pageAjax.XHR) { pageAjax.XHR.abort(); }

        var container = $('.village-content');
        var count = ++pageAjax.count;

        if (url) {
            container.loadingOverlay();
            container.find('.feed-error, .pjax-error').remove();

            pageAjax.XHR = $.get(url, function (response) {
                if (response && response.html && pageAjax.count === count) {
                    container.replaceWith($(response.html));
                    PYO.initializePage();
                }
                container.loadingOverlay('remove');
                pageAjax.XHR = null;
            }).error(function (request, status, error) {
                if (status !== 'abort') {
                    PYO.pageAjaxError(url);
                }
                pageAjax.XHR = null;
            });
        }
    };

    PYO.ajaxifyVillages = function (container) {
        if ($(container).length) {
            var context = $(container);
            var History = window.History;

            if (History.enabled) {
                $('body').on('click', 'a.ajax-link', function (e) {
                    if (e.which === 2 || e.metaKey) {
                        return true;
                    } else {
                        e.preventDefault();
                        var url = $(this).attr('href');
                        if ($(this).hasClass('active')) {
                            PYO.pageAjaxLoad(url + '?ajax=true');
                        } else {
                            var title = document.title;
                            var data = { url: url };
                            if ($(this).hasClass('addelder-link')) {
                                data.remainActive = true;
                            }
                            History.pushState(data, title, url);
                        }
                        $(this).blur();
                    }
                });

                $(window).bind('statechange', function () {
                    context.trigger('pjax-load');
                    var data = History.getState().data;
                    var url = data.url ? data.url : window.location.pathname;
                    if (!data.remainActive) {
                        context.find('.village-nav .ajax-link').removeClass('active');
                    }
                    context.find('a.ajax-link[href="' + url + '"]').addClass('active');
                    PYO.pageAjaxLoad(url + '?ajax=true');
                });
            }
        }
    };

    PYO.editStudentName = function (container) {
        if ($(container).length) {
            var nav = $(container);
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
            var cancel = function (student) {
                var link = student.data('link');
                var edit = student.find('.edit-student');
                var save = student.find('.save-student');
                var editing = student.find('.select-student.editing');
                editing.replaceWith(link);
                save.hide();
                edit.show();
            };

            nav.on('click', '.edit-student', function (e) {
                e.preventDefault();
                var edit = $(this);
                var student = edit.closest('.student');
                var link = student.find('.select-student');
                var name = student.find('.student-name').text();
                var save = student.find('.save-student');
                var editing = ich.edit_student({name: name});

                student.data('link', link);
                link.replaceWith(editing);
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
                        cancel(student);
                    }
                });
            });

            nav.on('click', '.save-student', function (e) {
                var save = $(this);
                var student = save.closest('.student');
                var url = student.data('url');
                var edit = student.find('.edit-student');
                var editing = student.find('.select-student.editing');
                var link = student.data('link');
                var name = link.find('.student-name');
                var oldName = editing.data('original-name');
                var newName = $.trim(editing.text());

                if (url && newName && newName !== oldName) {
                    student.loadingOverlay();
                    $.post(url, {name: newName}, function (response) {
                        student.loadingOverlay('remove');
                        if (response && response.name && response.success) {
                            name.text(response.name);
                            editing.replaceWith(link);
                            save.hide();
                            edit.show();
                        }
                    });
                } else {
                    cancel(student);
                }
            });

            $('.village').on('pjax-load', function (e) {
                nav.find('.select-student.editing').each(function () {
                    var student = $(this).closest('.student');
                    cancel(student);
                });
            });
        }
    };

    PYO.initializeEldersForm = function () {
        $('.formset.elders').formset({
            prefix: $('.formset.elders').data('prefix'),
            formTemplate: '#empty-elder-form',
            formSelector: '.fieldset.elder',
            addLink: '<a class="add-row" href="javascript:void(0)" title="more elders">more elders</a>',
            addAnimationSpeed: 'normal',
            removeAnimationSpeed: 'fast',
            optionalIfEmpty: true
        });
        if ($('#id_name').length) {
            $('#id_name').focus();
        } else {
            $('#id_elders-0-contact').focus();
        }
    };

    PYO.initializeFeed = function () {
        PYO.activeStudentId = $('.village-feed').data('student-id');
        PYO.activeUserId = $('.village-feed').data('user-id');
        PYO.fetchBacklog('.village-feed');
        PYO.submitPost('.village-feed');
        PYO.characterCount('.village-main');
    };

    PYO.initializePage = function () {
        if ($('.village-feed').length) {
            PYO.initializeFeed();
        }
        if ($('.formset.elders').length) {
            PYO.initializeEldersForm();
        }
    };

    return PYO;

}(PYO || {}, jQuery));
