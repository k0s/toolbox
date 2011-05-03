// javascript for the new tool view

$(document).ready(function(){
    $('input.field-input').each(function(index) {
        var field = $(this).attr('name');
        $(this).tokenInput("/tags?format=json&field=" + field, {
            theme: 'facebook',
            submitOnEnter: false,
            submitOnBlur: false,
            hintText: false,
            onSubmit : function() {
              alert('submitted ):');
            }
        });
    });
    $("input[name=name]").focus();
});
