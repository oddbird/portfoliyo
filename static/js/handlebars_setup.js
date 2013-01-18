var PYO = (function (PYO, $) {

    'use strict';

    PYO.tpl = function (template, data) {
        return $($.parseHTML(Handlebars.templates[template](data))).filter('*');
    };

    $(function () {
        Handlebars.registerPartial('group_list_items', Handlebars.templates.group_list_items);
        Handlebars.registerPartial('student_list_items', Handlebars.templates.student_list_items);

        // Handlebars.registerHelper('debug', function(optionalValue) {
        //     console.log('Current Context');
        //     console.log('====================');
        //     console.log(this);

        //     if (optionalValue) {
        //         console.log('Value');
        //         console.log('====================');
        //         console.log(optionalValue);
        //     }
        // });
    });

    return PYO;

}(PYO || {}, jQuery));
