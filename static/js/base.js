var PYO = (function (PYO, $) {

    'use strict';

    var pageAjax = {
        XHR: null,
        count: 0
    };

    // Store keycode variables for easier readability
    PYO.keycodes = {
        SPACE: 32,
        ENTER: 13,
        TAB: 9,
        ESC: 27,
        BACKSPACE: 8,
        SHIFT: 16,
        CTRL: 17,
        ALT: 18,
        CAPS: 20,
        LEFT: 37,
        UP: 38,
        RIGHT: 39,
        DOWN: 40
    };

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
            var height = parseInt(context.get(0).scrollHeight, 10);
            context.scrollTop(height);
        }
    };

    PYO.scrolledToBottom = function (container) {
        var context = $(container);
        var bottom = false;
        if (context.get(0).scrollHeight - context.scrollTop() - context.outerHeight() <= 50) {
            bottom = true;
        }
        return bottom;
    };

    PYO.pageAjaxError = function (url) {
        var container = $('.village-content');
        var msg = ich.pjax_error_msg();
        msg.find('.reload-pjax').click(function (e) {
            e.preventDefault();
            msg.remove();
            PYO.pageAjaxLoad(url);
        });
        container.loadingOverlay('remove');
        container.html(msg);
    };

    PYO.pageAjaxLoad = function (url) {
        if (pageAjax.XHR) { pageAjax.XHR.abort(); }

        var container = $('.village-content');
        var count = ++pageAjax.count;

        if (url) {
            container.loadingOverlay();
            container.find('.feed-error, .pjax-error').remove();

            pageAjax.XHR = $.get(url, function (response) {
                if (response && response.html && pageAjax.count === count) {
                    container.replaceWith($(response.html));
                    PYO.initializePage();
                }
                container.loadingOverlay('remove');
                pageAjax.XHR = null;
            }).error(function (request, status, error) {
                if (status !== 'abort') {
                    PYO.pageAjaxError(url);
                }
                pageAjax.XHR = null;
            });
        }
    };

    PYO.ajaxifyVillages = function (container) {
        if ($(container).length) {
            var context = $(container);
            var History = window.History;

            if (History.enabled) {
                $('body').on('click', 'a.ajax-link', function (e) {
                    if (e.which === 2 || e.metaKey) {
                        return true;
                    } else {
                        e.preventDefault();
                        var url = $(this).attr('href');
                        var stateData = History.getState().data;
                        var currentUrl = stateData.url ? stateData.url : window.location.pathname;
                        if (url === currentUrl) {
                            PYO.pageAjaxLoad(url + '?ajax=true');
                        } else {
                            var title = document.title;
                            var data = { url: url };
                            if ($(this).hasClass('addelder-link') || $(this).hasClass('edit-elder')) {
                                data.remainActive = true;
                            }
                            History.pushState(data, title, url);
                        }
                        $(this).blur();
                    }
                });

                $(window).bind('statechange', function () {
                    context.trigger('pjax-load');
                    var data = History.getState().data;
                    var url = data.url ? data.url : window.location.pathname;
                    if (!data.remainActive) {
                        context.find('.village-nav .ajax-link').removeClass('active');
                    }
                    context.find('a.ajax-link[href="' + url + '"]').addClass('active');
                    PYO.pageAjaxLoad(url + '?ajax=true');
                });
            }
        }
    };

    PYO.initializeEldersForm = function () {
        $('.formset.elders').formset({
            prefix: $('.formset.elders').data('prefix'),
            formTemplate: '#empty-elder-form',
            formSelector: '.fieldset.elder',
            addLink: '<a class="add-row" href="javascript:void(0)" title="more elders">more elders</a>',
            addAnimationSpeed: 'normal',
            removeAnimationSpeed: 'fast',
            optionalIfEmpty: true
        });
        if ($('#id_name').length) {
            $('#id_name').focus();
        } else {
            $('#id_elders-0-contact').focus();
        }
    };

    PYO.initializeFeed = function () {
        PYO.activeStudentId = $('.village-feed').data('student-id');
        PYO.activeUserId = $('.village-feed').data('user-id');
        PYO.fetchBacklog('.village-feed');
        PYO.submitPost('.village-feed');
        PYO.characterCount('.village-main');
    };

    PYO.initializePage = function () {
        if ($('.village-feed').length) {
            PYO.initializeFeed();
        }
        if ($('.formset.elders').length) {
            PYO.initializeEldersForm();
        }
    };

    return PYO;

}(PYO || {}, jQuery));
