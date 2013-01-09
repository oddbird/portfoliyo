(function ($) {

    'use strict';

    $(function () {
        Handlebars.registerPartial('group_list_item', Handlebars.templates.group_list_item);
        Handlebars.registerPartial('student_list_item', Handlebars.templates.student_list_item);
    });

}(jQuery));
