// Ctor
function Details() {

	/* Template task_details.html */
	
	// Initialize all tabs in the Details panel
	$("#tabs").tabs();

}


Details.prototype.hideDetails = function() {
	$("#details_panel #tabs").hide();
	$("#details-info-message").show();
}


Details.prototype.showDetails = function () {
	$("#details-info-message").hide();
	$("#details_panel #tabs").show();
}


Details.prototype.loadTaskDetails = function(task_id) {
	$('#task-name').text( $("#task_table #task_"+task_id+" .column-name input").val() );
	

	this.showDetails();
	g_Reminders.loadReminders(task_id);
	g_Predecessors.loadPredecessors(task_id);
	g_Attachments.loadAttachments(task_id);
	g_Observations.loadObservations(task_id);

	g_Predecessors.dragAndDropPredecessors();
	$("#task_comment_list").data('active-task', task_id)
	
	$('#fileupload').fileupload({
		formData: [
			{ name: "csrfmiddlewaretoken", value: $('#fileupload input[name="csrfmiddlewaretoken"]').val() },
			{ name: "task_id", value: $('#task_table tr.selected').attr('task-id') }
		]
	});
}

