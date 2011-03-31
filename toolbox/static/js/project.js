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
                var project_div = $(this);
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

                // function to add auto suggest to an input
                function addAutoSuggest(input, field) {
                    // raise NotImplementedError
                    var ul = $(input).parents('ul.field');

                    function postField() {
                        var elem = $(ul).children('li:last');
                        var li = $('<li><a href="/?' + field + '=' + value + '">' + value + '</a></li>');
                        
                        if (elem.length == 0) {
                            var elem = $(ul).children('h2');
                        } 
                        elem.after(li);
                        addDeleteButton(li);
                    }

                    $(input).autoSuggest('/tags', {selectedItemProp: 'value',
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
                                        postField();
                                        // var elem = $(ul).children('li:last');
                                        // var li = $('<li><a href="/?' + field + '=' + value + '">' + value + '</a></li>');

                                        // if (elem.length == 0) {
                                        //     var elem = $(ul).children('h2');
                                        // } 
                                        // elem.after(li);
                                        // addDeleteButton(li);
                                    });
                                return false;
                            }
                        });
                    $(input).keypress(function(event) {
                            if (event.which == 13) {
                                var value = $(this).val();
                                var data = {};
                                data[field] = value;
                                
                                $(this).val('');
                            }
                        });
                    $(input).focus();
                }

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
                        addAutoSuggest(input, field); // could get field instead from introspection
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
                            var fields = ul.children('li');
                            if (fields.length == 0) {
                                $(ul).remove();
                                // add back in to the missing field container 
                                addMissingField(field, additional_fields);
                            }
                        });
                }

                // add a delete button to a field value list item
                function addDeleteButton(li) {
                    var button = $('<button class="remove-field" title="remove">-</button>');
                    li.prepend(button);
                    button.click(addDeleteHandler)
                }

                // add a remove fields button
                $(this).find('ul.field > li').each(function(index){
                        addDeleteButton($(this));
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
                function addMissingField(missing_field, additional_fields) {
                    // add a missing field to the additional fields container

                    var button = $('<button name="' + missing_field + '">+ ' + missing_field + '</button>');
                    var li = $('<li></li>');
                    li.append(button);
                    additional_fields.append(li);
                    button.click(function() {
                            var missing_field = $(this).attr('name');
                            var ul = $('<ul class="field ' + missing_field + '"><h2 class="project-header"><a href="' + missing_field + '">' + missing_field + '</a></h2></ul>');
                            var input = $('<input class="add-field" type="text"/>');
                            ul.append(input);
                            var elem = project_div.find('ul.field:last');
                            if (elem.length == 0) {
                                elem = project_div.children('p.description');
                            }
                            elem.after(ul);
                            addAutoSuggest(input, missing_field);
                            $(this).parent().remove();
                        });
                    
                }
                for (var i=0; i < missing_fields.length; i++) {
                    var missing_field = missing_fields[i];
                    addMissingField(missing_field, additional_fields);
                }
                $(this).find('form.delete').before(additional_fields);
            });

    });
