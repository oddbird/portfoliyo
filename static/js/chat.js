var PYO = (function (PYO, $) {

    'use strict';

    var postAjax = {
        XHR: {},
        count: 0
    };
    var feedAjax = {
        XHR: null,
        count: 0
    };
    var smsDetailsOpened = function (trigger) {
        trigger.css('overflow', '');
        if (trigger.closest('.post').is(':last-child')) {
            PYO.scrollToBottom();
        }
    };

    PYO.scrollToBottom = function () {
        if ($('.village-feed').length) {
            var feed = $('.village-feed');
            var height = parseInt(feed.get(0).scrollHeight, 10);
            feed.scrollTop(height).scroll();
        }
    };

    PYO.scrolledToBottom = function () {
        var feed = $('.village-feed');
        var bottom = false;
        if (feed.length && feed.get(0).scrollHeight - feed.scrollTop() - feed.outerHeight() <= 50) {
            bottom = true;
        }
        return bottom;
    };

    PYO.updateFeedHeights = function () {
        var feed = $('.village-feed');
        var scroll = PYO.scrolledToBottom();
        if (feed.length) {
            var postAddForm = $('.village .post-add-form');
            if (postAddForm.length) {
                feed.css('bottom', postAddForm.outerHeight().toString() + 'px');
            }

            var instructions = feed.find('.instructions');
            var stickyhack = feed.find('.feed-posts .stickyhack');
            if (instructions.length && stickyhack.length) {
                var howToPost = instructions.find('.howto-post').css('margin-top', '');
                var howToSms = instructions.find('.howto-sms').css('margin-top', '');
                var diff;
                var updateInstructions = function () {
                    var instructionsHeight = instructions.outerHeight();
                    instructions.css('margin-top', '-' + instructionsHeight.toString() + 'px');
                    stickyhack.css('height', instructionsHeight.toString() + 'px');
                    if (howToSms.outerHeight() > howToPost.outerHeight()) {
                        diff = howToSms.outerHeight() - howToPost.outerHeight();
                        howToPost.css('margin-top', diff.toString() + 'px');
                    } else if (howToPost.outerHeight() > howToSms.outerHeight()) {
                        diff = howToPost.outerHeight() > howToSms.outerHeight();
                        howToSms.css('margin-top', diff.toString() + 'px');
                    }
                };
                updateInstructions();
            }

            if (scroll) { PYO.scrollToBottom(); }
        }
    };

    PYO.renderPost = function (data) {
        var posts;
        if (data && data.posts && data.posts.length) {
            $.each(data.posts, function () {
                this.plural_sms = '';
                this.sms_recipients = false;
                if (this.meta && this.meta.sms && this.meta.sms.length) {
                    var recipients = [];

                    $.each(this.meta.sms, function () {
                        if ($.inArray(this.display, recipients) === -1) {
                            recipients.push(this.display);
                        }
                    });

                    this.sms_recipients = recipients.join(', ');
                    if (recipients.length > 1) { this.plural_sms = 's'; }
                }
            });
            posts = PYO.tpl('post', data);
        }
        if (posts) {
            var nametag = posts.find('.nametag');
            nametag.each(function () {
                var thisTag = $(this);
                var userID = thisTag.data('user-id');
                if (userID) {
                    var mentions = userID.toString().split(',');
                    if ($.inArray(PYO.activeUserId.toString(), mentions) !== -1) {
                        thisTag.addClass('me');
                    }
                }
            });
            posts.filter('.post[data-author-id="' + PYO.activeUserId + '"]').addClass('mine').removeClass('unread');
            return posts;
        }
    };

    PYO.addPost = function (data) {
        if (data) {
            var feedPosts = $('.village-feed .feed-posts');
            var stickyhack = feedPosts.find('.stickyhack');
            var posts = PYO.renderPost(data);
            posts.find('.details').html5accordion({
                initialSlideSpeed: 0,
                openCallback: smsDetailsOpened
            });
            if (stickyhack.length) { stickyhack.before(posts); }
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
            newPost.filter('.post.mine').removeClass('old unread').each(function () {
                $(this).find('.details').addClass('open auto');
            });
            newPost.find('.details').html5accordion({
                initialSlideSpeed: 0,
                openCallback: smsDetailsOpened
            });
            oldPost.loadingOverlay('remove');
            oldPost.replaceWith(newPost);
            $.doTimeout('new-post-' + newPostData.author_sequence_id);
            if (scroll) { PYO.scrollToBottom(); }
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
        var text = $.trim(textarea.val());
        var postObj = {
            posts: [
                {
                    author: author,
                    author_id: PYO.activeUserId,
                    role: role,
                    date: date,
                    time: time,
                    text: text,
                    author_sequence_id: author_sequence,
                    xhr_count: xhr_count,
                    local: true
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
                    var postObj = PYO.createPostObj(author_sequence_id, count);
                    var post = PYO.addPost(postObj);
                    var postData = [
                        { name: 'text', value: text },
                        { name: 'author_sequence_id', value: author_sequence_id }
                    ];
                    var smsInputName = $('#sms-target').attr('name');

                    form.find('.sms-targeting .ui-multiselect-checkboxes input:checked').each(function () {
                        var obj = { name: smsInputName, value: $(this).val() };
                        postData.push(obj);
                    });

                    if (url) {
                        postAjax.XHR[count] = $.post(url, postData, function (response) {
                            PYO.postAjaxSuccess(response, author_sequence_id, count);
                        }).error(function (request, status, error) {
                            PYO.postAjaxError(post, author_sequence_id, status, count);
                            postAjax.XHR[count] = null;
                        });
                    }

                    textarea.val('').change();
                    feed.find('.post.mine .details.open.auto').removeClass('open').prop('open', false).find('.details-body').hide();
                    feed.find('.post .details.auto').removeClass('auto');
                    feed.find('.instructions').remove();
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
                feed.trigger('successful-post', {smsRecipients: this.meta.sms.length, studentId: PYO.activeStudentId, groupId: PYO.activeGroupId});
                if (this.author_sequence_id) {
                    var oldPost = feed.find('.post.mine.local[data-author-sequence="' + this.author_sequence_id + '"]');
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
            }).error(function (request, status, error) {
                PYO.postAjaxError(post, author_sequence_id, status, count);
                postAjax.XHR[count] = null;
            });
        }

        post.find('.timeout').remove();
        post.loadingOverlay();
        PYO.addPostTimeout(post, author_sequence_id, count);
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
                        if (response && response.posts && response.posts.length && feedAjax.count === count) {
                            PYO.addPost(response);
                            feed.find('.post.unread').removeClass('unread');
                            PYO.updateFeedHeights();
                            PYO.scrollToBottom();
                        }
                        feedAjax.XHR = null;
                    }).error(function (request, status, error) {
                        if (status !== 'abort') {
                            var msg = PYO.tpl('ajax_error_msg', {
                                error_class: 'feed-error',
                                message: 'Unable to load prior posts in this village.'
                            });
                            msg.find('.try-again').click(function (e) {
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
            $('.village-elders .elder .action-sms[data-name="' + PYO.directSmsName + '"]').click();
            PYO.directSmsName = '';
        }
    };

    PYO.initializeSmsDirectLinks = function () {
        $('body').on('click', '.village-elders .elder .action-sms', function (e) {
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
                $('.village-nav .listitem-select.ajax-link.active').click();
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
        $('.village-feed').scroll(function () {
            $.doTimeout('scroll', 150, function () {
                if (PYO.scrolledToBottom()) {
                    PYO.markPostsRead();
                }
            });
        });
    };

    return PYO;

}(PYO || {}, jQuery));
