$(document).ready(function(){
        $('div.project').each(function(){
                var project = $(this).attr('id'); 
                $(this).find('p.description').editable(project, {
                        'type': 'textarea',
                            'rows': 7,
                            'cols': 80,
                            'indicator': '<img src="/img/indicator.gif"/>',
                            'onblur': 'submit',
                            'name': 'description',
                            });
            });
    });
