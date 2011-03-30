$(document).ready(function(){
        
        // find all fields
        var fields = [];
        $('ul.navigation a:gt(1)').each(function(index) {
                var text = $(this).text();
                fields[fields.length] = text;
            });

        // modify project div
        $('div.project').each(function(){
                var project = $(this).attr('id'); 
                var url = '/' + project; // TODO: urlquote

                // make description editable with jeditable
                $(this).find('p.description').editable(url, {
                        'type': 'textarea',
                            'rows': 7,
                            'cols': 80,
                            'indicator': '<img src="/img/indicator.gif"/>',
                            'onblur': 'submit',
                            'name': 'description',
                            'tooltip': 'click to edit description'
                            });

                // add an add fields button
                $(this).find('ul.field').append('<button class="add-field" title="add a field">+</button>');
                $(this).find('button.add-field').click(function() {
                        $(this).addClass('hide');
                        var input = $('<input class="add-field" type="text"/>');
                        $(this).before(input);
                        var button = $(this);
                        var ul = $(this).parents("ul.field");
                        var field = ul.attr('class').split(' ')[1];
                        var data = '/tags';
                        $(input).autoSuggest(data, {selectedItemProp: 'value',
                                    selectedValuesProp: 'value', 
                                    searchObjProps: 'value',
                                    minChars: 0,
                                    emptyText: null,
                                    startText: '',
                                    resultsHighlight: false,
                                    extraParams: '&format=json&field=' + field + '&omit=' + project,
                                    preSelectionAdded: function(value) {
                                    var data = {};
                                    data[field] = value;
                                    $.post(url, data, function() {
                                            var elem = $(ul).children('li:last');
                                            var li = $('<li><a href="/?' + field + '=' + value + '">' + value + '</a></li>');
                                            elem.after(li);
                                            addDeleteButton(li);
                                        });
                                    return false;
                                }
                            });
                        $(input).focus();
                    });

                // add a remove fields button

                function addDeleteHandler(button) {
                    $(this).addClass('highlight');
                    var ul = $(this).parents("ul.field");
                    var field = ul.attr('class').split(' ')[1];
                    var value = $(this).next().html();
                    var data = {action: 'delete'}
                    data[field] = value;
                    var that = $(this);
                    $.post(url, data, function() {
                            $(that).parent().remove();
                            var fields = ul.find('li');
                            if (fields.length == 0) {
                                $(ul).remove();
                                // TODO: add back in to 
                                // some field container thingy if its empty
                            }
                        });
                }

                function addDeleteButton(li) {
                    var button = $('<button class="remove-field" title="remove">-</button>');
                    li.prepend(button);
                    button.click(addDeleteHandler)
                }

                // add a remove fields button
                $(this).find('ul.field > li').prepend('<button class="remove-field" title="remove">-</button>');
                $(this).find('button.remove-field').click(function() {
                        $(this).addClass('highlight');
                        var ul = $(this).parents("ul.field");
                        var field = ul.attr('class').split(' ')[1];
                        var value = $(this).next().html();
                        var data = {action: 'delete'}
                        data[field] = value;
                        var that = $(this);
                        $.post(url, data, function() {
                                $(that).parent().remove();
                                var fields = ul.find('li');
                                if (fields.length == 0) {
                                    $(ul).remove();
                                    // TODO: add back in to 
                                    // some field container thingy if its empty
                                }
                            });
                    });

                // add a missing fields container
                var missing_fields = [];
                var found_fields = [];
                $(this).find('ul.field').each(function(index) {
                    var field = $(this).attr('class').split(' ')[1];
                    found_fields[index] = field;
                    });
                for (var i=0; i < fields.length; i++) {
                    var found = false;
                    for (var j=0; j < found_fields.length; j++) {
                        if (found_fields[j] == fields[i]) {
                            found = true;
                            break;
                        }
                    }
                    if (!found) {
                        missing_fields[missing_fields.length] = fields[i];
                    }
                }
                var additional_fields = $('<ul class="additional-fields"></ul>');
                for (var i=0; i < missing_fields.length; i++) {
                    additional_fields.append('<li>+ ' + missing_fields[i] + '</li>');
                }
                $(this).find('ul.field:last').after(additional_fields);
            });

    });
