
$(function(){ 
	
    $('.king-step').click(function(){
    	var next_id=$(this).attr('data-next-id'); 
    	var this_id=$(this).attr('data-this-id');
    	if(next_id > this_id){
            var validate_info=$(this).data('validate_info');
            $(this_id).validate(generate_validate(validate_info))
            if($(this_id).valid()){
                $("div[data="+next_id.replace("#", "")+"]").removeClass('process-did');
                $("div[data="+next_id.replace("#", "")+"]").addClass('process-done');
                $('.king-form-step').addClass('king-display-none'); 
                $(next_id).removeClass('king-display-none');
            }
        }
    	if(next_id < this_id){
	    	$("div[data="+this_id.replace("#", "")+"]").removeClass('process-done');
	    	$("div[data="+this_id.replace("#", "")+"]").addClass('process-did');
	    	$('.king-form-step').addClass('king-display-none'); 
    		$(next_id).removeClass('king-display-none');
        }
    });

    function generate_validate(validate_info){
        console.debug(validate_info)
        validate = {
            errorElement: 'span',
            rules: {},
            messages: {}
        }
        if(validate_info){
            $.each(validate_info, function(key, value){
                validate['rules'][key] = {required: true}
                validate['messages'][key] = value
            });
        }
        return validate
    }
});
