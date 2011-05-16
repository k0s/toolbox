// javascript for the new tool view

$(document).ready(function(){

    var query = parseQueryString();

    // error functions
    function errorMissing() {
        return 'Required';
    }
    function errorReserved() {
        return 'Conflicts with a reserved URL';
    }
    function errorConflict() {
        return 'Project already exists';
        //             return '<a href="%s">%s</a> already exists' % (name, name)
    }
    var queryStringErrors = {'missing': errorMissing,
                             'reserved': errorReserved,
                             'conflict': errorConflict}

    // prepare the form
    var form = $('<form id="new" method="post"></form>');
    var table = $('<table></table>');    
    function addRow(fieldName, rhs) {
        var row = $('<tr id="' + fieldName + '-row"><td class="field-name" for="' + fieldName + '">' + fieldName + '</td><td class="input">' + rhs + '</td></tr>');

        // add errors
        var errors = $('<ul class="error"></ul>');
        for (var key in query) {
            var error = queryStringErrors[key];
            if(error && (jQuery.inArray(fieldName, query[key]) != -1)) {
                errors.append('<li>' + error() + '</li>');
            }
        }
        var cell = $('<td></td>');
        cell.append(errors);
        row.append(cell);

        $(table).append(row)
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
    $(form).submit(function() {
        // submit guard
        var retval = true;
        $('ul.error').empty(); // remove existing errors
        var required = ['name', 'description', 'url']; // required fields
        for (var i in required) { // check required fields
            var row = $(this).find('#' + required[i] + '-row').first();
            var inputCell = $(row).find('td.input').first(); 
            var inputElement = $(inputCell).children().last();
            var value = $(inputElement).val()
            var trimmed = value.trim();
            if (trimmed.length == 0) {
                $(row).find('ul.error').append('<li>' + errorMissing() + '</li');
                retval = false;
            }
        }
        return retval;
    });
    $('#new-container').append(form);


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
