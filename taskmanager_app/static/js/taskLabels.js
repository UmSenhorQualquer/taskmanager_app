// Ctor
function TaskLabels() {

}

TaskLabels.prototype.setAddTaskLabel = function(rowSelector) {
	var selector = ".labels-container";
	if( rowSelector ) selector = rowSelector+" "+selector;

	$( selector ).droppable({
		accept: ".labels-list .color",
		drop: function( event, ui ) {
			var task_id = $(this).parent().parent().attr('task-id');
			var label_id = ui.draggable.attr('label-id');
			var container = this;

			$.ajax({
				url: "/labels/task/add/"+task_id, 
				type: "get",
				data: { label_id: label_id }, 
				success: function(result){
					if(result.status=='Ok') {
						var clone = ui.draggable.clone()
						clone.appendTo(container);
						g_TaskLabels.setDeleteTaskLabel(clone);
					} else Utils.alert("Error: "+result.message);
				}
			});
		}
	});
}


TaskLabels.prototype.setDeleteTaskLabel = function(rowSelector) {
	var jqobject;

	var selector = ".labels-container .color";
	if( rowSelector ){ 
		if( typeof rowSelector == 'string'){
			selector = rowSelector+" "+selector;
			jqobject = $( selector );
		}
		else
			jqobject = rowSelector;
	}
	else
		jqobject = $( selector );
	
	jqobject.draggable({ 
		revert: true,
		drag: function( event, ui ){
			var task_id = $(this).parent().parent().parent().attr('task-id');
			var label_id = $(this).attr('label-id');
			if( ui.position.left>50 && task_id){
				$.ajax({
					url: "/labels/task/del/"+task_id, 
					type: "get",
					data: { label_id: label_id }, 
					success: function(result){
						if(result.status=='Ok') {
							ui.helper.remove();
						} else Utils.alert("Error: "+result.message);
					}
				});
			}
		}
	});
}
