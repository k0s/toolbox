$(document).ready(function(){
    $(".date").timeago();
    $(".field-edit").hide();
    
    $(".description").autolink();

    // modify project div
    $('div.project').each(function(){
        var project = $(this).attr('id');
        var url = escape(project).replace(/\//g, '%25%32%66'); // urlquote

        // add a delete link
        var deletelink = $('<a class="delete" title="permanantly remove">Delete</a>');
        $(deletelink).click(function() {
                if(confirm("Permanently remove: " + project + " ?")) {
                    var form = $('<form class="delete" action="delete" method="POST"></form>')
                    var input = $('<input type="hidden" name="project"/>');
                    input.val(project);
                    form.append(input);
                    $(this).after(form);
                    $(form).submit();
                }
            });
        $(this).append(deletelink);

        // make description editable with jeditable
        $(this).find('p.description').editable(url, {
          type: 'textarea',
          rows: 7,
          cols: 80,
          indicator: '<img src="img/indicator.gif"/>',
          onblur: 'submit',
          name: 'description',
          tooltip: 'click to edit description',
          beforeedit: function (settings, jedit, event) {
              if(event.target.nodeName == "A")
                  return false; 
          }
        });

        // make the name and url editable
        var UEB = '<img class="UEB" src="img/UEB16.png" alt="click to edit" title="click to edit"/>'; // universal edit button
        function nameHover(eventObject) {
           var header = this;
           var img = $(this).find('img.UEB');
           $(img).css('visibility', 'visible');
           $(img).click(function() {
               var link = $(header).children('a');
               var text = $(link).html();
               var size = text.length;
               var form = $('<form method="POST" action="' + url + '"><input type="text" name="name" value="' + text +'" size="' + size + '"/><button class="cancel">Cancel</button><input type="submit" value="Rename"/></form>');
               $(form).submit(function() {
                   var input = $(this).find('input[name="name"]')
                   var name = $(input).val()
                   name = name.trim();
                   if (name.length == 0) {
                       $(this).append('<div class="error">A project must have a name</span>');
                       return false;
                   }
                   return true;
               })
               $(form).css('display', 'block');
               $(header).replaceWith(form);
               $(form).find('button.cancel').click(function(){
                   $(header).find('img.UEB').css('visibility', 'hidden');
                   $(header).hover(nameHover,
                                   function(eventObject) { $(this).children('img.UEB').css('visibility', 'hidden'); });
                   $(form).replaceWith(header);
                   });
               $(form).find('input[type=text]').keypress(function(event) {
                       if (event.which == 13) {
                           $(form).submit();
                       }
                   });
               $(form).find('input[type=text]').focus();
               });
        }
        var header = $(this).find('h1');
        $(header).append(UEB);
        $(header).find('img.UEB').each(function() {$(this).css('visibility', 'hidden'); });
        $(header).hover(nameHover,
                        function(eventObject) { $(this).children('img.UEB').css('visibility', 'hidden'); });
        $(this).find('a.home').each(function() {
                var home = this;
                $(this).wrap('<span/>');
                var wrapper = $(this).parent();
                var img = $(UEB);
                $(wrapper).append(img);
                img.css('visibility', 'hidden');
                function urlHover(eventObject) {
                    var img = $(this).find('img.UEB');
                    $(img).css('visibility', 'visible');
                    $(img).click(function() {
                        var link = $(home).attr('href');
                        var size = link.length;
                        var input = $('<input type="text" value="' + link + '" size="' + size + '"/>');
                        $(wrapper).replaceWith(input);
                        
                        function urlEditBlur() {
                            var newlink = $(this).val();
                            var that = this;
                            newlink = newlink.trim();
                            if (newlink != link) {
                                var throbber = $('<img class="throbber" src="img/indicator.gif"/>');
                                $(this).after(throbber);
                                $(this).hide();
                                $.post(url, {"url": newlink}, function(data) {
                                    $(throbber).remove();
                                    var a = $(wrapper).children('a');
                                    a.attr('href', newlink);
                                    a.html(newlink);
                                    $(wrapper).children('img.UEB').css('visibility', 'hidden');
                                    wrapper.hover(urlHover, function(eventObject) { $(this).children('img.UEB').css('visibility', 'hidden'); });
                                    $(that).replaceWith(wrapper);
                                    });
                            }
                            else {
                                $(wrapper).children('img.UEB').css('visibility', 'hidden');
                                wrapper.hover(urlHover, function(eventObject) { $(this).children('img.UEB').css('visibility', 'hidden'); });
                                $(this).replaceWith(wrapper);
                            }
                        }
                        $(input).blur(urlEditBlur);
                        $(input).keypress(function(event) {
                                if (event.which == 13) {
                                    $(this).blur();
                                }
                            });
                        $(input).focus();
                        });
                }
                wrapper.hover(urlHover, function(eventObject) { $(this).children('img.UEB').css('visibility', 'hidden'); });
            });

        // autocomplete
        $(this).find(".edit-message").click(function() {
          var container = $(this).parents('.field-value-container');
          var edit = $(this).parents('.field').children('.field-edit');
          var valueList = container.children('.field-values');

          container.hide();
          edit.show();

          var items = valueList.children('.field-value-item');
          var values = [];
          for(var i = 0; i < items.length; i++) {
              values.push($(items.get(i)).text().trim());
          }

          var tokenData = values.map(function(value) {
                  return {id: value, name: escape(value)};
              });
        
          var input = edit.children('input');
          var field = $(this).parents(".field").attr('class').split(' ')[1];

          input.tokenInput("tags?format=json&field=" + field + "&omit=" + project, {
              theme: 'facebook',
              prePopulate: tokenData,
              autoFocus: true,
              submitOnBlur: true,
              canBlur: function(elem) {
                  return !container.find($(elem)).length;
                  },
              hintText: false,
              onSubmit: function(values) {
                  edit.hide();
                  container.show();
                  valueList.empty();

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
            
                  
                  var data = {
                      action: 'replace'
                  };
                  data[field] = values.join(",");
                  
                  $.post(url, data, function() {
                      });
                  }
              });
            });
        });
    });
