var PYO = (function (PYO, $) {

    'use strict';

    var postAjax = {
        XHR: {},
        count: 0
    };

    PYO.scrollToBottom = function () {
        if ($('.feed-posts').length) {
            var feed = $('.feed-posts');
            var height = parseInt(feed.get(0).scrollHeight, 10);
            feed.scrollTop(height).scroll();
        }
    };

    PYO.scrolledToBottom = function () {
        var feed = $('.feed-posts');
        var bottom = false;
        if (feed.length && feed.get(0).scrollHeight - feed.scrollTop() - feed.outerHeight() <= 50) {
            bottom = true;
        }
        return bottom;
    };

    PYO.renderPost = function (data) {
        var posts;
        if (data && data.posts && data.posts.length) {
            posts = PYO.tpl('posts', data);
        }
        return posts;
    };

    PYO.addPost = function (data) {
        if (data) {
            var feedPosts = $('.village-feed .feed-posts');
            var instructions = feedPosts.find('.howto');
            var posts = PYO.renderPost(data);
            posts.find('.details').html5accordion();
            if (instructions.length) { instructions.before(posts); }
            else { feedPosts.append(posts); }
            PYO.authorPosts = feedPosts.find('.post.mine').length;
            return posts;
        }
    };

    PYO.replacePost = function (newPostData, oldPost) {
        if (newPostData && oldPost && oldPost.length) {
            var post_obj = { posts: [newPostData] };
            var newPost = PYO.renderPost(post_obj);
            var scroll = PYO.scrolledToBottom();
            newPost.filter('.post.mine').removeClass('old');
            newPost.find('.details').html5accordion();
            oldPost.loadingOverlay('remove');
            oldPost.replaceWith(newPost);
            $.doTimeout('new-post-' + newPostData.author_sequence_id);
            if (scroll) { PYO.scrollToBottom(); }
        }
    };

    PYO.createPostObj = function (author_sequence, xhr_count, smsTargetArr) {
        var feed = $('.village-feed');
        var textarea = $('#post-text');
        var author = feed.data('author');
        var role = feed.data('author-role');
        var today = new Date();
        var hour = today.getHours();
        var minute = today.getMinutes();
        minute = (minute < 10) ? '0' + minute : minute;
        var period = (hour > 12) ? 'pm' : 'am';
        hour = (hour > 12) ? hour - 12 : hour;
        var time = hour + ':' + minute + period;
        var text = $.trim(textarea.val());
        var postObj = {
            posts: [
                {
                    author: author,
                    author_id: PYO.activeUserId,
                    role: role,
                    timestamp_display: time,
                    text: text,
                    author_sequence_id: author_sequence,
                    xhr_count: xhr_count,
                    pending: true,
                    school_staff: true,
                    mine: true,
                    sms: smsTargetArr.length ? true : false,
                    to_sms: smsTargetArr.length ? true : false,
                    plural_sms: smsTargetArr.length > 1 ? 's' : '',
                    sms_recipients: smsTargetArr.join(', ')
                }
            ]
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
                    var text = $.trim(textarea.val());
                    var author_sequence_id = (PYO.authorPosts || 0) + 1;
                    var url = feed.data('post-url');
                    var count = ++postAjax.count;
                    var postData = [
                        { name: 'text', value: text },
                        { name: 'author_sequence_id', value: author_sequence_id }
                    ];
                    var smsInputName = $('#sms-target').attr('name');
                    var smsTargetArr = [];
                    var postObj, post;

                    form.find('.sms-targeting .ui-multiselect-checkboxes input:checked').each(function () {
                        var obj = { name: smsInputName, value: $(this).val() };
                        var displayName = $(this).data('actual-name') ? $(this).data('actual-name') : $(this).data('role');
                        postData.push(obj);
                        smsTargetArr.push(displayName);
                    });

                    postObj = PYO.createPostObj(author_sequence_id, count, smsTargetArr);
                    post = PYO.addPost(postObj);

                    if (url) {
                        postAjax.XHR[count] = $.post(url, postData, function (response) {
                            PYO.postAjaxSuccess(response, author_sequence_id, count);
                        }).error(function (request, status) {
                            PYO.postAjaxError(post, author_sequence_id, status, count);
                            postAjax.XHR[count] = null;
                        });
                    }

                    textarea.val('').change();
                    feed.find('.howto').remove();
                    PYO.scrollToBottom();
                    PYO.addPostTimeout(post, author_sequence_id, count);
                    $('#sms-target').multiselect('checkAll');
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
        if (response && response.posts && response.posts.length) {
            var feed = $('.village-feed');
            $.each(response.posts, function () {
                feed.trigger('successful-post', {smsRecipients: this.num_sms_recipients, studentId: PYO.activeStudentId, groupId: PYO.activeGroupId});
                if (this.author_sequence_id) {
                    var oldPost = feed.find('.post.mine.pending[data-author-sequence="' + this.author_sequence_id + '"]');
                    if (oldPost.length) { PYO.replacePost(this, oldPost); }
                }
            });
        }
        PYO.removePostTimeout(old_author_sequence);
        postAjax.XHR[xhr_count] = null;
    };

    PYO.postAjaxError = function (post, author_sequence_id, status, xhr_count) {
        if (status !== 'abort' && status !== 'timeout') {
            var msg = PYO.tpl('post_timeout_msg');
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
            PYO.scrollToBottom();
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
        var text = $.trim(post.find('.post-text').text());
        var postData = {
            author_sequence_id: author_sequence_id,
            text: text
        };
        var count = ++postAjax.count;

        if (url) {
            postAjax.XHR[count] = $.post(url, postData, function (response) {
                PYO.postAjaxSuccess(response, author_sequence_id, count);
            }).error(function (request, status) {
                PYO.postAjaxError(post, author_sequence_id, status, count);
                postAjax.XHR[count] = null;
            });
        }

        post.find('.timeout').remove();
        post.loadingOverlay();
        PYO.addPostTimeout(post, author_sequence_id, count);
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
                var chars = $.trim(textarea.val()).length;
                var remain = limit - chars;
                if (remain < 0) {
                    count.addClass('overlimit');
                    button.not('.disabled').attr('disabled', 'disabled');
                } else {
                    count.removeClass('overlimit');
                    button.not('.disabled').removeAttr('disabled');
                }
                count.text(remain + ' characters remaining...');
            };

            textarea.keyup(updateCount).change(updateCount);
        }
    };

    PYO.initializeMultiselect = function () {
        var context = $('.village-main');
        var form = context.find('.post-add-form');
        var select = form.find('#sms-target');
        select.multiselect({
            checkAllText: 'all',
            uncheckAllText: 'none',
            noneSelectedText: 'no one',
            selectedText: function (checked, total, arr) {
                if (checked < 4) {
                    return $(arr).map(function () { return $(this).data('role'); }).get().join(', ');
                } else {
                    if (checked === total) {
                        return 'all family members';
                    } else {
                        return checked + ' family members';
                    }
                }
            }
        });

        if (PYO.directSmsName) {
            $('.elder-list.family .elder .action-sms[data-name="' + PYO.directSmsName + '"]').click();
            PYO.directSmsName = '';
        }
    };

    PYO.initializeSmsDirectLinks = function () {
        $('body').on('click', '.elder-list.family .elder .action-sms', function (e) {
            e.preventDefault();
            var context = $('.village-main');
            var el = $(this);
            var name = el.data('name');
            var textarea = context.find('#post-text');

            if (textarea.length) {
                textarea.focus();
                var form = context.find('.post-add-form');
                var select = form.find('#sms-target');
                select.multiselect('uncheckAll');
                select.multiselect('widget').find('input[data-name="' + name + '"]').each(function () {
                    this.click();
                });
            } else {
                PYO.directSmsName = name;
                $('.village-nav .ajax-link.active').click();
            }
        });
    };

    PYO.markPostsRead = function () {
        var feed = $('.village-feed');
        var nav = $('.village-nav');
        var posts = feed.find('.post.unread');

        nav.find('.student .listitem-select[data-id="' + PYO.activeStudentId + '"] .unread').addClass('zero').text('0');

        if (posts.length) {
            posts.each(function () {
                var thisPost = $(this);
                var url = thisPost.data('mark-read-url');
                if (url) {
                    $.post(url, function () {
                        thisPost.removeClass('unread');
                    });
                }
            });
        }
    };

    PYO.watchForReadPosts = function () {
        $('.feed-posts').scroll(function () {
            $.doTimeout('scroll', 150, function () {
                if (PYO.scrolledToBottom()) {
                    PYO.markPostsRead();
                }
            });
        });
    };

    PYO.initializeFeed = function () {
        var feed = $('.village-feed');
        var posts = feed.find('.post');

        posts.find('.details').html5accordion();
        PYO.authorPosts = posts.filter('.mine').length;
        posts.filter('.unread').removeClass('unread');

        PYO.initializeMultiselect();
        PYO.watchForReadPosts();
        PYO.submitPost('.village-feed');
        PYO.characterCount('.village-main');
        PYO.scrollToBottom();
    };

    return PYO;

}(PYO || {}, jQuery));
