var PYO = (function (PYO, $) {

    'use strict';

    $(function () {
        // plugins
        $('input[placeholder], textarea[placeholder]').placeholder();
        $('#messages').messages({handleAjax: true});
        $('.email').defuscate();
        $('.formset.elders').formset({
            prefix: $('.formset.elders').data('prefix'),
            formTemplate: '#empty-elder-form',
            formSelector: '.fieldset.elder',
            addLink: '<a class="add-row" href="javascript:void(0)" title="more elders">more elders</a>',
            addAnimationSpeed: 'normal',
            removeAnimationSpeed: 'fast',
            optionalIfEmpty: true
        });

        // landing.js
        PYO.ajaxifyForm('.village-landing .membership form', '.village-landing .membership');

        // village.js
        PYO.updatePageHeight('.village');
        PYO.updateVillageScroll('.village-feed');
        PYO.addPost({
            author: 'Ms. Rooney',
            title: 'Principal',
            date: '8/16/2012',
            time: '9:07am',
            text: 'Ms. Burell, Allyson has been late to school for the last 4 days. We need to schedule a meeting to plan how she can get to school on time. Can you come at 4pm tomorrow after school?'
        }, '.pusher-test .village-feed');
        PYO.submitPost('.pusher-test');
    });

    return PYO;

}(PYO || {}, jQuery));
