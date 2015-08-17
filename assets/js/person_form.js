$(document).ready(function(){
     $('.datepicker').datepicker();
     $('#person-form').validate({
            rules:{
                focusInvalid: false,
                focusCleanup: true,
                name: {
                    required: true,
                    minlength: 3,
                    maxlength: 16
                },
                surname: {
                    required: true,
                    minlength: 3,
                    maxlength: 16
                },
                date_of_birth: {
                    required: true,
                    minlength: 3,
                    maxlength: 16,

                },
                email: {
                    required: true,
                    email: true
                },

            },
            submitHandler: function(form) {
                 var $form = $(form);
                 $form.find('.form-control').find('input, textarea').attr('disabled', true);
                 $form.find('button').attr('disabled', true);
                 $form.attr('class', 'hidden');
                 $('#form-loading').html('<img src="/static/274.gif"/>');
                 $.post(
                     $(form).attr('action'),
                     $(form).serialize(),
                     function(data){
                        var json_data = $.parseJSON(data);
                        if (json_data['msg']){
                           $('#form-loading').html('<h3>' + json_data['msg'] + '</h3>');
                        } else{
                            $('#form-loading').html('');
                            $form.attr('class', 'show');
                            $form.find('.form-control').find('input, textarea').attr('disabled', false);
                            $form.find('button').attr('disabled', false);  
                            $.each(json_data, function(i, val) {
                                $("#error_" + i).text(val);
                            });
                        }
                    }
                 )
                 .done(function(){
                    //$('#form-loading').html('');
                    //$form.attr('class', 'show');
                    $form.find('.form-control').find('input, textarea').attr('disabled', false);
                    $form.find('button').attr('disabled', false);
                    $(form).trigger('reset');
                });
              
              return false;
            }
              
      });
      //$('#form-loading').html('<img src="/static/274.gif"/>');
      //$('#person-form').find('button').attr('disabled', false);
 });