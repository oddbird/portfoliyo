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
        var selectAll = context.find(options.selectAll);
        var selectNone = context.find(options.selectNone);
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

            // Refresh suggestions when an input changes
            if (newSuggestions) {
                filterSuggestions();
                suggestionList.hide().html(filteredSuggestions);
                // Adds ".selected" to first autocomplete suggestion.
                if (!(suggestionList.find('.selected').length)) {
                    suggestionList.find('li:first-child .option').addClass('selected');
                }
            }
        };

        // Filter autocomplete suggestions, returning those that aren't duplicates.
        var filterSuggestions = function () {
            filteredSuggestions = newSuggestions.filter(function () {
                var thisSuggestionID = $(this).find('.option').data('id');
                var thisSuggestionText = $(this).find('.option').data('text').toString();
                var thisSuggestionType = $(this).find('.option').data('type') || options.inputType;
                var existingInputs;

                if (thisSuggestionText && !options.caseSensitive) { thisSuggestionText = thisSuggestionText.toLowerCase(); }
                if ($(this).find('.option').hasClass('new')) {
                    // Checked inputs of the same type, with the same text
                    existingInputs = inputs.filter('[name="' + prefix + '-' + thisSuggestionType + '"]:checked').filter(function () {
                        return $(this).closest(options.inputWrapper).find(options.inputText).text() === thisSuggestionText;
                    });
                    // Existing non-new suggestions of the same type, with the same text
                    var existingSuggestions = newSuggestions.find('.option').not('.new').filter(function () {
                        var thisText = $(this).data('text').toString();
                        if (!options.caseSensitive) { thisText = thisText.toLowerCase(); }
                        if (options.multipleCategories) {
                            return thisText === thisSuggestionText && $(this).data('type') === thisSuggestionType;
                        } else {
                            return thisText === thisSuggestionText;
                        }
                    });
                    if (existingInputs.length || existingSuggestions.length) {
                        return false;
                    } else {
                        return true;
                    }
                } else {
                    existingInputs = inputs.filter('[value="' + thisSuggestionID + '"]:checked').filter(function () {
                        return $(this).attr('name') === prefix + '-new-' + thisSuggestionType || $(this).attr('name') === prefix + '-' + thisSuggestionType;
                    });
                    if (existingInputs.length) {
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
                // If cursor is at the beginning of the textbox, LEFT BACKSPACE RIGHT function to highlight existing tokens
                if ((e.keyCode === keycodes.LEFT || e.keyCode === keycodes.BACKSPACE || e.keyCode === keycodes.RIGHT) && textbox.get(0).selectionStart === 0) {
                    var wrappers = inputs.filter(':checked').closest(options.inputWrapper);
                    // If a token is already selected...
                    if (wrappers.filter('.selected').length) {
                        var selected = wrappers.filter('.selected').first();
                        var index = wrappers.index(selected);
                        // Move the selected one LEFT
                        if (e.keyCode === keycodes.LEFT) {
                            if (!selected.is(wrappers.first())) {
                                wrappers.removeClass('selected');
                                wrappers.eq(index - 1).addClass('selected');
                            }
                        }
                        // Move the selected one RIGHT
                        if (e.keyCode === keycodes.RIGHT) {
                            wrappers.removeClass('selected');
                            if (!selected.is(wrappers.last())) {
                                wrappers.eq(index + 1).addClass('selected');
                            }
                        }
                        // Uncheck the selected input on BACKSPACE
                        if (e.keyCode === keycodes.BACKSPACE) {
                            wrappers.removeClass('selected');
                            selected.find(options.inputs).prop('checked', false).change();
                        }
                        e.preventDefault();
                        suggestionList.hide();
                        return;
                    // LEFT or BACKSPACE highlight the last input if cursor is at the beginning of the textbox
                    } else if (e.keyCode === keycodes.LEFT || e.keyCode === keycodes.BACKSPACE) {
                        inputs.filter(':checked').last().closest(options.inputWrapper).addClass('selected');
                        suggestionList.hide();
                        return;
                    }
                } else { inputs.closest(options.inputWrapper).removeClass('selected'); }
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
                        var thisSuggestion = suggestionList.find('.selected');
                        var thisInputText = thisSuggestion.data('text').toString();
                        var newSelected;
                        // UP and DOWN move "active" suggestion
                        if (e.keyCode === keycodes.UP) {
                            e.preventDefault();
                            if (!thisSuggestion.parent().is(':first-child')) {
                                thisSuggestion.removeClass('selected');
                                newSelected = thisSuggestion.parent().prev().children('.option').addClass('selected');
                                if (newSelected.length && newSelected.position().top < 0) {
                                    suggestionList.scrollTop(suggestionList.scrollTop() + newSelected.position().top);
                                }
                            }
                        }
                        if (e.keyCode === keycodes.DOWN) {
                            e.preventDefault();
                            if (!thisSuggestion.parent().is(':last-child')) {
                                thisSuggestion.removeClass('selected');
                                newSelected = thisSuggestion.parent().next().children('.option').addClass('selected');
                                if (newSelected.length) {
                                    var elPosition = newSelected.position().top;
                                    var elHeight = newSelected.outerHeight();
                                    var contScrolltop = suggestionList.scrollTop();
                                    var contHeight = suggestionList.outerHeight();
                                    if (elPosition + elHeight > contHeight) {
                                        suggestionList.scrollTop(elPosition + contScrolltop + elHeight - contHeight);
                                    }
                                }
                            }
                        }
                        // ENTER selects the "active" suggestion, if exists.
                        if (e.keyCode === keycodes.ENTER) {
                            e.preventDefault();
                            if (thisSuggestion.length) {
                                $.doTimeout(100, function () {
                                    if (ajaxCalls === ajaxResponses) {
                                        thisSuggestion.click();
                                        return false;
                                    }
                                    return true;
                                });
                            }
                        }
                        // TAB auto-completes the "active" suggestion if it isn't already completed...
                        if (e.keyCode === keycodes.TAB) {
                            if (thisInputText && textbox.val().toLowerCase() !== thisInputText.toLowerCase()) {
                                e.preventDefault();
                                textbox.val(thisInputText);
                            // ...otherwise, TAB selects the "active" suggestion (if exists)
                            } else if (thisSuggestion.length) {
                                e.preventDefault();
                                thisSuggestion.click();
                            }
                        }
                        // RIGHT auto-completes the "active" suggestion if it isn't already completed
                        // and the cursor is at the end of the textbox
                        if (e.keyCode === keycodes.RIGHT) {
                            if (thisInputText && textbox.val().toLowerCase() !== thisInputText.toLowerCase() && textbox.get(0).selectionStart === textbox.val().length) {
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
                context.find(options.inputWrapper).filter('.selected').removeClass('selected');
            });

        // Optionally give textbox initial focus on page-load
        if (options.initialFocus) {
            textbox.focus();
        }

        suggestionList.on({
            // Adds ".selected" to suggestion on mouseover, removing ".selected" from other suggestions
            mouseover: function () {
                var thisSuggestion = $(this).addClass('selected');
                thisSuggestion.parent('li').siblings('li').find('.option').removeClass('selected');
            },
            // Prevent the suggestion list from being hidden (by textbox blur event) when clicking a suggestion
            mousedown: function () {
                textbox.data('clicked', true);
            },
            // Add new input or select existing input when suggestion is clicked
            click: function (e) {
                e.preventDefault();
                var thisGroup, thisTypeName, existingNewInput, index, newInput, data;
                var el = $(this);
                var thisID = el.data('id');
                var thisInput = inputs.filter('[value="' + thisID + '"]');
                var inputText = el.data('text').toString();
                var addInput = function () {
                    newInput = PYO.tpl('autocomplete_input', data);
                    if (thisGroup.children('ul').length) {
                        thisGroup.removeClass('empty').children('ul').append(newInput);
                    } else {
                        thisGroup.removeClass('empty').append(newInput);
                    }
                    newInput.find(options.inputs).prop('checked', true).change();
                    inputs = inputList.add(newInputList).find(options.inputs);
                };
                if (options.multipleCategories) {
                    thisTypeName = el.data('type');
                } else {
                    thisTypeName = options.inputType;
                }
                if (!options.caseSensitive) {
                    inputText = inputText.toLowerCase();
                }
                data = {
                    typeName: thisTypeName,
                    inputText: inputText,
                    id: thisID,
                    prefix: prefix,
                    labelText: options.labelText
                };
                if (el.data(options.extraDataName)) {
                    data.responseDataName = options.extraDataName;
                    data.responseDataVal = el.data(options.extraDataName);
                }
                // If there's an existing non-new input, select it
                if (thisInput.length) {
                    thisInput.prop('checked', true).change();
                // Otherwise, if we're allowed to add new inputs...
                } else if (options.allowNew) {
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
                    data.index = index;
                    // If we're dealing with a new input...
                    if (el.hasClass('new')) {
                        existingNewInput = thisGroup.find(options.inputs + '[value="' + inputText + '"]');
                        // ...select it if it already exists...
                        if (existingNewInput.length && options.inputsNeverRemoved) {
                            existingNewInput.prop('checked', true).change();
                        } else {
                            // ...or add it if it doesn't already exist.
                            if (!options.multipleCategories) {
                                thisTypeName = 'new-' + thisTypeName;
                            }
                            data.typeName = thisTypeName;
                            data.newInput = true;
                            addInput();
                        }
                    } else {
                        // Otherwise, simply add the input.
                        addInput();
                    }
                }
                // Empty the textbox, and empty and hide the suggestion list
                textbox.val(null);
                typedText = null;
                suggestionList.empty().hide();
            }
        }, '.option');

        // Remove inputs and update suggestion list when unchecked.
        inputList.add(newInputList).on('change', options.inputs, function () {
            if (!options.inputsNeverRemoved || $(this).hasClass('new')) {
                if ($(this).prop('checked') === false) {
                    $(this).closest(options.inputWrapper).remove();
                    inputs = inputList.add(newInputList).find(options.inputs);
                    inputsChanged();
                }
            }
        });

        selectAll.click(function (e) {
            e.preventDefault();
            $(this).blur();
            inputs.each(function () {
                $(this).prop('checked', true).change();
            });
        });

        selectNone.click(function (e) {
            e.preventDefault();
            $(this).blur();
            inputs.each(function () {
                $(this).prop('checked', false).change();
            });
        });

        context.on('click', options.inputWrapper, function (e) {
            if (!$(e.target).is('label')) {
                var el = $(this);
                el.addClass('selected');
                el.siblings(options.inputWrapper).removeClass('selected');
            }
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
        fakePlaceholder: false,                         // Set ``true`` to create fake placeholder text when using ``initialFocus: true``
        initialFocus: false,                            // Set ``true`` to give textbox focus on initial page load
        reset: '.reset',                                // Selector for button to reset all inputs to original state
        inputType: null,                                // Name for input types when using only one category of inputs
        inputsNeverRemoved: false,                      // Set ``true`` if non-new inputs are never added or removed (only checked or unchecked)
        caseSensitive: false,                           // Set ``true`` if inputs should be treated as case-sensitive
        prefix: '',                                     // Prefix to apply to each input ID (to avoid ID duplication when using multiple times on one page)
        noInputsNote: false,                            // Set ``true`` to add "none" when no there are no inputs
        extraDataName: null,                            // Additional key to be sent with ajax-request
        extraDataFn: null,                              // Function which returns additional value to be sent with ajax-request
        selectAll: null,                                // Selector for select-all button
        selectNone: null,                               // Selector for select-none button
        labelText: null                                 // Text to insert in new-input labels (only needed if ``allowNew: true``)
    };

    return PYO;

}(PYO || {}, jQuery));