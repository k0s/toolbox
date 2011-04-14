$(document).ready(function(){
    $(".date").timeago();
    $(".field-edit").hide();

    $(".edit-message").click(function() {
        var container = $(this).parents('.field-value-container');
        var edit = $(this).parents('.field').children('.field-edit');
        var valueList = container.children('.field-values');

        container.hide();
        edit.show();

        var input = edit.children('input');

        var field = $(this).parents(".field").attr('class').split(' ')[1];

        var items = valueList.children('.field-value-item');
        var values = [];
        for(var i = 0; i < items.length; i++) {
          values.push($(items.get(i)).text().trim());
        }

        var tokenData = values.map(function(value) {
          return {id: value, name: value};
        });

        input.tokenInput("/tags?format=json&field=" + field, {
          theme: 'facebook',
          prePopulate: tokenData,
          autoFocus: true,
          submitOnBlur: true,
          hintText: false,
          onSubmit: function(tokens) {
            edit.hide();
            container.show();
            valueList.empty();

            var values = [];
            for(token in tokens)
              values.push(tokens[token].name);

            if(!values.length) {
              container.children(".field-value").remove();
              container.prepend($('<div class="field-none field-value">none</div>'));
            }
            else {
              values.forEach(function(value) {
                var li = $("<li></li>")
                  .addClass("field-value-item");
                var a = $("<a></a>")
                  .attr("href", "?" + field + "=" + value)
                  .attr("title", "tools with " + field + " " + value)
                  .text(value)
                  .appendTo(li);
                
                if(valueList.length == 0) {
                  container.children(".field-value").remove();
                  valueList = $("<ul class='field-values field-value'></ul>")
                    .prependTo(container);
                }
                valueList.append(li);
              });
            }
            
            var project = container.parents('.project').attr('id');
            var url = '/' + project;
            
            var data = {
              action: 'replace'
            };
            data[field] = values.join(",");
            console.log("values " + JSON.stringify(data));
            
            $.post(url, data, function() {
              console.log("submitted " + field +" for " + project);
            });
          }
        });
    });

    // modify project div
    $('div.project').each(function(){
        var project = $(this).attr('id');
        var url = '/' + project; // TODO: urlquote

        // make description editable with jeditable
        $(this).find('p.description').editable(url, {
          'cols': 80,
          'indicator': '<img src="/img/indicator.gif"/>',
          'onblur': 'submit',
          'name': 'description',
          'tooltip': 'click to edit description'
        });
    });
});
