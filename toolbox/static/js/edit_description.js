$(document).ready(function(){
        $('div.project').each(function(){
                var project = $(this).attr('id'); 

                // make description editable with jeditable
                $(this).find('p.description').editable(project, {
                        'type': 'textarea',
                            'rows': 7,
                            'cols': 80,
                            'indicator': '<img src="/img/indicator.gif"/>',
                            'onblur': 'submit',
                            'name': 'description',
                            });

                // add an add fields button
                $(this).find('ul.field').append('<button class="add-field">+</button>');

                // add a remove fields button
                $(this).find('ul.field > li').prepend('<button class="remove-field">-</button>');
            });
    });
