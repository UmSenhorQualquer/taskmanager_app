// Ctor
function Observations() {

	/* Template task_observations.html */

	$("#task_comment" ).keydown(function(e) {
		if(e.ctrlKey && e.keyCode == 13) {
			g_Observations.sendObservation();
		}
	});


	$("#send_obs_btn").click(function(){
		g_Observations.sendObservation();
	});
}


Observations.prototype.loadObservations = function(task_id) {

	$.ajax({
		url: "/observations/browse/"+task_id+"/",
		type: "get",
		success: function(result) {
			
			if(result.status == 'Ok') {
				var html = '';
				
				$(result.data).each(function(i, e) {
					html += '<li><div class="observation-title" >'+e.user+' <small>'+e.date+'</small>';
					html += '<button observation_id='+e.id+' class="delete"><i class="glyphicon glyphicon-trash"></i></button></div>';
					html += '<pre>'+e.msg+'</pre></li>';
				});
				
				$('#task_comment_list').html(html);
				
				// Delete handlers for observations
				$('#task_comment_list button.delete').click(function() {
					var observation_id = $(this).attr('observation_id');
					$.ajax({
						url: "/observations/del/"+observation_id+"/",
						type: "get",
						success: function(result) {
							if(result.status == 'Ok') {
								var task_id = $("#task_comment_list").data('active-task');
								g_Observations.loadObservations(task_id);
							} else Utils.alert("Error: "+result.message);
						}
					});
				});
			} else Utils.alert("Error: "+result.message);
		}
	});
}


Observations.prototype.sendObservation = function() {

	var task_id = $("#task_table tr.selected").attr('task-id');
	
	$.ajax({
		url: "/observations/add/"+task_id+"/",
		type: "post",
		data: { 
			csrfmiddlewaretoken: '{{ csrf_token }}',
			observation: $("#task_comment").text()
		},
		success: function(result) {
			if(result.status == 'Ok') {
				g_Observations.loadObservations(task_id);
				$("#task_comment").val('');
			} else Utils.alert("Error: "+result.message);
		}
	});
}

