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
            var context = $(container);
            var form = context.find('form.post-add-form');
            var createObj = function () {
                var text = context.find('#post-text').val();
                var author = 'Test User';
                var title = 'Developer';
                var today = new Date();
                var dd = today.getDate();
                var mm = today.getMonth() + 1;
                var yyyy = today.getFullYear();
                var date = mm + '/' + dd + '/' + yyyy;
                var hours = today.getHours();
                var minute = today.getMinutes();
                var period = (hours > 12) ? 'PM' : 'AM';
                hours = (hours > 12) ? hours - 12 : hours;
                var time = hours + ":" + minute + " " + period;
                var data = {
                    author: author,
                    title: title,
                    date: date,
                    time: time,
                    text: text
                };
                return data;
            };

            form.submit(function (event) {
                event.preventDefault();
                var postData = createObj();
                if (postData) {
                    PYO.addPost(postData);
                    context.find('#post-text').val('');
                }
            });
        }
    };

    PYO.listenForPusherEvents = function (container) {
        var context = $(container);
        var feed = context.find('.village-feed');
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
    };

    PYO.fetchBacklog = function (container) {
        var context = $(container);
        var feed = context.find('.village-feed');
        var url = feed.data('backlog-url');
        $.get(url, function (data) {
            PYO.addPost(data);
        });
    };

    return PYO;

}(PYO || {}, jQuery));
