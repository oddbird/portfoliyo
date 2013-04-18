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
            var posts = PYO.renderPost(data);
            posts.find('.details').html5accordion();
            PYO.feedPosts.append(posts);
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

    PYO.createPostObj = function (text, author_sequence, xhr_count, smsTargetArr, presentArr, attachmentsArr, type) {
        var author = PYO.feed.data('author');
        var role = PYO.feed.data('author-role');
        var today = new Date();
        var hour = today.getHours();
        var minute = today.getMinutes();
        minute = (minute < 10) ? '0' + minute : minute;
        var period = (hour > 12) ? 'pm' : 'am';
        hour = (hour > 12) ? hour - 12 : hour;
        var time = hour + ':' + minute + period;
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
                sms_recipients: smsTargetArr,
                type: {
                    name: type,
                    is_call: false,
                    is_meeting: false,
                    is_message: false,
                    is_note: false
                },
                present: presentArr,
                attachments: attachmentsArr
            }]
        };
        postObj.objects[0].type['is_' + type] = true;
        return postObj;
    };

    PYO.submitPost = function () {
        if (PYO.feed.length) {
            var context = PYO.feed.closest('.village');
            var forms = context.find('form.post-type');
            forms.each(function () {
                var form = $(this);
                var button = form.find('.action-post');
                var textarea = form.find('.post-textfield textarea');
                var formReset = function () {
                    form.find('.attach-value:disabled').removeAttr('disabled');
                    form.resetForm();
                    form.find('.attach-input label').click();
                    form.find('.tokens-list .token.new label').click();
                    textarea.focus().change();
                };

                form.submit(function (event) {
                    var fileInputs = form.find('.attach-value');
                    var attachments = fileInputs.filter(function () { return $(this).val() !== ''; });
                    if (!attachments.length || ($("<input type='file'/>").get(0).files !== undefined && window.FormData !== undefined)) {
                        event.preventDefault();
                        if (textarea.val().length || attachments.length || (form.hasClass('conversation-form') && form.find('.token-toggle:checked').length)) {
                            var text = $.trim(textarea.val());
                            var author_sequence_id = (PYO.authorPosts || 0) + 1;
                            var url = PYO.feed.data('post-url');
                            var count = ++postAjax.count;
                            var extraPostData = { author_sequence_id: author_sequence_id };
                            var type = form.find('input[name="type"]').fieldValue()[0];
                            var elderInputs = form.find('.token-toggle:checked');
                            var noInputs = form.find('.no-to-field');
                            var smsTargetArr = [];
                            var presentArr = [];
                            var attachmentsArr = [];
                            var postObj, post;

                            // Prevent notes without attachments from submitting as multipart/form-data
                            form.removeAttr('enctype');

                            if (elderInputs.length) {
                                elderInputs.each(function () {
                                    var el = $(this);
                                    var displayName;
                                    if (type === 'message') {
                                        displayName = el.data('display-name');
                                        smsTargetArr.push(displayName);
                                    } else if (type === 'call' || type === 'meeting') {
                                        displayName = el.hasClass('new') ? el.val() : el.data('display-name');
                                        presentArr.push(displayName);
                                    }
                                });
                            } else if (noInputs.length) {
                                var namesArr = noInputs.data('elders').split(',');
                                smsTargetArr = smsTargetArr.concat(namesArr);
                            }

                            if (attachments.length) {
                                attachments.each(function () {
                                    var el = $(this);
                                    var name;
                                    if (el.get(0).files && el.get(0).files.length && el.get(0).files[0].name) {
                                        name = el.get(0).files[0].name;
                                    } else {
                                        name = el.val().replace(/^.*\\/, '');
                                    }
                                    attachmentsArr.push({name: name});
                                });
                            }

                            postObj = PYO.createPostObj(text, author_sequence_id, count, smsTargetArr, presentArr, attachmentsArr, type);
                            post = PYO.addPost(postObj);
                            post.data('post-data', form.formSerialize());
                            fileInputs.filter(function () { return $(this).val() === ''; }).attr('disabled', true);

                            if (url) {
                                form.ajaxSubmit({
                                    url: url,
                                    data: extraPostData,
                                    dataType: 'json',
                                    success: function (response) {
                                        PYO.postAjaxSuccess(response, author_sequence_id, count);
                                    },
                                    error: function (request, status) {
                                        if (attachments.length) { post.data('attachments', true); }
                                        PYO.postAjaxError(post, author_sequence_id, status, count);
                                        postAjax.XHR[count] = null;
                                        form.removeData('jqxhr');
                                    }
                                });
                                postAjax.XHR[count] = form.data('jqxhr');
                                formReset();
                            }

                            PYO.scrollToBottom();
                            PYO.addPostTimeout(post, author_sequence_id, count);
                        }
                    } else {
                        form.attr('enctype', 'multipart/form-data');
                        form.loadingOverlay();
                        return true;
                    }
                });

                // Hijack ENTER to submit the form (instead of adding a newline)
                textarea.keydown(function (event) {
                    if (event.keyCode === PYO.keycodes.ENTER && !event.shiftKey) {
                        event.preventDefault();
                        if (!button.is(':disabled')) {
                            form.submit();
                        }
                    }
                });
            });
        }
    };

    PYO.postAjaxSuccess = function (response, old_author_sequence, xhr_count) {
        if (response && response.objects && response.objects.length) {
            $.each(response.objects, function () {
                PYO.feed.trigger('successful-post', {smsRecipients: this.sms_recipients.length, studentId: PYO.activeStudentId, groupId: PYO.activeGroupId});
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
            var msg = PYO.tpl('post_timeout_msg', { attachments: post.data('attachments') });
            msg.find('.resend').click(function (e) {
                e.preventDefault();
                PYO.resendPost(post);
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
        var count = ++postAjax.count;
        if (url) {
            var postData = post.data('post-data') + '&author_sequence_id=' + author_sequence_id;
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
            var form = context.find('form.message-form');
            var textarea = form.find('#message-text');
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

    PYO.initializeToField = function (containerSel, textareaSel, opts) {
        if ($(containerSel).length) {
            var container = $(containerSel);
            var defaults = {
                textbox: 'input.token-value',
                inputs: 'input.token-toggle',
                suggestionList: '.token-suggest',
                inputList: '.tokens-list',
                triggerSubmit: function (context) {
                    context.find(textareaSel).focus();
                },
                inputsNeverRemoved: true,
                inputType: 'elder',
                selectAll: '.bulk-tokens .add-all',
                selectNone: '.bulk-tokens .remove-all'
            };
            var options = $.extend({}, defaults, opts);

            container.customAutocomplete(options);

            container.on('click', '.tokens-input', function () {
                container.find('input.token-value').focus();
            });
        }
    };

    // Adding/removing attachments on notes
    PYO.initializeAttachments = function (formSel) {
        if ($(formSel).length) {
            var form = $(formSel);
            var counter = 0;
            var label = form.find('label.attach-type');
            var attachmentList = form.find('.attach-input');
            var inputList = form.find('.attach-field');
            var textarea = form.find('.post-textfield textarea');

            label.click(function (e) {
                e.preventDefault();
                var id = $(this).attr('for');
                form.find('#' + id).click();
            });

            form.on('change', 'input.attach-value', function () {
                var input = $(this);
                var inputID = input.attr('id');
                var token, newInput, filename;

                inputList.find('.attach-value').removeClass('ie-fix-active');

                if (input.get(0).files && input.get(0).files.length && input.get(0).files[0].name) {
                    filename = input.get(0).files[0].name;
                } else {
                    filename = input.val().replace(/^.*\\/, '');
                }

                token = PYO.tpl('autocomplete_input', {
                    newInput: true,
                    typeName: 'attachment-token',
                    index: counter++,
                    id: inputID,
                    inputText: filename
                });
                newInput = PYO.tpl('note_attachment_input', { index: counter });
                attachmentList.append(token);
                inputList.append(newInput);
                label.attr('for', 'attach-file-' + counter);
                textarea.focus();
            });

            attachmentList.on('change', '.token-toggle.new', function () {
                var input = $(this);
                if (input.prop('checked') === false) {
                    var inputID = input.val();
                    var token = input.closest('.token');

                    form.find('#' + inputID).remove();
                    token.remove();
                }
            });

            attachmentList.on('click', function (e) {
                if (e.target === this && !$('html').hasClass('ie9')) {
                    label.click();
                }
            });
        }
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

        PYO.watchForReadPosts();
        PYO.initializeToField('.post-add-form .message-form', '#message-text', {prefix: 'message'});
        PYO.initializeToField('.post-add-form .conversation-form', '#conversation-text', {
            allowNew: true,
            newInputName: 'extra_name',
            labelText: 'present',
            prefix: 'conversation'
        });
        PYO.initializeAttachments('.post-add-form .note-form');
        PYO.submitPost();
        PYO.characterCount('.village-main');
        PYO.scrollToBottom();
        PYO.scrollForBacklog();

        $('.post-add-form').resize(function () {
            PYO.updateContentHeight('.village-feed', '.feed-posts', true);
        });
    };

    return PYO;

}(PYO || {}, jQuery));
