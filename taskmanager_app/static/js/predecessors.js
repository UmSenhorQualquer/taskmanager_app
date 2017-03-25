var __dbg = null;

// Ctor
function Predecessors() {


}

Predecessors.prototype.displayPredecessors = function (result) {

	$("#details_panel #predecessors-list").html('<tr><td colspan="3" class="placeholder">Drop the predecessors tasks here.</td></tr>');

	if($("#task_panel #task_table TR.selected").length && result.status.toLowerCase() == "ok" && result.data.length) {

		var task_id = $("#task_panel #task_table TR.selected")[0].id.split("_").slice(-1)[0];

		var html = '';
		$.each(result.data, function(pos, item) {
			html +=  "<tr id='pred_"+ task_id +"_"+ item.task_id +"'>";
			html += "<td>"+ item.task_name +"</td>";
			html += "<td class='datetime'>"+ item.task_start_date +"</td>";
			html += '<td class="delete"><button class="delete" predecessors-id="'+ item.task_id +'" task-id="'+ task_id +'" ><i class="glyphicon glyphicon-trash"></i></button></td>';
			html += "</tr>";
		});
		html += '<tr><td colspan="3" class="placeholder">Drop the predecessors tasks here.</td></tr>';
		$("#details_panel #predecessors-list").html(html);

		// Define the handler for delete
		$("#details_panel #predecessors-list button.delete").click(function() {
			var task_id = $(this).attr('task-id');
			var predecessor_id = $(this).attr('predecessors-id');

			// Send AJAX request info to database
			$.ajax({ 
				url: "predecessors/del/"+ task_id +"/"+ predecessor_id +"/", 
				type: "GET", 
				success: function(result) { g_Predecessors.loadPredecessors(task_id); }
			});
		});
	}
}

Predecessors.prototype.loadPredecessors = function(task_id) {

	// Make sure there is a selected task
	if($("#task_panel #task_table TR.selected").length) {
		
		// Send AJAX request to collect all Predecessors of selected task
		var dataValues = {
			task_id: task_id
		};
		$.ajax({
			url: "predecessors/browse/", 
			type: "POST", 
			data: dataValues, 
			success: g_Predecessors.displayPredecessors });
	}
}

/*
Predecessors.prototype.dropPredecessor = function(result) {
	if(result.status == 'Ok') {
		g_Predecessors.loadPredecessors(result.data.task_id);
	} else Utils.alert("Error: "+result.message);
}
*/

// Former setDragAndDropTaskHandlers
Predecessors.prototype.dragAndDropPredecessors = function() {

	// Define draggables
	$("#task_panel #task_table TR.task TD.column-handler").draggable({
		appendTo: "body",
		helper: "clone"
	});

	// Define droppables
	$("#details_panel #details_panel_predecessors").droppable({
		accept: "#task_panel #task_table TR.task TD.column-handler",
		drop: function( event, ui ) {

			var task_id = $("#task_panel #task_table TR.selected")[0].id.split("_").slice(-1)[0];
			var predecessor_id = ui.draggable.parent().attr("id").split("_").slice(-1)[0];

			// Update handlers to delete a predecessor

			// Send AJAX request to update task predecessors on if there is a selected task
			if($("#task_panel #task_table TR.selected").length) {
				$.ajax({ 
					url: "predecessors/add/"+ task_id +"/"+ predecessor_id +"/", 
					type: "GET", 
					success: function(result) {
						if(result.status == 'Ok') {
							g_Predecessors.loadPredecessors(result.data.task_id);
						} else Utils.alert("Error: "+result.message);
					} 
				});
			}
		}
	});
}