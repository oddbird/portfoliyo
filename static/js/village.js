var PYO = (function (PYO, $) {

    'use strict';

    PYO.activeStudentId = $('.village-feed').data('student-id');
    PYO.activeUserId = $('.village-feed').data('user-id');

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
            return post;
        }
    };

    PYO.addPost = function (data) {
        if (data) {
            var post = PYO.renderPost(data);
            $('.village-feed').append(post);
            PYO.scrollToBottom('.village-feed');
        }
    };

    PYO.submitPost = function (container) {
        if ($(container).length) {
            var feed = $(container);
            var context = feed.closest('.village');
            var form = context.find('form.post-add-form');

            form.ajaxForm(function () {
                context.find('#post-text').val('').change();
            });
        }
    };

    PYO.listenForPusherEvents = function (container) {
        if ($(container).length) {
            var feed = $(container);
            var pusherKey = feed.data('pusher-key');
            var pusher = new Pusher(pusherKey, {encrypted: true});
            var students = $('.village-nav .student a');

            students.each(function () {
                var el = $(this);
                var id = el.data('id');
                var unread = el.find('.unread');
                var channel = pusher.subscribe('student_' + id);

                channel.bind('message_posted', function (data) {
                    if (id === PYO.activeStudentId) {
                        PYO.addPost(data);
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
            var feed = $(container);
            var textarea = feed.find('#post-text');
            var count = feed.find('.charcount');
            var button = feed.find('.action-post');
            var updateCount = function () {
                var chars = textarea.val().length;
                var remain = 160 - chars;
                if (remain < 0) {
                    count.addClass('overlimit');
                    button.attr('disabled', 'disabled');
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
