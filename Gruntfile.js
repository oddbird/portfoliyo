/*global module:false*/
module.exports = function (grunt) {

    'use strict';

    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        vars: {
            src_py_dir: 'portfoliyo/',
            py_tests_dir: 'portfoliyo/tests/',
            src_templates_dir: 'templates/',
            src_js_dir: 'static/js/',
            src_js_templates: 'jstemplates/*.hbs',
            dest_js_templates: '<%= vars.src_js_dir %>app/jstemplates.js',
            fonts_dir: 'static/fonts/',
            images_dir: 'static/images/',
            sass_dir: 'sass/'
        },
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
                    src: '<%= vars.src_js_templates %>',
                    dest: '<%= vars.dest_js_templates %>'
                }]
            }
        },
        jshint: {
            options: {
                jshintrc: '.jshintrc'
            },
            gruntfile: {
                src: ['Gruntfile.js']
            },
            src: {
                src: [
                    '<%= vars.src_js_dir %>*.js',
                    '<%= vars.src_js_dir %>app/**/*.js',
                    '!<%= vars.dest_js_templates %>'
                ]
            }
        },
        compass: {
            dev: {
                options: {
                    bundleExec: true,
                    config: 'config.rb'
                }
            }
        },
        shell: {
            pytest: {
                command: 'py.test',
                options: {
                    stdout: true,
                    failOnError: true
                }
            }
        },
        concurrent: {
            compile: ['newer:jshint', 'any-newer:handlebars', 'compass']
        },
        watch: {
            gruntfile: {
                files: ['<%= jshint.gruntfile.src %>'],
                tasks: ['default']
            },
            pytest: {
                files: [
                    '<%= vars.src_py_dir %>**/*.py',
                    '<%= vars.py_tests_dir %>**/*.py',
                    '<%= vars.src_templates_dir %>**/*.html'
                ],
                tasks: ['pytest']
            },
            js: {
                files: ['<%= vars.src_js_dir %>**/*.js', '!<%= vars.dest_js_templates %>'],
                tasks: ['newer:jshint:src']
            },
            jstemplates: {
                files: ['<%= vars.src_js_templates %>'],
                tasks: ['any-newer:handlebars']
            },
            css: {
                files: ['<%= vars.sass_dir %>**/*.scss', '<%= vars.fonts_dir %>**/*', '<%= vars.images_dir %>**/*'],
                tasks: ['compass']
            }
        }
    });

    // Default task
    grunt.registerTask('default', ['concurrent:compile', 'pytest']);

    // Run default tasks and watch for changes
    grunt.registerTask('dev', ['default', 'watch']);

    // Shortcut for running python tests
    grunt.registerTask('pytest', ['shell:pytest']);

    // Plugin tasks
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-handlebars');
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-shell');
    grunt.loadNpmTasks('grunt-newer');
    grunt.loadNpmTasks('grunt-concurrent');
};
