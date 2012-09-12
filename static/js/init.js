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
            addLink: '<a class="pluselder" href="javascript:void(0)">more elders</a>',
            addAnimationSpeed: 'normal',
            removeAnimationSpeed: 'fast'
        });

        // local.js
        PYO.ajaxifyForm('.village-landing .membership form', '.village-landing .membership');
        PYO.updatePageHeight('.village');
        PYO.updateVillageScroll('.village-feed');
    });

    return PYO;

}(PYO || {}, jQuery));
