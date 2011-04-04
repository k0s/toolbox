// javascript for the new tool view

$(document).ready(function(){

        // find all fields
        var fields = [];
        $('ul.navigation a.by-field').each(function(index) {
                var text = $(this).text();
                fields[fields.length] = text;
            });

        // enable auto-complete on field inputs
        // TODO
        $('input.field-input').each(function(index) {
                var field = $(this).attr('name');
                $(this).autoSuggest('/tags', {selectedItemProp: 'value',
                            selectedValuesProp: 'value',
                            searchObjProps: 'value',
                            minChars: 0,
                            emptyText: null,
                            startText: '',
                            resultsHighlight: false,
                            extraParams: '&format=json&field=' + field});
            });
    });