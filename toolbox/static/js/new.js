// javascript for the new tool view

$(document).ready(function(){

    // prepare the form
    var form = $('<form id="new" method="post"></form>');
    var table = $('<table></table>');

    function addRow(fieldName, rhs) {
        $(table).append('<tr><td class="field-name" for="' + fieldName + '">' + fieldName + '</td><td>' + rhs + '</td></tr>')
    }
    function addTextInput(fieldName, isFieldInput) {
        var input = '';
        if (isFieldInput) {
            input = '<input type="text" class="field-input" name="' + fieldName + '"/>';
        } else {
            input = '<input type="text" name="' + fieldName + '"/>';
        }
        addRow(fieldName, input);
    }

    // insert mandatory data: name, description, url
    addTextInput('name', false);
    addRow('description', '<textarea name="description"></textarea>');
    addTextInput('url', false);

    // find other fields
    var fields = [];
    $('.by-field').each(function() {
        fields.push($(this).text());
    });
    for (var i in fields) {
        addTextInput(fields[i], true);
    }

    // add the form to the DOM
    $(form).append(table);
    $(form).append('<input id="submit-new-tool" class="submit button" type="submit" value="Add it!"/>');
    $('#new-container').append(form);
    // TODO: add submit guards

    // add autocomplete
    $('input.field-input').each(function(index) {
        var field = $(this).attr('name');
        $(this).tokenInput("tags?format=json&field=" + field, {
            theme: 'facebook',
            submitOnEnter: false,
            closeOnBlur: true,
            hintText: false
        });
    });

    // focus the first field: name
    $("input[name=name]").focus();
});
