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

    PYO.pageAjaxError = function (url) {
        var container = $('.village-content');
        var msg = ich.ajax_error_msg({
            error_class: 'pjax-error',
            message: 'Unable to load the requested page.'
        });
        msg.find('.try-again').click(function (e) {
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
                    var newPage = $(response.html);
                    container.replaceWith(newPage);
                    newPage.find('.details').html5accordion();
                    newPage.find('input[placeholder], textarea[placeholder]').placeholder();
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
                            var query = url.toString().indexOf('?') !== -1 ? '&' : '?';
                            PYO.pageAjaxLoad(url + query + 'ajax=true');
                        } else {
                            var title = document.title;
                            var data = { url: url };
                            History.pushState(data, title, url);
                        }
                        $(this).blur();
                    }
                });

                $(window).bind('statechange', function () {
                    var data = History.getState().data;
                    var url = data.url ? data.url : window.location.pathname;
                    var query = url.toString().indexOf('?') !== -1 ? '&' : '?';
                    PYO.pageAjaxLoad(url + query + 'ajax=true');
                });
            }
        }
    };

    PYO.detectFlashSupport = function (container) {
        if ($(container).length) {
            if (Pusher && Pusher.TransportType !== 'native' && FlashDetect && !FlashDetect.versionAtLeast(10)) {
                ich.flash_warning_msg().appendTo('#messages');
                $('#messages').messages();
            }
        }
    };

    PYO.disablePreselectedAssociations = function (container) {
        var form = $(container);
        var inputs = form.find('.relation-fieldset .check-options input:checked');

        inputs.attr('disabled', 'disabled').each(function () {
            var el = $(this);
            var label = $(this).siblings('.type');
            if (el.closest('form').hasClass('village-add-form')) {
                label.attr('title', 'this is the group to which you are adding this student');
            } else if (el.closest('form').hasClass('elder-add-form')) {
                var type = el.attr('name').substring(0, el.attr('name').toString().length - 1);
                label.attr('title', 'this is the ' + type + ' you are inviting this elder to join');
            }
        });
        form.submit(function () { inputs.removeAttr('disabled'); });
    };

    PYO.addGroupAssociationColors = function (container) {
        if ($(container).length) {
            var form = $(container);
            var groupInputs = form.find('.check-options input[name="groups"]');
            var inputs = form.find('.check-options input').not(groupInputs);
            var count = 0;
            var updateColors = function () {
                groupInputs.each(function () {
                    var el = $(this);
                    var label = el.siblings('.type');
                    if (el.is(':checked')) {
                        if (label.data('color')) {
                            label.addClass(label.data('color'));
                        } else {
                            count = count === 18 ? 1 : count + 1;
                            label.addClass('label-color-' + count);
                            label.data('color', 'label-color-' + count);
                        }
                    } else if (label.data('color')) {
                        label.removeClass(label.data('color'));
                    }
                });
            };

            groupInputs.change(function () {
                updateColors();
            });

            updateColors();
        }
    };

    PYO.initializeFeed = function () {
        PYO.activeUserId = $('.village-feed').data('user-id');
        PYO.fetchBacklog('.village-feed');
        PYO.submitPost('.village-feed');
        PYO.characterCount('.village-main');
    };

    PYO.initializePusher = function () {
        PYO.pusherKey = $('.village').data('pusher-key');
        if (PYO.pusherKey) { PYO.pusher = new Pusher(PYO.pusherKey, {encrypted: true}); }
    };

    PYO.initializePage = function () {
        PYO.activeStudentId = $('.village-content').data('student-id');
        PYO.activeGroupId = $('.village-content').data('group-id');
        PYO.updateNavActiveClasses();
        PYO.addGroupAssociationColors('.relation-fieldset');
        if ($('#invite-elders-form').length) { PYO.disablePreselectedAssociations('#invite-elders-form'); }
        if ($('#add-student-form').length) { PYO.disablePreselectedAssociations('#add-student-form'); }
        if ($('.village-feed').length) { PYO.initializeFeed(); }
    };

    return PYO;

}(PYO || {}, jQuery));
