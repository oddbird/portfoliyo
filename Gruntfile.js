/*global module:false*/
module.exports = function (grunt) {

    'use strict';

    // Project configuration.
    grunt.initConfig({
        vars: {
            src_js_templates_dir: 'jstemplates/',
            dest_js_templates_dir: 'static/js/',
            src_js_dir: 'static/js/',
            dest_js_templates: 'jstemplates.js',
            src_js_templates: '*.handlebars',
            src_js: '*.js'
        },
        pkg: grunt.file.readJSON('package.json'),
        handlebars: {
            compile: {
                options: {
                    namespace: 'PYO.templates',
                    wrapped: true,
                    processName: function (filename) {
                        var pieces = filename.split('/');
                        var name = pieces[pieces.length - 1].split('.');
                        return name[name.length - 2];
                    }
                },
                files: [{
                    src: '<%= vars.src_js_templates_dir %><%= vars.src_js_templates %>',
                    dest: '<%= vars.dest_js_templates_dir %><%= vars.dest_js_templates %>'
                }]
            }
        },
        jshint: {
            options: {
                jshintrc: '.jshintrc'
            },
            gruntfile: ['Gruntfile.js'],
            js: ['<%= vars.src_js_dir %><%= vars.src_js %>', '!<%= vars.dest_js_templates_dir %><%= vars.dest_js_templates %>']
        },
        watch: {
            jstemplates: {
                files: '<%= vars.src_js_templates_dir %><%= vars.src_js_templates %>',
                tasks: ['handlebars']
            },
            gruntfile: {
                files: '<%= jshint.gruntfile %>',
                tasks: ['jshint:gruntfile']
            },
            js: {
                files: '<%= jshint.js %>',
                tasks: ['jshint:js']
            }
        }
    });

    // Default task
    grunt.registerTask('default', ['handlebars']);

    // Plugin tasks
    grunt.loadNpmTasks('grunt-contrib-handlebars');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-watch');
};
