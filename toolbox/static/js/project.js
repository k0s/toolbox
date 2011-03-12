$(document).ready(function(){
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
                        $(input).autocomplete({
                                source: ["c++", "java", "php", "coldfusion", "javascript", "asp", "ruby"],
                                    minLength: 0,
                                    delay: 0,
                                    position: {my: "left top", at: "left bottom"},
                                    select: function(event, ui) {
                                    alert('foo');
                                }
                            });
                        $(input).focus();
                        $(input).blur(function(event) {
                                $(button).removeClass('hide');
                                alert(JSON.stringify(event));

                                // TODO: instead of just removing, 
                                // should POST whatever's there, etc
                                $(this).remove();
                            });
                    });

                // add a remove fields button
                $(this).find('ul.field > li').prepend('<button class="remove-field" title="remove">-</button>');
                $(this).find('button.remove-field').click(function() {
                        $(this).addClass('highlight');
                        var ul = $(this).parents("ul.field");
                        var field = ul.attr('class').split(' ')[1];
                        var value = $(this).next().html();
                        data = {action: 'delete'}
                        data[field] = value;
                        var that = $(this);
                        $.post(url, data, function() {
                                $(that).parent().remove();
                                var fields = ul.find('li');
                                if (fields.length == 0) {
                                    $(ul).remove();
                                    // TODO: add back in to 
                                    // some field container thingy
                                }
                            });
                    });
            });
    });
