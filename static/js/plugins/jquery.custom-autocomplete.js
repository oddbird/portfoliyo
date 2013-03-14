/**
 * jQuery Custom Autocomplete 0.2.1
 *
 * Copyright (c) 2011-2013, Jonny Gerig Meyer
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
var PYO = (function (PYO, $) {

    'use strict';

    // Add cache to avoid repeated duplicate Ajax calls
    var cache = {};

    $.fn.customAutocomplete = function (opts) {
        var options = $.extend({}, $.fn.customAutocomplete.defaults, opts);
        var keycodes = $.fn.customAutocomplete.keycodes;
        var context = $(this);
        var textbox = context.find(options.textbox);
        var formActions = context.find(options.formActions);
        var suggestionList = context.find(options.suggestionList);
        var inputList = context.find(options.inputList);
        var newInputList = context.find(options.newInputList);
        var origInputs = inputList.html();
        var origNewInputs = newInputList.html();
        var inputs = inputList.add(newInputList).find(options.inputs);
        var newInputTextbox = newInputList.find(options.newInputTextbox);
        var placeholder = textbox.attr('placeholder');
        var prefix = options.prefix;
        var newInputCounter = 1;
        var ajaxCalls = 0;
        var ajaxResponses = 0;
        var newSuggestions, filteredSuggestions, typedText;

        // Removes (faked) placeholder text from textbox
        var removeFakePlaceholder = function () {
            if (textbox.val().indexOf(placeholder) !== -1) {
                textbox.val(null);
            }
            textbox.removeClass('placeholder');
        };

        // Submits form, adds no-inputs note, or shows/hides form-actions when inputs change
        var inputsChanged = function () {
            if (options.autoSubmit) {
                options.triggerSubmit(context);
            }

            if (options.hideFormActions) {
                if (inputList.html() !== origInputs && newInputList.html() !== origNewInputs) {
                    formActions.fadeIn();
                } else {
                    formActions.fadeOut();
                }
            }

            if (options.noInputsNote) {
                var noInputsNote = PYO.tpl('autocomplete_no_inputs', { prefix: prefix });
                inputList.add(newInputList).each(function () {
                    if ($(this).find(options.inputs).length) {
                        $(this).find('.none').remove();
                    } else {
                        if ($(this).children('ul').length) {
                            $(this).children('ul').append(noInputsNote);
                        } else {
                            $(this).append(noInputsNote);
                        }
                    }
                });
            }
        };

        // Filter autocomplete suggestions, returning those that aren't duplicates.
        var filterSuggestions = function () {
            filteredSuggestions = newSuggestions.filter(function () {
                var thisSuggestionID = $(this).find('.option').data('id');
                var thisSuggestionText = $(this).find('.option').data('text');
                var thisSuggestionType = $(this).find('.option').data('type') || options.inputType;

                if (thisSuggestionText && !options.caseSensitive) { thisSuggestionText = thisSuggestionText.toString().toLowerCase(); }
                if ($(this).find('a').hasClass('new')) {
                    // Checked inputs of the same type, with the same text
                    var existingInputs = inputs.filter('[name="' + thisSuggestionType + '"]:checked').filter(function () {
                        return $(this).closest(options.inputWrapper).find(options.inputText).text() === thisSuggestionText;
                    });
                    // Existing non-new suggestions of the same type, with the same text
                    var existingSuggestions = newSuggestions.find('.option').not('.new').filter(function () {
                        if (options.multipleCategories) {
                            return $(this).data('text') === thisSuggestionText && $(this).data('type') === thisSuggestionType;
                        } else {
                            return $(this).data('text') === thisSuggestionText;
                        }
                    });
                    if (existingInputs.length || existingSuggestions.length) {
                        return false;
                    } else {
                        return true;
                    }
                } else {
                    if (inputs.filter('[name="' + thisSuggestionType + '"][value="' + thisSuggestionID + '"]:checked').length) {
                        return false;
                    } else {
                        return true;
                    }
                }
            });
        };

        // Create list of autocomplete suggestions from Ajax response or existing list of inputs
        var updateSuggestions = function (data, cached) {
            var extraDataName, possibilities;
            // Create list of suggestions from local inputs
            if (!data && !options.ajax) {
                var possibileInputs = inputList.find(options.inputs).not(':disabled').closest(options.inputWrapper);
                if (options.caseSensitive) {
                    possibilities = possibileInputs.filter(function () {
                        return $(this).find(options.inputText).text().indexOf(typedText) !== -1;
                    });
                } else {
                    possibilities = possibileInputs.filter(function () {
                        return $(this).find(options.inputText).text().toLowerCase().indexOf(typedText.toLowerCase()) !== -1;
                    });
                }
                data = {};
                data.suggestions = [];
                possibilities.each(function () {
                    var thisSuggestion = {};
                    var typedIndex;
                    if (options.caseSensitive) {
                        typedIndex = $(this).find(options.inputText).text().indexOf(typedText);
                    } else {
                        typedIndex = $(this).find(options.inputText).text().toLowerCase().indexOf(typedText.toLowerCase());
                    }
                    thisSuggestion.typedText = typedText;
                    thisSuggestion.text = $(this).find(options.inputText).text();
                    thisSuggestion.preText = $(this).find(options.inputText).text().substring(0, typedIndex);
                    thisSuggestion.postText = $(this).find(options.inputText).text().substring(typedIndex + typedText.length);
                    thisSuggestion.id = $(this).find(options.inputs).attr('value');
                    if (options.multipleCategories) {
                        thisSuggestion.type = $(this).find(options.inputs).data('type');
                        if ($(this).closest(options.inputList).find('.category-title').length) {
                            thisSuggestion.displayType = $(this).closest(options.inputList).find('.category-title').text();
                        }
                    }
                    data.suggestions.push(thisSuggestion);
                });
            }

            // Create suggestion from new-input types
            if (options.allowNew && !cached && !(options.restrictAllowNew && textbox.data('allow-new') !== true)) {
                newInputList.each(function () {
                    var thisSuggestion = {};
                    thisSuggestion.typedText = typedText;
                    thisSuggestion.text = typedText;
                    thisSuggestion.id = typedText;
                    thisSuggestion.newSuggestion = true;
                    if (options.multipleCategories) {
                        thisSuggestion.type = $(this).data('type');
                        if ($(this).find('.category-title').length) {
                            thisSuggestion.displayType = $(this).find('.category-title').text();
                        }
                    }
                    data.suggestions.unshift(thisSuggestion);
                });
            }

            if (options.extraDataName) {
                extraDataName = options.extraDataName;
                $.each(data.suggestions, function () {
                    if (this[extraDataName]) {
                        this.responseDataName = extraDataName;
                        this.responseDataVal = this[extraDataName];
                    }
                });
            }

            newSuggestions = PYO.tpl('autocomplete_suggestion', data);
            filterSuggestions();
            suggestionList.html(filteredSuggestions);

            // Show suggestion list if it contains suggestions; otherwise, hide it.
            if (suggestionList.find('li').length) {
                suggestionList.show();
            } else {
                suggestionList.hide();
            }

            // Adds ".selected" to first autocomplete suggestion.
            if (!(suggestionList.find('.selected').length)) {
                suggestionList.find('li:first-child .option').addClass('selected');
            }
        };

        // Updates suggestion-list
        var updateSuggestionList = function () {
            if (textbox.val() !== typedText && textbox.val() !== placeholder) {
                var data, serializedData, extraDataName, extraDataVal;
                var extraData = {};
                typedText = textbox.val();
                if (typedText.length && typedText.trim() !== '') {
                    if (options.ajax) {
                        if (options.extraDataName && options.extraDataFn) {
                            extraDataName = options.extraDataName;
                            extraDataVal = options.extraDataFn();
                            extraData[extraDataName] = extraDataVal;
                        }
                        data = $.extend({}, extraData, {text: typedText});
                        serializedData = $.param(data);
                        if (cache[serializedData]) {
                            updateSuggestions(cache[serializedData], true);
                        } else {
                            ajaxCalls = ajaxCalls + 1;
                            $.get(options.url, data, function (response) {
                                ajaxResponses = ajaxResponses + 1;
                                cache[serializedData] = response;
                                updateSuggestions(response, false);
                            });
                        }
                    } else {
                        updateSuggestions();
                    }
                } else {
                    suggestionList.empty().hide();
                }
            }
        };

        var showSuggestionList = function () {
            if (suggestionList.find('li').length) {
                suggestionList.show();
            }
        };

        // Hide suggestion-list on initial page-load
        suggestionList.hide();

        // Optionally hide form-actions on initial page-load
        if (options.hideFormActions) {
            formActions.hide();
        }

        // Optionally add fake placeholder text on initial page-load
        // (this allows textbox to initially have focus and a placeholder)
        if (options.fakePlaceholder) {
            textbox.addClass('placeholder');
        }

        // Set newInputList to inputList if only one category
        if (!options.multipleCategories && options.newInputList === null) {
            newInputList = context.find(options.inputList);
            newInputTextbox = newInputList.find(options.newInputTextbox);
            options.newInputList = options.inputList;
        }

        // Selecting/unselecting an input returns focus to textbox and hides suggestion-list
        inputList.add(newInputList).on('change', options.inputs, function () {
            textbox.focus();
            suggestionList.hide();
            inputsChanged();
        });

        textbox
            .keyup(function () {
                if (options.ajax) {
                    $(this).doTimeout('autocomplete', 200, function () {
                        updateSuggestionList();
                    });
                } else {
                    updateSuggestionList();
                }
            })
            .keydown(function (e) {
                // If textbox has fake placeholder text, removes it on keydown for non-meta keys other than shift, ctrl, alt, caps, or esc.
                if (textbox.hasClass('placeholder') && options.fakePlaceholder) {
                    if (!e.metaKey && e.keyCode !== keycodes.SHIFT && e.keyCode !== keycodes.CTRL && e.keyCode !== keycodes.ALT && e.keyCode !== keycodes.CAPS && e.keyCode !== keycodes.ESC) {
                        removeFakePlaceholder();
                    }
                }
                // Submit form if textbox is empty and form-actions are visible
                if (e.keyCode === keycodes.ENTER && textbox.val() === '' && formActions.is(':visible') && !options.autoSubmit) {
                    e.preventDefault();
                    options.triggerSubmit(context);
                } else {
                    // If the suggestion list is not visible...
                    if (!suggestionList.is(':visible')) {
                        // ...prevent normal TAB function, and show suggestion list
                        if (e.keyCode === keycodes.TAB && textbox.val() !== '') {
                            e.preventDefault();
                            showSuggestionList();
                        }
                        // ...show suggestion list on ENTER
                        if (e.keyCode === keycodes.ENTER) {
                            e.preventDefault();
                            showSuggestionList();
                        }
                        // ...show the suggestion list on arrow-keys
                        if (e.keyCode === keycodes.UP || e.keyCode === keycodes.DOWN || e.keyCode === keycodes.LEFT || e.keyCode === keycodes.RIGHT) {
                            showSuggestionList();
                        }
                    // If the suggestion list is already visible...
                    } else {
                        var thisInputText = suggestionList.find('.selected').data('text');
                        // UP and DOWN move "active" suggestion
                        if (e.keyCode === keycodes.UP) {
                            e.preventDefault();
                            if (!suggestionList.find('.selected').parent().is(':first-child')) {
                                suggestionList.find('.selected').removeClass('selected').parent().prev().children('a').addClass('selected');
                            }
                        }
                        if (e.keyCode === keycodes.DOWN) {
                            e.preventDefault();
                            if (!suggestionList.find('.selected').parent().is(':last-child')) {
                                suggestionList.find('.selected').removeClass('selected').parent().next().children('a').addClass('selected');
                            }
                        }
                        // ENTER selects the "active" suggestion, if exists.
                        if (e.keyCode === keycodes.ENTER) {
                            e.preventDefault();
                            if (suggestionList.find('.selected').length) {
                                $.doTimeout(100, function () {
                                    if (ajaxCalls === ajaxResponses) {
                                        suggestionList.find('.selected').click();
                                        return false;
                                    }
                                    return true;
                                });
                            }
                        }
                        // TAB auto-completes the "active" suggestion if it isn't already completed...
                        if (e.keyCode === keycodes.TAB) {
                            if (thisInputText && textbox.val().toLowerCase() !== thisInputText.toString().toLowerCase()) {
                                e.preventDefault();
                                textbox.val(thisInputText);
                            // ...otherwise, TAB selects the "active" suggestion (if exists)
                            } else if (suggestionList.find('.selected').length) {
                                e.preventDefault();
                                suggestionList.find('.selected').click();
                            }
                        }
                        // RIGHT auto-completes the "active" suggestion if it isn't already completed
                        // and the cursor is at the end of the textbox
                        if (e.keyCode === keycodes.RIGHT) {
                            if (thisInputText && textbox.val().toLowerCase() !== thisInputText.toString().toLowerCase() && textbox.get(0).selectionStart === textbox.val().length) {
                                e.preventDefault();
                                textbox.val(thisInputText);
                            }
                        }
                        // ESC hides the suggestion list
                        if (e.keyCode === keycodes.ESC) {
                            e.preventDefault();
                            suggestionList.hide();
                        }
                    }
                }
            })
            // If textbox still has fake placeholder text, remove it on click
            .click(function () {
                if (textbox.hasClass('placeholder') && options.fakePlaceholder) {
                    removeFakePlaceholder();
                }
            })
            .focus(function () {
                // Resets textbox data-clicked to "false" (becomes "true" when an autocomplete suggestion is clicked)
                textbox.data('clicked', false);
                // Adds fake placeholder on initial page load (and moves cursor to start of textbox)
                if (textbox.val().length === 0 && textbox.hasClass('placeholder') && options.fakePlaceholder) {
                    textbox.val(placeholder);
                    textbox.get(0).setSelectionRange(0, 0);
                }
            })
            // On blur, removes fake placeholder text, and hides the suggestion
            // list after 150 ms if textbox data-clicked is "false"
            .blur(function () {
                function hideList() {
                    if (textbox.data('clicked') !== true) {
                        suggestionList.hide();
                        textbox.data('clicked', false);
                    }
                }
                if (options.fakePlaceholder) {
                    removeFakePlaceholder();
                }
                window.setTimeout(hideList, 150);
            });

        // Optionally give textbox initial focus on page-load
        if (options.initialFocus) {
            textbox.focus();
        }

        suggestionList.on({
            // Adds ".selected" to suggestion on mouseover, removing ".selected" from other suggestions
            mouseover: function () {
                var thisSuggestion = $(this).addClass('selected');
                thisSuggestion.parent('li').siblings('li').find('a').removeClass('selected');
            },
            // Prevent the suggestion list from being hidden (by textbox blur event) when clicking a suggestion
            mousedown: function () {
                textbox.data('clicked', true);
            },
            // Add new input or select existing input when suggestion is clicked
            click: function (e) {
                e.preventDefault();
                var thisGroup, thisTypeName, existingNewInput, index, newInput, thisInput, data;
                var el = $(this);
                var thisID = el.data('id');
                var inputText = el.data('text');
                if (options.multipleCategories) {
                    thisTypeName = el.data('type');
                } else {
                    thisTypeName = options.inputType;
                }
                if (!options.caseSensitive) {
                    inputText = inputText.toString().toLowerCase();
                }
                thisInput = inputs.filter('[value="' + thisID + '"]');
                // If there's an existing non-new input, select it...
                if (thisInput.length) {
                    thisInput.prop('checked', true).change();
                } else {
                    if (options.multipleCategories) {
                        thisGroup = newInputList.filter(function () {
                            return $(this).data('type') === thisTypeName;
                        });
                    } else {
                        thisGroup = newInputList;
                    }
                    if (options.inputsNeverRemoved) {
                        index = thisGroup.find(options.inputs).length + 1;
                    } else {
                        index = newInputCounter++;
                    }
                    if (options.allowNew) {
                        // If we're dealing with a new input...
                        if (el.hasClass('new')) {
                            if (!options.multipleCategories) {
                                thisTypeName = 'new-' + thisTypeName;
                            }
                            data = {
                                typeName: thisTypeName,
                                inputText: inputText,
                                id: inputText,
                                index: index,
                                newInput: true,
                                prefix: prefix
                            };
                            if (el.data(options.extraDataName)) {
                                data.responseDataName = options.extraDataName;
                                data.responseDataVal = el.data(options.extraDataName);
                            }
                            existingNewInput = thisGroup.find(options.inputs + '[value="' + inputText + '"]');
                            // ...select it if it already exists...
                            if (existingNewInput.length && options.inputsNeverRemoved) {
                                existingNewInput.prop('checked', true).change();
                            } else {
                                // ...or add it if it doesn't already exist.
                                newInput = PYO.tpl('autocomplete_input', data);
                                if (thisGroup.children('ul').length) {
                                    thisGroup.removeClass('empty').children('ul').append(newInput);
                                } else {
                                    thisGroup.removeClass('empty').append(newInput);
                                }
                                newInput.find(options.inputs).prop('checked', true).change();
                                inputs = inputList.add(newInputList).find(options.inputs);
                            }
                        } else {
                            // Otherwise, simply add the input.
                            data = {
                                typeName: thisTypeName,
                                inputText: inputText,
                                id: thisID,
                                index: index,
                                prefix: prefix
                            };
                            if (el.data(options.extraDataName)) {
                                data.responseDataName = options.extraDataName;
                                data.responseDataVal = el.data(options.extraDataName);
                            }
                            newInput = PYO.tpl('autocomplete_input', data);
                            if (thisGroup.children('ul').length) {
                                thisGroup.removeClass('empty').children('ul').append(newInput);
                            } else {
                                thisGroup.removeClass('empty').append(newInput);
                            }
                            newInput.find(options.inputs).prop('checked', true).change();
                            inputs = inputList.add(newInputList).find(options.inputs);
                        }
                    }
                }
                // Empty the textbox, and empty and hide the suggestion list
                textbox.val(null);
                typedText = null;
                suggestionList.empty().hide();
            }
        }, '.option');

        // Remove inputs and update suggestion list when unchecked.
        if (!options.inputsNeverRemoved) {
            inputList.add(newInputList).on('click', 'label', function (e) {
                e.preventDefault();
                $(this).closest(options.inputWrapper).remove();
                inputs = inputList.add(newInputList).find(options.inputs);
                if (newSuggestions) {
                    filterSuggestions();
                    suggestionList.hide().html(filteredSuggestions);
                    // Adds ".selected" to first autocomplete suggestion.
                    if (!(suggestionList.find('.selected').length)) {
                        suggestionList.find('li:first-child a').addClass('selected');
                    }
                }
                inputsChanged();
            });
        }

        // Allow adding new inputs via group-specific textbox
        newInputTextbox.each(function () {
            $(this).keydown(function (e) {
                if (e.keyCode === keycodes.ENTER) {
                    e.preventDefault();
                    var thisTextbox = $(this);
                    var thisText = options.caseSensitive ? thisTextbox.val() : thisTextbox.val().toLowerCase();
                    var thisGroup = thisTextbox.closest(options.newInputList);
                    var existingInput = thisGroup.find(options.inputs + '[value="' + thisText + '"]');
                    var typeName = thisGroup.data('type');
                    var index = thisGroup.find(options.inputs).length + 1;
                    var newInput = PYO.tpl('autocomplete_input', {
                        typeName: typeName,
                        inputText: thisText,
                        id: thisText,
                        index: index,
                        newInput: true,
                        prefix: prefix
                    });
                    var addInput = function () {
                        if (thisGroup.children('ul').length) {
                            thisGroup.removeClass('empty').children('ul').append(newInput);
                        } else {
                            thisGroup.removeClass('empty').append(newInput);
                        }
                        newInput.find(options.inputs).prop('checked', true).change();
                        inputs = inputList.add(newInputList).find(options.inputs);
                        thisTextbox.val(null);
                        thisText = null;
                    };
                    var selectInput = function () {
                        existingInput.prop('checked', true).change();
                        thisTextbox.val(null);
                        thisText = null;
                    };
                    // ENTER performs submit action if textbox is empty...
                    if (thisText === '' && formActions.is(':visible') && !options.autoSubmit) {
                        options.triggerSubmit(context);
                    } else if (thisText.length && thisText.trim() !== '') {
                        // ...otherwise, if the input already exists, ENTER selects it...
                        if (existingInput.length) {
                            if (!existingInput.is(':checked')) {
                                selectInput();
                            }
                        } else {
                            addInput();
                        }
                    }
                }
            });
        });
    };

    // Store keycode variables for easier readability
    $.fn.customAutocomplete.keycodes = {
        SPACE: 32,
        ENTER: 13,
        TAB: 9,
        ESC: 27,
        BACKSPACE: 8,
        SHIFT: 16,
        CTRL: 17,
        ALT: 18,
        CAPS: 20,
        LEFT: 37,
        UP: 38,
        RIGHT: 39,
        DOWN: 40
    };

    /* Setup plugin defaults */
    $.fn.customAutocomplete.defaults = {
        textbox: '#autocomplete-textbox',               // Selector for autocomplete textbox
        inputs: 'input[type="checkbox"]',               // Selector for inputs
        inputWrapper: '.token',                         // Selector for wrapper around inputs
        inputText: '.token-text',                       // Selector for input text
        suggestionList: '.suggest',                     // Selector for list of autocomplete suggestions
        inputList: '.visual',                           // Selector for list of inputs
        formActions: '.form-actions',                   // Select for form-actions (only needed if ``hideFormActions: true``)
        ajax: false,                                    // Set ``true`` if using Ajax to retrieve autocomplete suggestions
        url: null,                                      // Ajax url (only needed if ``ajax: true``)
        triggerSubmit: function (context) {             // Function to be executed on ENTER in empty textbox
            context.find('.form-actions button[type="submit"]').click();
        },
        hideFormActions: false,                         // Set ``true`` if form actions should be hidden when inputs are unchanged
        autoSubmit: false,                              // Set ``true`` if form should be submitted on every input change
        multipleCategories: false,                      // Set ``true`` if inputs are separated into categorized groups
        allowNew: false,                                // Set ``true`` if new inputs (neither existing nor returned via Ajax) are allowed
        restrictAllowNew: false,                        // Set ``true`` if new inputs are only allowed if textbox has data-allow-new="true"
        newInputList: null,                             // Selector for list of new inputs (only needed if ``allowNew: true``
                                                        //      and ``multipleCategories: true``)
        newInputTextbox: null,                          // Selector for secondary textbox to enter new group-specific inputs
        fakePlaceholder: false,                         // Set ``true`` to create fake placeholder text when using ``initialFocus: true``
        initialFocus: false,                            // Set ``true`` to give textbox focus on initial page load
        reset: '.reset',                                // Selector for button to reset all inputs to original state
        inputType: null,                                // Name for input types when using only one category of inputs
        inputsNeverRemoved: false,                      // Set ``true`` if non-new inputs are never added or removed (only checked or unchecked)
        caseSensitive: false,                           // Set ``true`` if inputs should be treated as case-sensitive
        prefix: '',                                     // Prefix to apply to each input ID (to avoid ID duplication when using multiple times on one page)
        noInputsNote: false,                            // Set ``true`` to add "none" when no there are no inputs
        extraDataName: null,                            // Additional key to be sent with ajax-request
        extraDataFn: null                               // Function which returns additional value to be sent with ajax-request
    };

    return PYO;

}(PYO || {}, jQuery));