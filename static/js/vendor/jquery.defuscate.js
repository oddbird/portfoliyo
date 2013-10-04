/*! Defuscate - v0.1.1 - 2013-05-08
* https://github.com/jgerigmeyer/jquery-defuscate
* Copyright (c) 2013 Jonny Gerig Meyer; Licensed MIT */
(function (factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    } else {
        // Browser globals
        factory(jQuery);
    }
}(function ($) {

    var settings = {};

    var methods = {
        init: function (options) {
            settings = $.extend({}, $.fn.defuscate.defaults, options);
            return this.each(function () {
                var el, newHref, newHtml, is_link;
                el = $(this);
                is_link = false;
                if (el.is('a[href]')) {
                    is_link = true;
                    newHref = methods.defuscateHref(el.attr('href'));
                    methods.updateHref(el, newHref);
                }
                newHtml = methods.defuscateHtml(el.html(), is_link);
                methods.updateHtml(el, newHtml);
            });
        },
        defuscateHref: function (href) {
            return href.replace(settings.find, settings.replace);
        },
        defuscateHtml: function (html, is_link) {
            var find = settings.find;
            var replace = settings.replace;
            var replacedHTML;
            if (is_link) {
                replacedHTML = html.replace(find, replace);
            } else {
                replacedHTML = html.replace(find, '<a href="mailto:' + replace + '">' + replace + '</a>');
            }
            return replacedHTML;
        },
        updateHref: function (el, newHref) {
            el.attr('href', newHref);
            return el;
        },
        updateHtml: function (el, newHtml) {
            el.html(newHtml);
            return el;
        }
    };

    // Collection method.
    $.fn.defuscate = function (method) {
        // Method calling logic
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.tooltip');
        }
    };

    // Setup plugin defaults
    $.fn.defuscate.defaults = {
        find: /\b([A-Z0-9._%\-]+)\([^)]+\)((?:[A-Z0-9\-]+\.)+[A-Z]{2,6})\b/gi,
        replace: '$1@$2'
    };

    settings = $.extend({}, $.fn.defuscate.defaults);

}));