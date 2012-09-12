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
            optionalUntilFocus: true
        });

        // local.js
        PYO.ajaxifyForm('.village-landing .membership form', '.village-landing .membership');
        PYO.updatePageHeight('.village');
        PYO.updateVillageScroll('.village-feed');
    });

    return PYO;

}(PYO || {}, jQuery));
