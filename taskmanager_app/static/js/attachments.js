function Attachments() {

	/* Template task_details.html */
	$('#fileupload').fileupload({
		formData: [
			{ name: "csrfmiddlewaretoken", value: $('#fileupload input[name="csrfmiddlewaretoken"]').val() },
			{ name: "task_id", value: $('#task_table tr.selected').attr('task-id') }
		],
		autoUpload: true,
		sequentialUploads: true
	});
}


Attachments.prototype.loadAttachments = function(task_id) {
	
	$('.files').html('');
	var csrf = $('#fileupload input[name="csrfmiddlewaretoken"]').val()
	$.ajax({
		url: "/files/browse/"+task_id+"/",
		type: "get",
		success: function(result) {
			if(result.status == 'Ok') {
				$('.files').html('');
				$(result.data).each(function(i, e){
					var html  = '<tr class="template-download fade in">';
						html += '<td>';
						html += '<p class="name">';
						html += '<a data-gallery="" download="'+e.name+'" title="'+e.name+' "href="'+e.url+'">'+e.name+'</a>';
						html += '</p>';
						html += '</td>';
						html += '<td><span class="size">'+e.size+'</span></td>';
						html += '<td>';
						html += '<button data-url="/files/del/'+e.id+'" data-data="{ &quot;csrfmiddlewaretoken&quot; : &quot;'+csrf+'&quot; }" data-type="POST" class="delete"><i class="glyphicon glyphicon-trash"></i></button>';
						html += '</td>';
						html += '</tr>';
					$('.files').append(html);
				});
			} else Utils.alert("Error: "+result.message);
		}
	});
}
