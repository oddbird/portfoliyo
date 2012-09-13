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

    PYO.addPost = function (data, container) {
        if ($(container).length) {
            var context = $(container);
            var post;
            if (data) {
                post = PYO.renderPost(data);
            }
            if (post) {
                context.append(post);
            }
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

            form.submit(function(event) {
                event.preventDefault();
                var postData = createObj();
                if (postData) {
                    PYO.addPost(postData, '.pusher-test .village-feed');
                    context.find('#post-text').val('');
                }
            });
        }
    };

    return PYO;

}(PYO || {}, jQuery));
