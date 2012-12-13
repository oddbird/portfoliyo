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

    PYO.ieInputBootstrap = function (input) {
        if (input.is(':checked')) {
            input.attr('aria-checked', true);
        } else {
            input.removeAttr('aria-checked');
        }
    };

    PYO.ieInputBootstrapHandler = function () {
        $('body').on('change', 'input:radio, input:checkbox', function () {
            var el = $(this);

            if (el.is(':radio')) {
                var form = el.closest('form');
                var name = el.attr('name');
                form.find('input:radio[name="' + name + '"]').each(function () {
                    PYO.ieInputBootstrap($(this));
                });
            } else {
                PYO.ieInputBootstrap(el);
            }
        });
    };

    PYO.updatePageHeight = function (container) {
        if ($(container).length) {
            var page = $(container);
            var headerHeight = $('div[role="banner"]').outerHeight();
            var footerHeight = $('footer').outerHeight();
            var pageHeight, transition;
            var updateHeight = function (animate) {
                var scroll = PYO.scrolledToBottom();
                pageHeight = $(window).height() - headerHeight - footerHeight;
                if (animate) {
                    page.css('height', pageHeight.toString() + 'px');
                    if (scroll) {
                        $.doTimeout('page_height_scroll', 250, function () {
                            PYO.scrollToBottom();
                        });
                    }
                } else {
                    transition = page.css('transition');
                    page.css({
                        'transition': 'none',
                        'height': pageHeight.toString() + 'px'
                    });
                    $(window).load(function () {
                        page.css('transition', transition);
                    });
                    if (scroll) { PYO.scrollToBottom(); }
                }
            };
            updateHeight();

            $(window).resize(function () {
                $.doTimeout('resize', 250, function () {
                    updateHeight(true);
                    PYO.updateFeedHeights();
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
                $('body').on('click', '.ajax-link', function (e) {
                    var el = $(this);
                    if (e.which === 2 || e.metaKey) {
                        return true;
                    } else {
                        e.preventDefault();
                        var url = el.attr('href');
                        var stateData = History.getState().data;
                        var currentUrl = stateData.url ? stateData.url : window.location.pathname;
                        if (url === currentUrl) {
                            var query = url.toString().indexOf('?') !== -1 ? '&' : '?';
                            PYO.pageAjaxLoad(url + query + 'ajax=true');
                        } else {
                            var title = document.title;
                            var data = { url: url };
                            History.pushState(data, title, url);
                            if (!el.hasClass('active') && (!el.hasClass('group-link') || el.closest('.listitem').hasClass('grouptitle'))) {
                                if (el.parents('.village-nav').length) {
                                    $('.village-nav .ajax-link.listitem-select').removeClass('active');
                                    el.closest('.listitem').find('.ajax-link.listitem-select').addClass('active');
                                } else {
                                    el.addClass('active');
                                }
                            }
                        }
                        if (el.parent().hasClass('student')) {
                            el.find('.unread').addClass('zero').text('0');
                        }
                        el.blur();
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
        var checked = form.find('.relation-fieldset .check-options input.initial');

        checked.attr('disabled', 'disabled').addClass('disabled locked').each(function () {
            var el = $(this);
            var label = el.siblings('.type');
            var title;
            if (el.closest('form').hasClass('village-add-form')) {
                title = 'You are adding a student to the "' + $.trim(label.text()) + '" group.';
                label.attr('title', title).data('title', title);
            } else if (el.closest('form').is('#invite-teacher-form')) {
                if (el.closest('.check-options').hasClass('select-groups')) {
                    title = 'You are inviting a teacher to join all the student villages in the "' + $.trim(label.text()) + '" group.';
                    label.attr('title', title).data('title', title);
                }
                if (el.closest('.check-options').hasClass('select-students')) {
                    title = "You are inviting a teacher to join " + $.trim(label.text()) + "'s village.";
                    label.attr('title', title).data('title', title);
                }
            }
        });
    };

    PYO.disableStudentOwnerRemoval = function (container) {
        var form = $(container);
        var inputs = form.find('.relation-fieldset .check-options input.owner');

        inputs.attr('disabled', 'disabled').addClass('disabled locked').each(function () {
            var el = $(this);
            var label = el.siblings('label.type');
            var title = 'You cannot remove the teacher who invited this student.';
            label.attr('title', title).data('title', title);
        });
    };

    PYO.addGroupAssociationColors = function (container) {
        if ($(container).length) {
            var context = $(container);
            var form = context.closest('form');
            var groupInputs = context.find('.check-options input[name="groups"]');
            var inputs = context.find('.check-options input').not(groupInputs);
            var count = 0;
            var selectedIds = [];
            var updateColors = function () {
                var colorInputs = function (i) {
                    var id = selectedIds[i];
                    var group = groupInputs.filter('[value=' + id + ']');
                    var groupLabel = group.siblings('.type');
                    var groupName = $.trim(groupLabel.text());
                    var thisCount = groupLabel.data('color-count');
                    var relInputs = inputs.filter(function () {
                        var groups = $(this).data('group-ids');
                        return $.inArray(id, groups) !== -1;
                    });
                    relInputs.each(function () {
                        var el = $(this);
                        if (!el.data('colored')) {
                            el.data('colored', true).attr('disabled', 'disabled').addClass('disabled');
                            el.siblings('.type').addClass('group-selected-' + thisCount).attr('title', 'selected as part of "' + groupName + '" group');
                        }
                    });
                };

                inputs.each(function () {
                    var el = $(this).removeData('colored');
                    var label = el.siblings('.type');
                    var classes = label.attr('class').split(' ');
                    for (var i = 0; i < classes.length; i++) {
                        if (classes[i].indexOf('group-selected-') !== -1) { label.removeClass(classes[i]); }
                    }
                    if (el.hasClass('locked')) {
                        label.attr('title', label.data('title'));
                    } else {
                        el.removeAttr('disabled').removeClass('disabled');
                        label.removeAttr('title');
                    }
                });

                if (selectedIds && selectedIds.length) {
                    for (var i = 0; i < selectedIds.length; i++) {
                        colorInputs(i);
                    }
                }
            };

            groupInputs.change(function () {
                var el = $(this);
                var label = el.siblings('.type');
                var id = parseInt(el.val(), 10);
                var thisCount;
                if (el.is(':checked')) {
                    if ($.inArray(id, selectedIds) === -1) { selectedIds.unshift(id); }
                    if (label.data('color-count')) {
                        thisCount = label.data('color-count');
                    } else {
                        count = count === 18 ? 1 : count + 1;
                        thisCount = count;
                        label.data('color-count', thisCount);
                    }
                    label.addClass('label-color-' + thisCount);
                } else {
                    if ($.inArray(id, selectedIds) !== -1) { selectedIds.splice($.inArray(id, selectedIds), 1); }
                    if (label.data('color-count')) {
                        thisCount = label.data('color-count');
                        label.removeClass('label-color-' + thisCount);
                    }
                }
                updateColors();
            });

            groupInputs.filter(':checked').each(function () { $(this).change(); });
            form.submit(function () { inputs.add(groupInputs).removeAttr('disabled'); });
        }
    };

    PYO.setAddGroupButtonText = function (container) {
        var form = $(container);
        var button = form.find('.form-actions .action-post');
        var defaultText = $.trim(button.text());
        var students = form.find('.relation-fieldset .select-students input[name="students"]');
        var steps = form.find('.form-steps');

        students.change(function () {
            if (students.filter(':checked').length) {
                if (!button.data('group')) {
                    button.data('group', true).fadeOut('fast', function () {
                        button.text('Create Group').fadeIn('fast');
                    });
                    steps.slideUp();
                }
            } else {
                if (button.data('group')) {
                    button.data('group', false).fadeOut('fast', function () {
                        button.text(defaultText).fadeIn('fast');
                    });
                    steps.slideDown();
                }
            }
        });
    };

    PYO.addStudentReplaceNameInInvitation = function (container) {
        var form = $(container);
        if (form.length) {
            var input = form.find('#id_name');
            var toReplace = form.find('.replace-student-name');
            var update = function () {
                toReplace.text(input.val() || '[student]');
            };

            // handle form reloads with prefilled form data
            update();

            input.keyup(update);
        }
    };

    PYO.setPhoneChangedClass = function (container) {
        var form = $(container);
        var input = form.find('#id_phone');
        var formfield = form.find('.formfield.phone-field');
        var orig = input.val();

        input.blur(function () {
            var newPhone = $(this).val();
            if (newPhone !== orig) {
                formfield.addClass('changed');
            } else {
                formfield.removeClass('changed');
            }
        });
    };

    PYO.formFocus = function () {
        if ($('#invite-teacher-form').length) {
            $('#id_email').focus();
        }
        if ($('#invite-family-form').length) {
            $('#id_phone').focus();
        }
        if ($('#add-student-form').length) {
            $('#id_name').focus();
        }
        if ($('#add-group-form').length) {
            $('#id_name').focus();
        }
    };

    PYO.announcements = function (container) {
        if ($(container).length) {
            var context = $(container);
            context.on('click', '.close', function (e) {
                e.preventDefault();
                var msg = $(this).closest('.announce');
                var url = msg.data('mark-read-url');

                msg.fadeOut(function () { $(this).remove(); });
                if (url) { $.post(url); }
            });
        }
    };

    PYO.initializeFeed = function () {
        PYO.activeUserId = $('.village-feed').data('user-id');
        PYO.watchForReadPosts();
        PYO.fetchBacklog('.village-feed');
        PYO.submitPost('.village-feed');
        PYO.characterCount('.village-main');
        PYO.initializeMultiselect();
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
        PYO.addStudentReplaceNameInInvitation('#add-student-form');
        if ($('#invite-teacher-form').length) { PYO.disablePreselectedAssociations('#invite-teacher-form'); }
        if ($('#add-student-form').length) { PYO.disablePreselectedAssociations('#add-student-form'); }
        if ($('#edit-student-form').length) { PYO.disableStudentOwnerRemoval('#edit-student-form'); }
        if ($('#add-group-form').length) { PYO.setAddGroupButtonText('#add-group-form'); }
        if ($('#edit-elder-form').length) { PYO.setPhoneChangedClass('#edit-elder-form'); }
        if ($('.village-feed').length) { PYO.initializeFeed(); }
        PYO.formFocus();
        $('body').find('input:radio, input:checkbox').each(function () {
            PYO.ieInputBootstrap($(this));
        });
    };

    return PYO;

}(PYO || {}, jQuery));
