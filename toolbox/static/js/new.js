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
        var tool = query['conflict'][0];
        tool = $('<div></div>').text(tool).html();
        return '<a href="' + escape(tool) + '">' + tool + '</a> already exists';
    }
    var queryStringErrors = {'missing': errorMissing,
                             'reserved': errorReserved,
                             'conflict': errorConflict}

    // prepare the form
    var form = $('<form id="new" method="post"></form>');
    var table = $('<table></table>');    
    function addRow(fieldName, rhs) {
        var row = $('<tr id="' + fieldName + '-row"><td class="field-name" for="' + fieldName + '">' + fieldName + '</td><td class="input"></td></tr>');
        $(row).find('td.input').append(rhs);

        // add errors
        var errors = $('<ul class="error"></ul>');
        for (var key in query) {
            var error = queryStringErrors[key];
            if(error) {
                if (jQuery.inArray(fieldName, query[key]) != -1) {
                    errors.append('<li>' + error() + '</li>');
                }
                // name-specific errors
                if ((key != 'missing') && (fieldName == 'name')) {
                    errors.append('<li>' + error() + '</li>');
                }
            }
        }
        var cell = $('<td></td>');
        cell.append(errors);
        row.append(cell);

        $(table).append(row)
    }
    function addTextInput(fieldName, isFieldInput) {
        var value = null;
        if (query) { 
            value = query[fieldName];
        }
        var input = $('<input type="text"/>');
        $(input).attr('name', fieldName);
        if (isFieldInput) {
            if (value) {
                value = value.join(", "); 
                // XXX for some reason, this doesnt get reflected in the observed input;
                // an oversight with the token parser/autocomplete? ::shrug::
            }
            $(input).addClass('field-input');
        } else {
            if (value) {
                value = value[0];
            }
        }
        if (value) {
            $(input).val(value);
        }
        addRow(fieldName, input);
        return input;
    }

    // insert mandatory data: name, description, url
    var nameInput = addTextInput('name', false);
    var description = '';
    if (query && query['description']) {
        description = query['description'][0];
    }
    addRow('description', $('<textarea name="description">' + description + '</textarea>'));
    var urlInput = addTextInput('url', false);
    var urlValue = urlInput.val();
    if (urlValue && !query['name']) {
        if (urlValue.charAt(urlValue.length -1) == '/') {
            urlValue = urlValue.slice(0, urlValue.length -1);
        }
        var index = urlValue.lastIndexOf('/');
        if (index != -1) {
            var name = urlValue.slice(index+1);
            $(nameInput).val(name);
        }
    }

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
    var now = new Date().getTime() / 1000; // seconds
    $(form).append('<input type="hidden" name="form-render-date" value="' + now + '"/>');
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
                $(row).find('ul.error').append('<li>' + errorMissing() + '</li>');
                retval = false;
            }
            // no slashes in name
            if (required[i] == 'name' && value.indexOf('/') != -1) {
                    $(row).find('ul.error').append('<li>slashes are not allowed in names</li>');
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
