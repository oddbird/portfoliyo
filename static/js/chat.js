var PYO = (function (PYO, $) {

    'use strict';

    var nav = $('.village-nav');

    var postAjax = {
        XHR: {},
        count: 0
    };

    var backlogXHR = false;
    var backlogHasMore;

    PYO.scrollToBottom = function () {
        if (PYO.feedPosts.length) {
            var height = parseInt(PYO.feedPosts.get(0).scrollHeight, 10);
            PYO.feedPosts.scrollTop(height).scroll();
        }
    };

    PYO.scrolledToBottom = function () {
        var bottom = false;
        if (PYO.feedPosts.length && PYO.feedPosts.get(0).scrollHeight - PYO.feedPosts.scrollTop() - PYO.feedPosts.outerHeight() <= 50) {
            bottom = true;
        }
        return bottom;
    };

    PYO.renderPost = function (data) {
        var posts;
        if (data) {
            posts = PYO.tpl('posts', data);
        }
        return posts;
    };

    PYO.addPost = function (data) {
        if (data) {
            var instructions = PYO.feedPosts.find('.howto');
            var posts = PYO.renderPost(data);
            posts.find('.details').html5accordion();
            if (instructions.length) { instructions.before(posts); }
            else { PYO.feedPosts.append(posts); }
            PYO.authorPosts = PYO.feedPosts.find('.post.mine').length;
            return posts;
        }
    };

    PYO.replacePost = function (newPostData, oldPost) {
        if (newPostData && oldPost && oldPost.length) {
            var post_obj = { objects: [newPostData] };
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
        var textarea = $('#post-text');
        var author = PYO.feed.data('author');
        var role = PYO.feed.data('author-role');
        var today = new Date();
        var hour = today.getHours();
        var minute = today.getMinutes();
        minute = (minute < 10) ? '0' + minute : minute;
        var period = (hour > 12) ? 'pm' : 'am';
        hour = (hour > 12) ? hour - 12 : hour;
        var time = hour + ':' + minute + period;
        var text = $.trim(textarea.val());
        var postObj = {
            objects: [{
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
            }]
        };
        return postObj;
    };

    PYO.submitPost = function () {
        if (PYO.feed.length) {
            var context = PYO.feed.closest('.village');
            var form = context.find('form.post-add-form');
            var button = form.find('.action-post');
            var textarea = form.find('#post-text');

            form.submit(function (event) {
                event.preventDefault();
                if (textarea.val().length) {
                    var text = $.trim(textarea.val());
                    var author_sequence_id = (PYO.authorPosts || 0) + 1;
                    var url = PYO.feed.data('post-url');
                    var count = ++postAjax.count;
                    var postData = [
                        { name: 'text', value: text },
                        { name: 'author_sequence_id', value: author_sequence_id }
                    ];
                    var smsSelect = form.find('.sms-targeting');
                    var smsInputName = smsSelect.find('#sms-target').attr('name');
                    var smsTargetArr = [];
                    var postObj, post;

                    if (smsSelect.length) {
                        smsSelect.find('.ui-multiselect-checkboxes input:checked').each(function () {
                            var obj = { name: smsInputName, value: $(this).val() };
                            var displayName = $(this).data('actual-name') ? $(this).data('actual-name') : $(this).data('role');
                            postData.push(obj);
                            smsTargetArr.push(displayName);
                        });
                    } else {
                        context.find('.village-info .elder-list.family .parents-list .parent .vcard.mobile').each(function () {
                            var name = $(this).find('.fn').data('name');
                            var role = $(this).find('.fn').data('role');
                            var displayName = name ? name : role;
                            smsTargetArr.push(displayName);
                        });
                    }

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
                    PYO.feed.find('.howto').remove();
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
        if (response && response.objects && response.objects.length) {
            $.each(response.objects, function () {
                PYO.feed.trigger('successful-post', {smsRecipients: this.num_sms_recipients, studentId: PYO.activeStudentId, groupId: PYO.activeGroupId});
                if (this.author_sequence_id) {
                    var oldPost = PYO.feed.find('.post.mine.pending[data-author-sequence="' + this.author_sequence_id + '"]');
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
        var url = PYO.feed.data('post-url');
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
    };

    PYO.markPostsRead = function () {
        var posts = PYO.feed.find('.post.unread');

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
        PYO.feedPosts.scroll(function () {
            $.doTimeout('scroll', 150, function () {
                if (PYO.scrolledToBottom()) {
                    PYO.markPostsRead();
                }
            });
        });
    };

    PYO.fetchBacklog = function () {
        var feedStatus = PYO.feedPosts.find('.feedstatus');
        var url = PYO.feed.data('posts-url');
        var timestamp = PYO.feedPosts.find('.post').first().find('time.pubdate').attr('datetime');
        var postData = {
            order_by: '-timestamp',
            timestamp__lt: timestamp
        };
        if (PYO.activeStudentId) {
            postData.student = PYO.activeStudentId;
        } else if (PYO.activeGroupId) {
            postData.group = PYO.activeGroupId;
        }
        if (url && !backlogXHR) {
            feedStatus.addClass('loading').removeClass('error');
            backlogXHR = $.get(url, postData, function (data) {
                if (data && data.objects && data.objects.length) {
                    data.objects.reverse();
                    var posts = PYO.renderPost(data);
                    posts.find('.details').html5accordion();
                    var scrollBottom = PYO.feedPosts.get(0).scrollHeight - PYO.feedPosts.scrollTop() - PYO.feedPosts.outerHeight();
                    feedStatus.after(posts);
                    var scrollTo = PYO.feedPosts.get(0).scrollHeight - PYO.feedPosts.outerHeight() - scrollBottom;
                    PYO.feedPosts.scrollTop(scrollTo);
                    PYO.authorPosts = PYO.feedPosts.find('.post.mine').length;
                    if (data.meta) { backlogHasMore = data.meta.more; }
                    if (!backlogHasMore) { feedStatus.removeClass('has-more'); }
                }
            }).fail(function () {
                feedStatus.addClass('error');
            }).always(function () {
                backlogXHR = false;
                feedStatus.removeClass('loading');
            });
        }
    };

    PYO.scrollForBacklog = function () {
        var scrolledToTop = function () {
            var top = false;
            if (PYO.feedPosts.scrollTop() <= 80) {
                top = true;
            }
            return top;
        };
        backlogHasMore = PYO.feedPosts.data('more');
        PYO.feedPosts.scroll(function () {
            $.doTimeout('scroll', 150, function () {
                if (scrolledToTop() && !backlogXHR && backlogHasMore) {
                    PYO.fetchBacklog();
                }
            });
        });
    };

    PYO.initializeFeed = function () {
        var posts = PYO.feed.find('.post');

        posts.find('.details').html5accordion();
        PYO.authorPosts = posts.filter('.mine').length;
        posts.filter('.unread').removeClass('unread');

        PYO.initializeMultiselect();
        PYO.watchForReadPosts();
        PYO.submitPost();
        PYO.characterCount('.village-main');
        PYO.scrollToBottom();
        PYO.scrollForBacklog();
    };

    return PYO;

}(PYO || {}, jQuery));
