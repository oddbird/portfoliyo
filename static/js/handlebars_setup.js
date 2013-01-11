(function ($) {

    'use strict';

    $(function () {
        Handlebars.registerPartial('group_list_item', Handlebars.templates.group_list_item);
        Handlebars.registerPartial('student_list_item', Handlebars.templates.student_list_item);

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

}(jQuery));
