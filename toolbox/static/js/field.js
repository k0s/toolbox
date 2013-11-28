$(document).ready(function(){

    var fieldname = $('#field-name').text();

    // enable editing of field values
    $('div.field').each(function() {
        var fielddiv = $(this);
        var field = $(this).attr('id');
        $(this).children('h2').each(function() {
             var header = $(this);
             var value = $(this).children('a').text();
             var UEB = $('<img class="UEB" src="img/UEB16.png"/>');
             $(UEB).attr('title', 'rename ' + fieldname + ': ' + field);
             $(UEB).css('visibility', 'hidden');
             var editField = function() {
                var input = $('<input class="text"/>');
                $(input).val(field);
                var submitHandler = function () {
                    var newvalue = $(this).val();
                    if (newvalue != value) {
                        var hiddeninput = $('<input type="hidden"/>');
                        $(hiddeninput).attr('name', value);
                        $(hiddeninput).val(newvalue);
                        var form = $('<form method="POST"></form>');
                        form.append(hiddeninput);
                        $(this).after(form);
                        $(form).submit();
                        $(this).replaceWith('<img class="throbber" src="img/indicator.gif"/>');
                        return;
                    }
                    $(this).blur(function() {});
                    $(this).replaceWith(header);
                    $(header).hover(function(eventObject) { $(this).children('img.UEB').css('visibility', 'visible'); },
                                    function(eventObject) { $(this).children('img.UEB').css('visibility', 'hidden'); });

                    $(header).find('img.UEB').each(function() {
                        $(this).css('visibility', 'hidden');
                        $(this).click(editField);
                    });
                }
                $(header).replaceWith(input);
                $(input).blur(submitHandler);
                $(input).keypress(function(event) {
                    if (event.which == 13) {
                        $(this).blur();
                    }
                });
                $(input).focus();
            }
            $(UEB).click(editField);
             $(this).append(UEB);
             $(this).hover(function(eventObject) { $(this).children('img.UEB').css('visibility', 'visible'); },
                           function(eventObject) { $(this).children('img.UEB').css('visibility', 'hidden'); });

        });
    });
});
