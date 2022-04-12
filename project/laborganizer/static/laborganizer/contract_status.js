function flip_contract_status(ta_id){
    var csrfToken = $( "input[name='csrfmiddlewaretoken']");    
    $.ajax({
	type: 'POST',
	url: 'flip_contract_status',
	data : {
	    'csrfmiddlewaretoken': csrfToken.val(),
	    'ta_id': ta_id,
	},
	success: function (response) {
	    // do nothing
	}
    });
}

