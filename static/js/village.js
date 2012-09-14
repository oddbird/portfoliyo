var PYO = (function (PYO, $) {

    'use strict';

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

    PYO.updateVillageScroll = function (container) {
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
        if (post) { return post; }
    };

    PYO.addPost = function (data) {
        if (data) {
            var post = PYO.renderPost(data);
            $('.village-feed').append(post);
            PYO.updateVillageScroll('.village-feed');
        }
    };

    PYO.submitPost = function (container) {
        if ($(container).length) {
            var feed = $(container);
            var url = feed.data('post-url');
            var context = feed.closest('.village');
            var form = context.find('form.post-add-form');

            form.submit(function (event) {
                event.preventDefault();
                var postText = form.find('#post-text').val();
                var postData = { text: postText };
                $.post(url, postData, function (data) {
                    context.find('#post-text').val('');
                });
            });
        }
    };

    PYO.listenForPusherEvents = function (container) {
        if ($(container).length) {
            var feed = $(container);
            var pusherKey = feed.data('pusher-key');
            var pusher = new Pusher(pusherKey, {encrypted: true});
            var activeStudentId = feed.data('student-id');
            var students = $('.village-nav .student a');

            students.each(function () {
                var el = $(this);
                var id = el.data('id');
                var unread = el.find('.unread');
                var channel = pusher.subscribe('student_' + id);

                channel.bind('message_posted', function (data) {
                    if (id === activeStudentId) {
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

    return PYO;

}(PYO || {}, jQuery));
