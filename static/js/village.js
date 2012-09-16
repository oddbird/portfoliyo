var PYO = (function (PYO, $) {

    'use strict';

    PYO.activeStudentId = $('.village-feed').data('student-id');
    PYO.activeUserId = $('.village-feed').data('user-id');
    PYO.pusherKey = $('.village-feed').data('pusher-key');

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
            var height = context.get(0).scrollHeight;
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
        if (data && data.posts[0] && data.posts[0].author_sequence_id) {
            var feed = $('.village-feed');
            var author_sequence_id = data.posts[0].author_sequence_id;
            var newPost = PYO.renderPost(data);
            var oldPost = feed.find('.post[data-author-sequence="' + author_sequence_id + '"]');
            if (oldPost && oldPost.length) {
                oldPost.replaceWith(newPost);
                PYO.scrollToBottom('.village-feed');
                $.doTimeout('new-post-' + author_sequence_id);
                return true;
            }
        }
    };

    PYO.createPostObj = function (author_sequence) {
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
            var author_sequence;
            var setAuthSeq = function () {
                author_sequence = feed.find('.post.mine').length + 1;
            };

            form.submit(function (event) {
                event.preventDefault();
                if (textarea.val().length) {
                    setAuthSeq();
                    form.ajaxSubmit({
                        data: { author_sequence_id: author_sequence },
                        beforeSubmit: function (arr, form, opts) {
                            var response = PYO.createPostObj(author_sequence);
                            var post = PYO.addPost(response);
                            textarea.val('').change();
                            $.doTimeout('new-post-' + author_sequence, 5000, function () {
                                PYO.postTimeout(post);
                            });
                        },
                        success: function (response) {
                            PYO.serverSuccess(response);
                        }
                    });
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

    PYO.serverSuccess = function (response) {
        if (response) {
            if (response.posts[0] && response.posts[0].author_sequence_id) {
                var feed = $('.village-feed');
                var author_sequence_id = response.posts[0].author_sequence_id;
                var oldPost = feed.find('.post[data-author-sequence="' + author_sequence_id + '"]');
                if (oldPost && oldPost.length) {
                    oldPost.loadingOverlay('remove');
                }
                PYO.removeTimeout(author_sequence_id);
            }
            if (response.success && !PYO.pusherKey) {
                PYO.replacePost(response);
            }
        }
    };

    PYO.postTimeout = function (post) {
        var msg = ich.post_timeout_msg();
        msg.find('.resend').click(function (e) {
            e.preventDefault();
            var thisPost = $(this).closest('.post');
            PYO.resendPost(thisPost);
        });
        msg.find('.cancel').click(function (e) {
            e.preventDefault();
            post.remove();
        });
        post.addClass('not-posted').prepend(msg).loadingOverlay('remove');
        PYO.scrollToBottom('.village-feed');
    };

    PYO.removeTimeout = function (author_sequence_id) {
        $.doTimeout('new-post-' + author_sequence_id);
    };

    PYO.resendPost = function (post) {
        var feed = $('.village-feed');
        var url = feed.data('post-url');
        var author_sequence = post.data('author-sequence');
        var text = post.find('.post-text').text();
        var postData = {
            author_sequence_id: author_sequence,
            text: text
        };
        $.post(url, postData, function (response) {
            PYO.serverSuccess(response);
        });
        post.find('.timeout').remove();
        post.loadingOverlay();
        $.doTimeout('new-post-' + author_sequence, 5000, function () {
            PYO.postTimeout(post);
        });
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
        if ($(container).length) {
            var feed = $(container);
            var url = feed.data('backlog-url');
            $.get(url, function (data) {
                PYO.addPost(data);
            });
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

    PYO.initializeFeed = function () {
        PYO.fetchBacklog('.village-feed');
        PYO.activeStudentId = $('.village-feed').data('student-id');
        PYO.submitPost('.village-feed');
        PYO.characterCount('.village');
        PYO.scrollToBottom('.village-feed');
        PYO.listenForPusherEvents('.village-feed');
    };

    return PYO;

}(PYO || {}, jQuery));
