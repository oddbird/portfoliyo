var PYO = (function (PYO, $) {

    'use strict';

    PYO.tpl = function (template, data) {
        // This will remove any top-level text nodes from rendered templates.
        // ...see http://bugs.jquery.com/ticket/12462 and https://github.com/wycats/handlebars.js/issues/162
        return $($.parseHTML(PYO.templates[template](data))).filter('*');
    };

    $(function () {
        Handlebars.registerPartial('group_list_items', PYO.templates.group_list_items);
        Handlebars.registerPartial('student_list_items', PYO.templates.student_list_items);

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

        Handlebars.registerHelper('comma_list', function (context, options) {
            var ret = "";
            for (var i = 0, j = context.length; i < j; i++) {
                ret = ret + options.fn(context[i]);
                if (i < j - 1) {
                    ret = ret + ", ";
                }
            }
            return ret;
        });

        Handlebars.registerHelper('plural', function (context, options) {
            if (context.length > 1) {
                return options.fn(this);
            }
            return options.inverse(this);
        });
    });

    return PYO;

}(PYO || {}, jQuery));
