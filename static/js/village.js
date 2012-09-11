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
        if (data) {
            var post = ich.post(data);
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

    return PYO;

}(PYO || {}, jQuery));
