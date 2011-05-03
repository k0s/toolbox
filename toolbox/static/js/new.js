// javascript for the new tool view

$(document).ready(function(){
    $('input.field-input').each(function(index) {
        var field = $(this).attr('name');
        $(this).tokenInput("/tags?format=json&field=" + field, {
            theme: 'facebook',
            submitOnEnter: false,
            closeOnBlur: true,
            hintText: false,
            onSubmit: function() {
            }
        });
    });
    $("input[name=name]").focus();
});
