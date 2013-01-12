/*global module:false*/
module.exports = function (grunt) {

    'use strict';

    var SRC_JS_TEMPLATES = 'jstemplates/';
    var DEST_JS_TEMPLATES = 'static/js/';

    // Project configuration.
    grunt.initConfig({
        shell: {
            handlebars_compile: {
                command: 'node_modules/.bin/handlebars ' + SRC_JS_TEMPLATES + ' -f ' + DEST_JS_TEMPLATES + 'jstemplates.js -k each -k if -k unless',
                stdout: true
            }
        },
        watch: {
            jstemplates: {
                files: SRC_JS_TEMPLATES + '*.handlebars',
                tasks: ['handlebars-compile']
            }
        }
    });

    // aliases for shell tasks
    grunt.registerTask('handlebars-compile', 'shell:handlebars_compile');

    // Default task
    grunt.registerTask('default', ['handlebars-compile']);

    // Plugin tasks
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-shell');
};
